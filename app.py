from flask import Flask, request, render_template, redirect, session, url_for, flash
import sqlite3
from signing_up import signUp, logIn

app = Flask(__name__)
app.secret_key = "private_key"
DB = 'data.db'

# Database Initialization
def init_db():
    with sqlite3.connect(DB) as con:
        cur = con.cursor()

        # cur.execute('''
        #             INSERT INTO User (fname, lname, email, passwd, gender, age)
        #             VALUES (?, ?, ?, ?, ?, ?)
        #         ''', ('Darth', 'Vader', 'anakin@gmail.com', "padma", "M", 20))

#USER
        cur.execute('''
            CREATE TABLE IF NOT EXISTS User (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                fname TEXT NOT NULL,
                lname TEXT,
                age INTEGER,
                gender TEXT,
                email TEXT UNIQUE NOT NULL,
                passwd TEXT NOT NULL,
                no_spots_booked DEFAULT 0
            );
        ''')

#VEHICLES
        cur.execute('''
            CREATE TABLE IF NOT EXISTS Vehicles (
              vehicle_id     INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id        INTEGER NOT NULL,
              vehicle_number TEXT    NOT NULL,
              FOREIGN KEY(user_id) REFERENCES Users(user_id)
                ON DELETE CASCADE
            );
        ''')

#PARKING LOT
        cur.execute('''
            CREATE TABLE IF NOT EXISTS ParkingLots (
              lot_id         INTEGER PRIMARY KEY AUTOINCREMENT,
              name           TEXT    NOT NULL,
              address        TEXT    NOT NULL,
              pin_code       TEXT,
              price_per_hour REAL    NOT NULL,
              max_spots      INTEGER NOT NULL,
              created_at     DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        ''')

#PARKING SPOT
        cur.execute('''
            CREATE TABLE IF NOT EXISTS ParkingSpots (
              spot_id  INTEGER PRIMARY KEY AUTOINCREMENT,
              lot_id   INTEGER NOT NULL,
              status   TEXT    NOT NULL DEFAULT 'Available'
                         CHECK(status IN ('Available','Occupied','OutOfService')),
              FOREIGN KEY(lot_id) REFERENCES ParkingLots(lot_id)
                ON DELETE CASCADE
            );
        ''')

# BOOKINGS
        cur.execute('''
            CREATE TABLE IF NOT EXISTS Bookings (
              booking_id  INTEGER PRIMARY KEY AUTOINCREMENT,
              spot_id     INTEGER NOT NULL,
              vehicle_id  INTEGER NOT NULL,
              start_time  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
              end_time    DATETIME,
              status      TEXT    NOT NULL DEFAULT 'Booked'
                           CHECK(status IN ('Booked','Completed','Cancelled')),
              FOREIGN KEY(spot_id)    REFERENCES ParkingSpots(spot_id)
                ON DELETE CASCADE,
              FOREIGN KEY(vehicle_id) REFERENCES Vehicles(vehicle_id)
                ON DELETE CASCADE
            );
                ''')

        con.commit()

# Insert User Data into DB
def add_user(data):
    with sqlite3.connect(DB) as con:
        cur = con.cursor()
        cur.execute('''
            INSERT INTO User (fname, lname, email, passwd, gender, age)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (data['Fname'], data['Lname'], data['email'], data['passwd'], data['gender'], data['age']))
        con.commit()

# Retrieve Users from DB
def get_users():
    with sqlite3.connect(DB) as con:
        cur = con.cursor()
        cur.execute('SELECT * FROM User')
        return cur.fetchall()

@app.route('/what')
def defaultHome():
    return render_template('home.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/')
def test():
    boxes = 10   # total boxes
    rows = 5    # button‐grid rows per box
    cols = 4    # button‐grid cols per box
    return render_template('test.html',
                           boxes=boxes,
                           rows=rows,
                           cols=cols)

# ADMIN -----------------------------------------------------------------------------
@app.route('/admin/home')
def admin_home():
    return render_template('adminHome.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    users = get_users()
    return render_template('adminDashboard.html', name="Admin (Darth Vader)", users=users)

@app.route('/admin/search')
def admin_search():
    return render_template('search.html')

#-------------------------------------------------------------------------------------

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')



# SIGNIN LOGIN LOGOUT -------------------------------------------------------------------
@app.route('/signup', methods=['POST', 'GET'])
def sign_up():
    form = signUp(request.form)
    if request.method == 'POST':
        if form.validate():
            user_data = {
                'Fname': form.Fname.data,
                'Lname': form.Lname.data,
                'email': form.email.data,
                'passwd': form.passwd.data,
                'gender': form.gender.data,
                'age': form.age.data
            }
            users = get_users()
            for user in users:
                if user[3] == user_data['email']:
                    flash("User already Exists. Login, please.")
                    return redirect(url_for('login'))
            add_user(user_data)
            session['Fname'] = user_data['Fname']
            return redirect(url_for('signupSuccess'))
        else:
            flash("All required fields must be filled correctly.")
            return render_template('signup.html', form=form)
    return render_template('signup.html', form=form)

@app.route('/welcome')
def signupSuccess():
    Fname = session.get('Fname', 'Guest')
    return render_template('signupSuccessful.html', Fname=Fname)

#login
@app.route('/login', methods = ['POST', 'GET'])
def login():
    form = logIn(request.form)
    if request.method == 'POST':
        if form.validate():
            email, pwd = form.email.data, form.passwd.data
            users = get_users()
            # return redirect(url_for('signupSuccess'))

            if email == 'anakin@gmail.com':
                if pwd == 'padma':
                    return redirect(url_for('admin_home'))
                return render_template('login.html', form=form)

            for user in users:
                if user[3] == email:
                    if user[4] == pwd:
                        session['username'] = user[1]
                        return redirect(url_for('dashboard'))
                # flash("Unregistered email. Please, signup.")
            flash("Invalid email or password")
            return redirect(url_for('sign_up'))
        else:
            flash("All required fields must be filled correctly.")
            return render_template('login.html', form=form)
    return render_template('login.html', form=form)

#logout
@app.route('/logout/<name>')
def log_out(name):
    return f'bye, {name}'

init_db()

if __name__ == '__main__':
    app.run(debug=True)
