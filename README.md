# Trekking Management System

This is my App Development 1 project for the IITM BS Degree programme (CS2003). I built a trekking management web app where admins can manage treks and staff, staff can manage their assigned treks, and users can browse and book treks.

---

## What I used to build this

- Flask for the backend
- SQLite as the database (managed using Flask-SQLAlchemy)
- Jinja2 + Bootstrap 5 for the frontend
- Werkzeug for password hashing
- Flask sessions for login/auth

---

## How to run this locally

First clone the repo and go into the folder:

```
git clone <your-repo-url>
cd Trekking-Management-System
```

Create a virtual environment and activate it:

```
python -m venv venv

# on windows
venv\Scripts\activate

# on mac/linux
source venv/bin/activate
```

Install the required packages:

```
pip install flask flask-sqlalchemy werkzeug
```

Set up the database (this also creates the admin account):

```
python setup_db.py
```

Run the app:

```
python app.py
```

Then open `http://127.0.0.1:5000` in your browser.

---

## Admin login

```
email    : admin@trek.com
password : admin123
```

The admin account is created automatically when you run setup_db.py. There is no registration page for admin.

---

## The three roles

**Admin** — pre-created, manages everything. Can add/edit/delete treks, approve and assign staff, blacklist users, and view all bookings.

**Trek Staff** — registers through the site but can only login after the admin approves their account. Can view and manage their assigned treks and see who booked.

**Trekker** — registers and can login immediately. Can browse open treks, book them, cancel bookings, and view their history.

---

## Files in this project

```
app.py          all the routes and logic
models.py       database models (User, Trek, TrekStaff, Booking)
setup_db.py     run this once to create tables and seed admin
config.py       just holds the secret key

templates/      all the html files
  base.html
  index.html
  login.html
  register.html
  admin_dashboard.html
  admin_treks.html
  admin_trek_add.html
  admin_trek_edit.html
  admin_staff.html
  admin_users.html
  admin_bookings.html
  admin_search.html
  pending_staff.html
  staff_dashboard.html
  staff_trek_detail.html
  staff_profile.html
  trekker_dashboard.html
  trekker_treks.html
  trekker_bookings.html
  trekker_profile.html

static/
  styles.css    small custom styles on top of bootstrap
```

---

## Database tables

- users — all three roles stored here, role column tells them apart
- treks — trek details, created by admin
- trek_staff — which staff is assigned to which trek
- bookings — one row per trekker booking

---

## Trek status flow

A trek goes through these stages:

```
Pending → Approved → Open → Closed → Completed
```

Trekkers can only book a trek when it is Open. When staff marks a trek as Completed, all active bookings for that trek automatically get marked Completed too.

---

## Booking rules

- Trek has to be Open
- Available slots have to be more than 0
- You can't book the same trek twice
- If you cancel, the slot goes back to the trek

---

## Notes

- If you add a new column to models.py, delete trekking.db and run setup_db.py again
- The trekking.db file is in .gitignore so it won't be pushed
- Staff accounts show as pending until admin approves from the dashboard