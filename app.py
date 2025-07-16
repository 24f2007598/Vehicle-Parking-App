from flask import Flask, request, render_template, redirect, session, url_for, flash
import sqlite3
from flask_wtf import Form
from wtforms import TextAreaField, PasswordField, IntegerField, RadioField, SubmitField, EmailField, FloatField
from wtforms.validators import ValidationError, DataRequired, Length, NumberRange


class Lot(Form):
    address = TextAreaField(label = "Address", validators = [DataRequired()])
    pincode = IntegerField(label = "Pincode", validators=[DataRequired(), NumberRange(min=0, max=999999)])
    price_per_hr = FloatField(label = "Price (per hour)", validators=[DataRequired()])
    max_spots = IntegerField(label = "Maximum Number of Parking Spots", validators=[DataRequired(), NumberRange(min=1)])

    submit = SubmitField("Add Lot")

class EditLot(Form):
    address = TextAreaField(label = "Address",)
    pincode = IntegerField(label = "Pincode", validators=[NumberRange(min=0, max=999999)])
    price_per_hr = FloatField(label = "Price (per hour)",)
    max_spots = IntegerField(label = "Maximum Number of Parking Spots", validators=[NumberRange(min=1)])


class logIn(Form):
    email = EmailField(label = "Email", validators = [DataRequired()])
    passwd = PasswordField(label = "Password", validators = [DataRequired()])
    submit = SubmitField("Login")

class signUp(Form):
    Fname = TextAreaField(label = "Username", validators = [DataRequired()])
    email = EmailField(label = "Email", validators = [DataRequired()])
    passwd = PasswordField(label = "Password", validators = [DataRequired()])
    gender = RadioField(label = "Gender", choices = [(c, c) for c in ['M', 'F']])
    age = IntegerField(label = "Age", validators = [DataRequired(), NumberRange(min=18, message="18 or above restriction in place")])

    submit = SubmitField("Signup")


app = Flask(__name__)
app.secret_key = "private_key"
DB = 'data.db'

O = 'O'
A = 'A'
num = 9


# Database Initialization
def init_db():
    with sqlite3.connect(DB) as con:
        cur = con.cursor()

        # cur.execute('''
        #             INSERT INTO User (fname, lname, email, passwd, gender, age)
        #             VALUES (?, ?, ?, ?, ?, ?)
        #         ''', ('Darth', 'Vader', 'anakin@gmail.com', "padma", "M", 20))


        cur.execute('''DROP TABLE User;''')

#USER
        cur.execute('''
            CREATE TABLE IF NOT EXISTS User (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                fname TEXT NOT NULL,
                age INTEGER,
                gender TEXT,
                email TEXT UNIQUE NOT NULL,
                passwd TEXT NOT NULL,
                no_spots_booked DEFAULT 0
            );
        ''')

        # cur.execute('''DROP TABLE ParkingLots;''')

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

# LOTS-----------------------------------------------------------------------------
@app.route('/newlot', methods=['POST', 'GET'])
def create_lot():
    form = Lot(request.form)
    if request.method == 'POST':
        if form.validate():
            lot_data = {
                'address': form.address.data,
                'pincode': form.pincode.data,
                'price_per_hr': form.price_per_hr.data,
                'max_spots': form.max_spots.data
            }
            add_lot(lot_data)
            return redirect(url_for('admin_dashboard'))
        else:
            flash("All required fields must be filled correctly.")
            return render_template('newLot.html', form=form)
    return render_template('newLot.html', form=form)

def add_lot(data):
    with sqlite3.connect(DB) as con:
        cur = con.cursor()
        cur.execute('''
            INSERT INTO ParkingLots (address, pin_code, price_per_hour, max_spots)
            VALUES (?, ?, ?, ?)
        ''', (data['address'], data['pincode'], data['price_per_hr'], data['max_spots']))
        con.commit()

        cur.execute('SELECT lot_id, max_spots FROM ParkingLots')
        rows = cur.fetchall()
        lotid, maxspotnum = int(rows[-1][0]), data['max_spots']
        for i in range(0, maxspotnum):
            cur.execute('''INSERT INTO ParkingSpots (lot_id) VALUES (?)''', (lotid,))
        con.commit()

# @app.route('/lots')
# def lot_success():
#     lots = get_lots()
#     return render_template('lotDetails.html', lots=lots)

def get_lots():
    with sqlite3.connect(DB) as con:
        cur = con.cursor()
        cur.execute('SELECT * FROM ParkingLots')
        return cur.fetchall()

def get_lot(lotid) :
    with sqlite3.connect(DB) as con:
        cur = con.cursor()
        cur.execute('SELECT * FROM ParkingLots WHERE lot_id = ?', (lotid,))
        return cur.fetchone()


#LSKRMGNV
def status_of_lot():
    lots = get_lots()
    with sqlite3.connect(DB) as con:
        cur = con.cursor()
        status = []
        for lot in lots:
            L = []
            cur.execute('SELECT status FROM ParkingSpots WHERE lot_id = ?', (lot[0],))
            stats = cur.fetchall()
            for s in stats:
                if s[0] == 'Available': L.append('A')
                elif s[0] == 'Occupied': L.append('O')
                elif s[0] == 'OutOfService': L.append('NA')
            status.append(L)
    return status

status = status_of_lot()

@app.route('/lot/edit', methods=['GET', 'POST'])
def edit_lot():
    with sqlite3.connect(DB) as con:
        cur = con.cursor()
        lotid = request.args.get('lotid', type=int)
        lot = get_lot(lotid)
        fields = {}
        form = EditLot(request.form)
        if request.method == 'POST':
            action = request.form.get('action')
            if action == "update":
                if form.validate():
                    lot_data = {
                        'address': form.address.data,
                        'pincode': form.pincode.data,
                        'price_per_hour': form.price_per_hr.data,
                        'max_spots': form.max_spots.data
                    }
                    for field in lot_data:
                        value = lot_data[field]
                        if value:
                            fields[field] = value
                    if  fields:
                        tup = ', '.join(f"{k} = ?" for k in fields)
                        values = list(fields.values()) + [lotid]
                        query = f"UPDATE ParkingLots SET {tup} WHERE lot_id = ?"
                        cur.execute(query, values)
                        con.commit()
                    return redirect(url_for('admin_dashboard'))
            elif action == "cancel":
                return redirect(url_for('admin_dashboard'))
    return render_template('lotDetails.html', lot=lot, form=form)



# SPOTS-----------------------------------------------------------------------------
def get_spots():
    with sqlite3.connect(DB) as con:
        cur = con.cursor()
        cur.execute('SELECT * FROM ParkingSpots')
        return cur.fetchall()

@app.route('/result')
def spot_details():
    selected = request.args.get('selected')
    return render_template('spotDetails.html', selected=selected)

# ADMIN -----------------------------------------------------------------------------
@app.route('/admin/home')
def admin_home():
    boxes = 10   # total boxes
    spots = num
    return render_template('adminHome.html', boxes=boxes,
                           spots=spots, L=status)


@app.route('/admin/dashboard')
def admin_dashboard():
    users = get_users()
    lots = get_lots()
    spots = get_spots()
    return render_template('adminDashboard.html', name="Admin (Darth Vader)", users=users, lots=lots, spots=spots)

@app.route('/admin/search')
def admin_search():
    return render_template('search.html')


# USERS -----------------------------------------------------------------------------
# Insert User Data into DB
def add_user(data):
    with sqlite3.connect(DB) as con:
        cur = con.cursor()
        cur.execute('''
            INSERT INTO User (fname, email, passwd, gender, age)
            VALUES (?, ?, ?, ?, ?)
        ''', (data['Fname'], data['email'], data['passwd'], data['gender'], data['age']))
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

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/test', methods=['GET','POST'])
def test():
    # initialize only once
    if 'boxes_data' not in session:
        session['boxes_data'] = status

    boxes_data = session['boxes_data']
    selected = None

    if request.method == 'POST':
        sel = request.form.get('selected')
        if sel:
            # parse "btn-b-i"
            parts = sel.split('-')
            if len(parts) == 3:
                b, i = map(int, parts[1:])
                # guard: only accept if it really was an "A"
                if boxes_data[b][i] == 'A':
                    selected = sel

    return render_template('test.html',
                           boxes_data=boxes_data,
                           selected=selected)

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
                if user[5] == email:
                    if user[6] == pwd:
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
