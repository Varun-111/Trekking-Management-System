from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
from models import db, User, Trek, Booking, TrekStaff
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trekking.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'trekking_secret_key'

db.init_app(app)

# ─── Home ────────────────────────────────────────────
@app.route('/')
def home():
    return render_template('index.html')

# ─── Login ───────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            if user.is_blacklisted:
                flash('Your account has been blacklisted. Contact admin.', 'danger')
                return redirect(url_for('login'))

            if not user.is_approved:
                flash('Your account is pending admin approval. Please wait.', 'warning')
                return redirect(url_for('login'))

            # Save user info in session
            session['user_id'] = user.id
            session['user_name'] = user.username
            session['role'] = user.role

            # Redirect based on role
            if user.role == 'Admin':
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'Trek Staff':
                return redirect(url_for('staff_dashboard'))
            else:
                return redirect(url_for('trekker_dashboard'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html')

# ─── Register ────────────────────────────────────────
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        role = request.form['role']

        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Please login.', 'danger')
            return redirect(url_for('register'))

        # Trekkers are approved immediately
        # Trek Staff need admin approval first
        if role == 'Trekker':
            approved = True
        else:
            approved = False

        new_user = User(
            username=username,
            email=email,
            phone=phone,
            password_hash=generate_password_hash(password),
            role=role,  
            is_approved=approved
        )

        db.session.add(new_user)
        db.session.commit()

        if role == 'Trek Staff':
            flash('Registration submitted! Wait for admin approval before logging in.', 'success')
        else:
            flash('Account created successfully! Please login.', 'success')

        return redirect(url_for('login'))

    return render_template('register.html')


# ─── Admin: View and Approve Pending Staff ────────────
@app.route('/admin/pending-staff')
def pending_staff():
    if session.get('role') != 'Admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))

    # Fetch all staff accounts that are not yet approved
    pending = User.query.filter_by(role='Trek Staff', is_approved=False).all()

    return render_template('pending_staff.html', pending=pending)


@app.route('/admin/approve-staff/<int:user_id>')
def approve_staff(user_id):
    if session.get('role') != 'Admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))

    # Find the staff user by ID and approve them
    staff_user = User.query.get(user_id)

    if staff_user and staff_user.role == 'Trek Staff':
        staff_user.is_approved = True
        db.session.commit()
        flash(f'{staff_user.username} has been approved successfully.', 'success')
    else:
        flash('User not found.', 'danger')

    return redirect(url_for('pending_staff'))


# ─── Logout ──────────────────────────────────────────
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

# ─── Dashboards (placeholder for now) ────────────────
@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'Admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))
    
    # Count stats for the dashboard cards
    total_treks = Trek.query.count()
    total_users = User.query.filter_by(role='Trekker').count()
    total_staff = User.query.filter_by(role='Trek Staff', is_approved=True).count()
    total_bookings = Booking.query.count()

    return render_template('admin_dashboard.html', 
        total_treks = total_treks,
        total_users = total_users,
        total_staff = total_staff,
        total_bookings = total_bookings
    )

# Admin: View All Treks
@app.route('/admin/treks')
def admin_treks():
    if session.get('role') != 'Admin':
        flash('Access Denied.', 'danger')
        return redirect(url_for('login'))
    
    all_treks = Trek.query.all()
    return render_template('admin_treks.html', treks=all_treks)

# Admin: Add Trek
@app.route('/admin/treks/add', methods=['GET', 'POST'])
def admin_trek_add():
    if session.get('role') != 'Admin':
        flash('Access Denied.', 'danger')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form['name']
        location = request.form['location']
        description = request.form['description']
        difficulty = request.form['difficulty']
        duration_days = request.form['duration_days']
        total_seats = request.form['total_seats']
        price = request.form['price']
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        new_trek = Trek(
            name=name,
            location=location,
            description=description,
            difficulty=difficulty,
            duration_days=int(duration_days),
            total_seats=int(total_seats),
            available_slots=int(total_seats),
            price=float(price),
            start_date=start_date,
            end_date=end_date,
            status='Pending',
            created_by=session['user_id']
        )

        db.session.add(new_trek)
        db.session.commit()
        flash('Trek created successfully.', 'success')
        return redirect(url_for('admin_treks'))

    return render_template('admin_trek_add.html')

@app.route('/admin/treks/edits/<int:trek_id>', methods=['GET', 'POST'])
def admin_trek_edit(trek_id):
    if session.get('role') != 'Admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))

    trek = Trek.query.get(trek_id)

    if not trek:
        flash('Trek not found.', 'danger')
        return redirect(url_for('admin_treks'))
    
    if request.method == 'POST':
        trek.name = request.form['name']
        trek.location = request.form['location']
        trek.description = request.form['description']
        trek.difficulty = request.form['difficulty']
        trek.duration_days = int(request.form['duration_days'])
        trek.total_seats = int(request.form['total_seats'])
        trek.available_slots = int(request.form['available_slots'])
        trek.price = float(request.form['price'])
        trek.start_date = request.form['start_date']
        trek.end_date = request.form['end_date']
        trek.status = request.form['status']

        db.session.commit()
        flash('Trek updated successfully.', 'success')
        return redirect(url_for('admin_treks'))

    return render_template('admin_trek_edit.html', trek=trek)

# Admin: Delete Trek
@app.route('/admin/treks/delete/<int:trek_id>')
def admin_trek_delete(trek_id):
    if session.get('role') != 'Admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))

    trek = Trek.query.get(trek_id)

    if trek:
        db.session.delete(trek)
        db.session.commit()
        flash('Trek deleted successfully.', 'success')
    else:
        flash('Trek not found.', 'danger')

    return redirect(url_for('admin_treks'))

# Admin: View All Staff + Remove
@app.route('/admin/staff')
def admin_staff():
    if session.get('role') != 'Admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))
    
    all_staff = User.query.filter_by(role='Trek Staff', is_approved=True).all()
    all_treks = Trek.query.all()
    return render_template('admin_staff.html', staff=all_stuff, treks=all_treks)

@app.route('/admin/staff/remove/<int:user_id>')
def admin_staff_remove(user_id):
    if session.get('role') != 'Admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))

    staff_user = User.query.get(user_id)

    if staff_user and staff_user.role == 'Trek Staff':
        db.session.delete(staff_user)
        db.session.commit()
        flash(f'{staff_user.username} has been removed.', 'success')
    else:
        flash('Staff member not found.', 'danger')

    return redirect(url_for('admin_staff'))

# Admin: Assign Staff to Trek
@app.route('/admin/staff/assign', methods=['POST'])
def admin_staff_assign():
    if session.get('role') != 'Admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))

    staff_id = request.form['staff_id']
    trek_id = request.form['trek_id']

    # Check if already assigned
    already_assigned = TrekStaff.query.filter_by(
        staff_id=staff_id,
        trek_id=trek_id
    ).first()

    if already_assigned:
        flash('This staff is already assigned to that trek.', 'warning')
    else:
        assignment = TrekStaff(
            staff_id=int(staff_id),
            trek_id=int(trek_id)
        )
        db.session.add(assignment)
        db.session.commit()
        flash('Staff assigned to trek successfully.', 'success')

    return redirect(url_for('admin_staff'))

# ─── Admin: View All Users + Blacklist ───────────────
@app.route('/admin/users')
def admin_users():
    if session.get('role') != 'Admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))

    all_users = User.query.filter_by(role='Trekker').all()
    return render_template('admin_users.html', users=all_users)

@app.route('/admin/users/blacklist/<int:user_id>')
def admin_blacklist_user(user_id):
    if session.get('role') != 'Admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))

    user = User.query.get(user_id)

    if user:
        # Toggle blacklist on and off
        user.is_blacklisted = not user.is_blacklisted
        db.session.commit()

        status = 'blacklisted' if user.is_blacklisted else 'reactivated'
        flash(f'{user.username} has been {status}.', 'success')
    else:
        flash('User not found.', 'danger')

    return redirect(url_for('admin_users'))

@app.route('/admin/staff/blacklist/<int:user_id>')
def admin_blacklist_staff(user_id):
    if session.get('role') != 'Admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))

    staff_user = User.query.get(user_id)

    if staff_user:
        staff_user.is_blacklisted = not staff_user.is_blacklisted
        db.session.commit()

        status = 'blacklisted' if staff_user.is_blacklisted else 'reactivated'
        flash(f'{staff_user.username} has been {status}.', 'success')
    else:
        flash('Staff not found.', 'danger')

    return redirect(url_for('admin_staff'))

# Admin: View All Bookings
@app.route('/admin/bookings')
def admin_bookings():
    if session.get('role') != 'Admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))

    all_bookings = Booking.query.all()
    return render_template('admin_bookings.html', bookings=all_bookings)

# Admin: Search 
@app.route('/admin/search')
def admin_search():
    if session.get('role') != 'Admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))

    query = request.args.get('q', '').strip()
    trek_results = []
    user_results = []
    staff_results = []

    if query:
        # Search treks by name or id
        trek_results = Trek.query.filter(
            Trek.name.ilike(f'%{query}%')
        ).all()

        # Search users by name, email or id
        user_results = User.query.filter(
            User.role == 'Trekker',
            User.username.ilike(f'%{query}%')
        ).all()

        # Search staff by name or email
        staff_results = User.query.filter(
            User.role == 'Trek Staff',
            User.username.ilike(f'%{query}%')
        ).all()

        # Also search by ID if query is a number
        if query.isdigit():
            trek_by_id = Trek.query.get(int(query))
            if trek_by_id and trek_by_id not in trek_results:
                trek_results.append(trek_by_id)

            user_by_id = User.query.get(int(query))
            if user_by_id:
                if user_by_id.role == 'Trekker' and user_by_id not in user_results:
                    user_results.append(user_by_id)
                elif user_by_id.role == 'Trek Staff' and user_by_id not in staff_results:
                    staff_results.append(user_by_id)

    return render_template('admin_search.html',
        query=query,
        trek_results=trek_results,
        user_results=user_results,
        staff_results=staff_results
    )

@app.route('/staff/dashboard')
def staff_dashboard():
    if session.get('role') != 'Trek Staff':
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))
    return render_template('staff_dashboard.html')

@app.route('/trekker/dashboard')
def trekker_dashboard():
    if session.get('role') != 'Trekker':
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))
    return render_template('trekker_dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)