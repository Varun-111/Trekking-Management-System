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
    return render_template('admin_dashboard.html')

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