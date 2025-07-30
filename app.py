from flask import Flask, request, render_template, redirect, session, url_for, flash
import sqlite3
from flask_wtf import Form
from wtforms import TextAreaField, PasswordField, IntegerField, RadioField, SubmitField, EmailField, FloatField
from wtforms.validators import ValidationError, DataRequired, Length, NumberRange
import re


class ChooseLot(Form):
    vh_num = TextAreaField(label="Vehicle Number", validators=[DataRequired(), Length(min=10, max=10, message=None)])


class Lot(Form):
    address = TextAreaField(label="Address", validators=[DataRequired()])
    pincode = IntegerField(label="Pincode", validators=[DataRequired(), NumberRange(min=0, max=999999)])
    price_per_hr = FloatField(label="Price (per hour)", validators=[DataRequired()])
    max_spots = IntegerField(label="Maximum Number of Parking Spots", validators=[DataRequired(), NumberRange(min=1)])

    submit = SubmitField("Add Lot")


class EditLot(Form):
    address = TextAreaField(label="Address", )
    pincode = IntegerField(label="Pincode", validators=[NumberRange(min=0, max=999999)])
    price_per_hr = FloatField(label="Price (per hour)", )
    max_spots = IntegerField(label="Maximum Number of Parking Spots", validators=[NumberRange(min=1)])


class logIn(Form):
    email = EmailField(label="Email", validators=[DataRequired()])
    passwd = PasswordField(label="Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class signUp(Form):
    Fname = TextAreaField(label="Username", validators=[DataRequired()])
    email = EmailField(label="Email", validators=[DataRequired()])
    passwd = PasswordField(label="Password", validators=[DataRequired()])
    gender = RadioField(label="Gender", choices=[(c, c) for c in ['M', 'F']])
    age = IntegerField(label="Age",
                       validators=[DataRequired(), NumberRange(min=18, message="18 or above restriction in place")])

    submit = SubmitField("Signup")


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
        # cur.execute('''DROP TABLE User;''')

        # USER
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
        # cur.execute('''DROP TABLE ParkingSpots;''')
        # cur.execute('''DROP TABLE Vehicles;''')
        # cur.execute('''DROP TABLE Bookings;''')

        # VEHICLES
        cur.execute('''
            CREATE TABLE IF NOT EXISTS Vehicles (
              vehicle_id     INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id        INTEGER NOT NULL,
              vehicle_number TEXT    NOT NULL,
              FOREIGN KEY(user_id) REFERENCES Users(user_id)
                ON DELETE CASCADE
            );
        ''')
        print("what")

        # PARKING LOT
        cur.execute('''
            CREATE TABLE IF NOT EXISTS ParkingLots (
              lot_id         INTEGER PRIMARY KEY AUTOINCREMENT,
              address        TEXT    NOT NULL,
              pin_code       TEXT,
              price_per_hour REAL    NOT NULL,
              max_spots      INTEGER NOT NULL,
              created_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
              free_spots   INTEGER NOT NULL
            );
        ''')

        # sql = f"ALTER TABLE User DROP COLUMN no_spots_booked;"
        # sql = f"DELETE from ParkingLots"
        # cur.execute(sql)

        # PARKING SPOT
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
              duration_hours Float Default NULL,
              total_amount Float Default NULL,
              FOREIGN KEY(spot_id)    REFERENCES ParkingSpots(spot_id)
                ON DELETE CASCADE,
              FOREIGN KEY(vehicle_id) REFERENCES Vehicles(vehicle_id)
                ON DELETE CASCADE
            );
                ''')
        # cur.execute('''ALTER TABLE Bookings ADD COLUMN duration_hours Float Default NULL;''')
        # cur.execute('''ALTER TABLE Bookings ADD COLUMN total_amount Float Default NULL;''')
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
            INSERT INTO ParkingLots (address, pin_code, price_per_hour, max_spots, free_spots)
            VALUES (?, ?, ?, ?, ?)
        ''', (data['address'], data['pincode'], data['price_per_hr'], data['max_spots'], data['max_spots']))
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


def get_lot(lotid):
    with sqlite3.connect(DB) as con:
        cur = con.cursor()
        cur.execute('SELECT * FROM ParkingLots WHERE lot_id = ?', (lotid,))
        return cur.fetchone()


# LSKRMGNV
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
                if s[0] == 'Available':
                    L.append('A')
                elif s[0] == 'Occupied':
                    L.append('O')
                elif s[0] == 'OutOfService':
                    L.append('NA')
            status.append(L)
    return status


status = status_of_lot()


@app.route('/lot/edit/<int:lotid>', methods=['GET', 'POST'])
def edit_lot(lotid):
    with sqlite3.connect(DB) as con:
        cur = con.cursor()
        lot = get_lot(lotid)
        form = EditLot(request.form)
        if request.method == 'POST':
            action = request.form.get('action')
            if action == "update":
                updates = {}
                if form.address.data:
                    updates['address'] = form.address.data
                if form.pincode.data:
                    updates['pin_code'] = form.pincode.data
                    # IntegerFields blank → data is None, so we check is not None
                if form.price_per_hr.data is not None:
                    updates['price_per_hour'] = form.price_per_hr.data
                if form.max_spots.data is not None:
                    updates['max_spots'] = form.max_spots.data
                print(updates)

                if updates:
                    cols = ', '.join(f"{col}=?" for col in updates)
                    params = list(updates.values()) + [lotid]
                    sql = f"UPDATE ParkingLots SET {cols} WHERE lot_id = ?"
                    cur.execute(sql, params)

                    if form.max_spots.data is not None:
                        sql = f"DELETE from ParkingSpots WHERE lot_id = ?"
                        cur.execute(sql, (lotid,))
                        for i in range(0, updates['max_spots']):
                            cur.execute('''INSERT INTO ParkingSpots (lot_id) VALUES (?)''', (lotid,))
                    con.commit()
                    flash(f"Updated fields: {', '.join(updates.keys())}", 'success')
                else:
                    flash("No fields were filled in — nothing to update.", 'warning')
            elif action == "delete":
                cur.execute("select * from ParkingSpots where lot_id = ? and status = ?", (lotid, 'Occupied'))
                data = cur.fetchall()
                print(data)
                if not data:
                    sql = f"DELETE from ParkingLots WHERE lot_id = ?"
                    cur.execute(sql, (lotid,))
                    sql = f"DELETE from ParkingSpots WHERE lot_id = ?"
                    cur.execute(sql, (lotid,))
                    con.commit()
                    return redirect(url_for('admin_dashboard'))
                else:
                    flash('Occupied Spots exist.')
            else:
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('edit_lot', lotid=lotid))
        return render_template('lotDetails.html', lot=lot, form=form)


# SPOTS-----------------------------------------------------------------------------
def get_spots():
    with sqlite3.connect(DB) as con:
        cur = con.cursor()
        cur.execute('SELECT * FROM ParkingSpots')
        return cur.fetchall()


def get_spot(spotid):
    with sqlite3.connect(DB) as con:
        cur = con.cursor()
        cur.execute('SELECT * FROM ParkingSpots WHERE spot_id = ?', (spotid,))
        return cur.fetchall()


@app.route('/spots/<int:spotid>')
def spot_details(spotid):
    with sqlite3.connect(DB) as con:
        cur = con.cursor()
        cur.execute('''
        Select s.spot_id, s.lot_id, l.pin_code, l.price_per_hour, l.address, s.status
         From ParkingSpots as s join ParkingLots as l 
         where s.lot_id=l.lot_id and s.spot_id = ?''', (spotid,))
        spot = cur.fetchone()
        booking = ()
        if spot[-1] == 'Occupied':
            cur.execute('''
            Select b.booking_id, b.spot_id, v.vehicle_number, v.user_id, b.start_time, b.status
            From Bookings as b join Vehicles as v 
            where b.vehicle_id=v.vehicle_id and b.spot_id=? and b.status = ?''', (spotid, 'Booked'))
            booking = cur.fetchone()
            print(booking)
        return render_template('spotDetails.html', spot=spot, bk=booking)


# ADMIN -----------------------------------------------------------------------------
@app.route('/admin/home')
def admin_home():
    boxes = 10  # total boxes
    spots = 9
    return render_template('adminHome.html', boxes=boxes,
                           spots=spots, L=status)


@app.route('/admin/dashboard')
def admin_dashboard():
    users = get_users()
    print(users)
    lots = get_lots()
    spots = get_spots()
    vhs = get_vehicles()
    bks = get_bookings()
    return render_template('adminDashboard.html', name="Admin (Darth Vader)", users=users, lots=lots, spots=spots,
                           vhs=vhs, bks=bks)


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

        cur.execute('''
                    Select user_id from User where email = ?''', (data['email'],))
        userid = cur.fetchone()[0]
        con.commit()
    return userid


# Retrieve Users from DB
def user_check():
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


@app.route('/test', methods=['GET', 'POST'])
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


@app.route('/users/<int:userid>')
def user_details(userid):
    user = user_history(userid)
    print("\n\n")
    j = 0
    for i in user:
        print(j, i)
        j += 1

    return render_template('userDetails.html', user=user)


@app.route('/dashboard/<int:userid>')
def dashboard(userid):
    det = in_progress(userid)
    lots = get_lots()
    return render_template('dashboard.html', lots=lots, details=det, userid=userid)


@app.route('/summary')
def user_summary():
    return render_template('userSummary.html')


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
                if user[2] == user_data['email']:
                    flash("User already Exists. Login, please.")
                    return redirect(url_for('login'))
            userid = add_user(user_data)
            session['Fname'] = user_data['Fname']
            return redirect(url_for('dashboard', userid=userid))
        else:
            flash("All required fields must be filled correctly.")
            return render_template('signup.html', form=form)
    return render_template('signup.html', form=form)


@app.route('/welcome')
def signupSuccess():
    Fname = session.get('Fname', 'Guest')
    return render_template('signupSuccessful.html', Fname=Fname)


# login
@app.route('/login', methods=['POST', 'GET'])
def login():
    form = logIn(request.form)
    if request.method == 'POST':
        if form.validate():
            email, pwd = form.email.data, form.passwd.data
            users = user_check()
            # return redirect(url_for('signupSuccess'))
            if email == 'anakin@gmail.com':
                if pwd == 'padma':
                    return redirect(url_for('admin_home'))
                return render_template('login.html', form=form)
            for user in users:
                if user[4] == email:
                    if user[5] == pwd:
                        session['email'] = user[4]
                        session['user_id'] = user[0]
                        # session.permanent = True
                        return redirect(url_for('dashboard', userid=session.get('user_id')))
                    # flash("Unregistered email. Please, signup.")
                    else:
                        flash("Incorrect password")
                        return redirect(url_for('login'))
            flash("Invalid email or password")
            return redirect(url_for('sign_up'))
        else:
            flash("All required fields must be filled correctly.")
            return render_template('login.html', form=form)
    return render_template('login.html', form=form)


# logout
@app.route('/logout/<name>')
def log_out(name):
    return f'bye, {name}'


# BOOKING----------------------------------------------------------------------------------------------------------
@app.route('/lot/choose/<int:lotid>', methods=['GET', 'POST'])
def book_lot(lotid):
    print("line 1")
    states = [
        "AP", "AR", "AS", "BR", "CG", "CH", "DD", "DL",
        "GA", "GJ", "HP", "HR", "JH", "JK", "KA", "KL",
        "LA", "LD", "MH", "ML", "MN", "MP", "MZ", "NL",
        "OD", "PB", "PY", "RJ", "SK", "TG", "TN", "TR",
        "UK", "UP", "WB"
    ]
    lot = get_lot(lotid)
    print("form request")

    if request.method == 'POST':
        vehicle = request.form.get('vehicle_number', '').strip()
        if not vehicle:
            flash('Vehicle number is required.')
        elif vehicle[:2].upper() not in states:
            flash('invalid state code')
        elif not re.fullmatch(r'^[A-Z]{2}\s*\d{2}\s*[A-Z]{2}\s*\d{4}$', vehicle.upper()):
            flash('Vehicle number must be exactly 10 alphanumeric characters.')
        else:
            with sqlite3.connect(DB) as con:
                cur = con.cursor()
                cur.execute('Select * from ParkingSpots where lot_id = ?', (lotid,))
                rows = cur.fetchall()
                for row in rows:
                    if row[2] == 'Available':
                        spotid = row[0]
                        break
                cur.execute('Select free_spots from ParkingLots where lot_id = ?', (lotid,))
                data = cur.fetchone()
                fr = data[0] - 1
                cur.execute(
                    'UPDATE ParkingSpots SET status = ? WHERE spot_id = ?',
                    ('Occupied', spotid)
                )
                cur.execute(
                    'UPDATE ParkingLots SET free_spots = ? WHERE lot_id = ?',
                    (fr, lotid)
                )
                usr_email = session.get('email')
                cur.execute('''Select user_id from User where email = ?''', (usr_email,))
                data = cur.fetchone()
                usrid = data[0]
                cur.execute('''
                    INSERT INTO Vehicles (user_id, vehicle_number)
                    VALUES (?, ?)
                ''', (usrid, vehicle))
                cur.execute('''Select vehicle_id from Vehicles''')
                data = cur.fetchall()
                vhid = data[-1][0]

                cur.execute('''
                    INSERT INTO Bookings (spot_id, vehicle_id)
                    VALUES (?, ?)
                ''', (spotid, vhid))
                con.commit()
                return render_template(
                    'bookSpots.html', lot=lot
                )

    return render_template(
        'userLotDetails.html',
        lot=lot, userid=session.get('user_id')
    )


@app.route('/lot/book/<int:lotid>', methods=['GET', 'POST'])
def confirm_booking(lotid):
    lot = get_lot(lotid)
    return render_template('bookSpots.html', lot=lot)


def get_vehicles():
    with sqlite3.connect(DB) as con:
        cur = con.cursor()
        cur.execute('SELECT * FROM Vehicles')
        return cur.fetchall()


def get_bookings():
    with sqlite3.connect(DB) as con:
        cur = con.cursor()
        cur.execute('SELECT * FROM Bookings')
        return cur.fetchall()


# RESERVATION-----------------------------------------------------------------------------------------------------
@app.route('/user/spot/<int:spotid>', methods=['GET', 'POST'])
def reservation_details(spotid):
    det = in_progress(session.get('user_id'))
    print("THE USER DETAILS:\n\n", det, "\nspotid = ", spotid)
    print("DET: ", det[0][3])
    for d in det:
        print(d)
    for d in det:
        if d[3] == spotid:
            spot = d
            break
    if request.method == 'POST':
        print("WASSSUP")
        action = request.form.get('action')
        if action == "complete":
            with sqlite3.connect(DB) as con:
                cur = con.cursor()
                cur.execute('''
                    UPDATE Bookings
                    SET end_time       = CURRENT_TIMESTAMP,
                    duration_hours = (julianday(CURRENT_TIMESTAMP) - julianday(start_time)) * 24,
                    status = 'Completed'
                    WHERE booking_id     = ?
                ''', (spot[0],))

                cur.execute('''
                    UPDATE ParkingSpots
                    SET status = 'Available'
                    WHERE spot_id = ?
                ''', (spot[3],))

                cur.execute('''
                SELECT ps.lot_id
                FROM ParkingLots ps join ParkingSpots s
                WHERE ps.lot_id = s.lot_id and s.spot_id = ?
                ''', (spot[3],))
                lot = cur.fetchone()
                lotid = lot[0]

                cur.execute('''
                                    UPDATE ParkingLots
                                    SET free_spots = free_spots+1   
                                    WHERE lot_id = ?
                                ''', (lotid,))

                con.commit()
            return redirect(url_for('bill_details', spotid=spot[3]))

        elif action == "back":
            return redirect(url_for('dashboard', userid=session.get('user_id')))

        else:
            return render_template('reservationDetails.html', spotid=spotid, spot=spot)
    return render_template('reservationDetails.html', spotid=spotid, spot=spot)


@app.route('/user/bill/<int:spotid>', methods=['GET', 'POST'])
def bill_details(spotid):
    details = for_bill(session.get('user_id'), spotid)
    return render_template('billDisplay.html', spot=details)


@app.route('/user/history/<int:userid>', methods=['GET', 'POST'])
def booking_history_user(userid):
    det = completed(userid)
    print(det)
    return render_template('reservationHistory.html', details=det, userid=userid)

@app.route('/user/complete_history/<int:userid>', methods=['GET', 'POST'])
def booking_history_user_all(userid):
    det = get_all_user_bookings(userid)
    return render_template('reservationHistoryAll.html', details=det, userid=userid)


def user_history(userid):
    with sqlite3.connect(DB) as con:
        cur = con.cursor()
        cur.execute(
            '''
                SELECT
                    b.booking_id,
                    v.vehicle_number,
                    v.user_id,
                    b.spot_id,
                    u.fname,
                    pl.address,
                    pl.pin_code,
                    b.status,
                    b.start_time,
                    b.end_time,
                    pl.price_per_hour,
                    ROUND(b.duration_hours, 2),
                    ROUND(b.total_amount, 2),
                    COALESCE(SUM(CASE WHEN b.status = 'Completed' THEN 1 ELSE 0 END), 0) AS spots_used,
                    COALESCE(SUM(CASE WHEN b.status = 'Booked'    THEN 1 ELSE 0 END), 0) AS spots_in_use,
                    CAST(
                        (julianday(COALESCE(b.end_time, CURRENT_TIMESTAMP)) - julianday(b.start_time)) * 24 * 60 * 60
                        AS INTEGER
                    ) AS duration_seconds

                FROM User AS u

                -- Per-user usage summary
                LEFT JOIN (
                    SELECT
                        v.user_id,
                        SUM(CASE WHEN b.status = 'Completed' THEN 1 ELSE 0 END) AS spots_used,
                        SUM(CASE WHEN b.status = 'Booked'    THEN 1 ELSE 0 END) AS spots_in_use,
                        b.status
                    FROM Vehicles AS v
                    LEFT JOIN Bookings AS b ON v.vehicle_id = b.vehicle_id
                    GROUP BY v.user_id
                ) AS us ON u.user_id = us.user_id

                -- Join to vehicles and bookings
                LEFT JOIN Vehicles AS v ON u.user_id = v.user_id
                LEFT JOIN Bookings AS b ON v.vehicle_id = b.vehicle_id

                -- Join from Bookings -> ParkingSpots -> ParkingLots
                LEFT JOIN ParkingSpots AS s ON b.spot_id = s.spot_id
                LEFT JOIN ParkingLots AS pl ON s.lot_id = pl.lot_id

                WHERE v.user_id = ?;
        ''', (userid,)
        )
        data = cur.fetchall()
        print(data)
    return data


def for_bill(userid, spotid):
    with sqlite3.connect(DB) as con:
        cur = con.cursor()
        cur.execute(
            '''
                SELECT
                    b.booking_id,
                    v.vehicle_number,
                    v.user_id,
                    b.spot_id,
                    u.fname,
                    pl.address,
                    pl.pin_code,
                    b.status,
                    b.start_time,
                    b.end_time,
                    pl.price_per_hour,
                    ROUND(b.duration_hours, 2),
                    ROUND(b.total_amount, 2),
                    COALESCE(SUM(CASE WHEN b.status = 'Completed' THEN 1 ELSE 0 END), 0) AS spots_used,
                    COALESCE(SUM(CASE WHEN b.status = 'Booked'    THEN 1 ELSE 0 END), 0) AS spots_in_use,
                    CAST(
                        (julianday(COALESCE(b.end_time, CURRENT_TIMESTAMP)) - julianday(b.start_time)) * 24 * 60 * 60
                        AS INTEGER
                    ) AS duration_seconds

                FROM User AS u

                -- Per-user usage summary
                LEFT JOIN (
                    SELECT
                        v.user_id,
                        SUM(CASE WHEN b.status = 'Completed' THEN 1 ELSE 0 END) AS spots_used,
                        SUM(CASE WHEN b.status = 'Booked'    THEN 1 ELSE 0 END) AS spots_in_use,
                        b.status
                    FROM Vehicles AS v
                    LEFT JOIN Bookings AS b ON v.vehicle_id = b.vehicle_id
                    GROUP BY v.user_id
                ) AS us ON u.user_id = us.user_id

                -- Join to vehicles and bookings
                LEFT JOIN Vehicles AS v ON u.user_id = v.user_id
                LEFT JOIN Bookings AS b ON v.vehicle_id = b.vehicle_id

                -- Join from Bookings -> ParkingSpots -> ParkingLots
                LEFT JOIN ParkingSpots AS s ON b.spot_id = s.spot_id
                LEFT JOIN ParkingLots AS pl ON s.lot_id = pl.lot_id

                WHERE v.user_id = ? and b.spot_id = ?;
        ''', (userid, spotid)
        )
        data = cur.fetchone()
        return data


def get_users():
    with sqlite3.connect(DB) as con:
        cur = con.cursor()
        cur.execute(
            '''SELECT 
        u.user_id,
        u.fname,
        u.email,
        u.age,
        u.gender,
        COALESCE(SUM(CASE WHEN b.status = 'Completed' THEN 1 ELSE 0 END), 0) AS spots_used,
        COALESCE(SUM(CASE WHEN b.status = 'Booked'    THEN 1 ELSE 0 END), 0) AS spots_in_use
    FROM User AS u
    LEFT JOIN Vehicles AS v
        ON u.user_id = v.user_id
    LEFT JOIN Bookings AS b
        ON v.vehicle_id = b.vehicle_id
    GROUP BY
        u.user_id,
        u.fname,
        u.email,
        u.age,
        u.gender;

        '''
        )
        return cur.fetchall()


def in_progress(userid):
    with sqlite3.connect(DB) as con:
        cur = con.cursor()
        cur.execute(
            '''
SELECT
    b.booking_id,
    v.vehicle_number,
    u.user_id,
    b.spot_id,
    pl.address,
    pl.pin_code,
    b.status,
    b.start_time,
    b.end_time,
    pl.price_per_hour,
    CAST(
        (julianday(COALESCE(b.end_time, CURRENT_TIMESTAMP)) - julianday(b.start_time)) * 24 * 60 * 60
        AS INTEGER
    ) AS duration_seconds

FROM User AS u

-- Per-user usage summary
LEFT JOIN (
    SELECT
        v.user_id,
        SUM(CASE WHEN b.status = 'Completed' THEN 1 ELSE 0 END) AS spots_used,
        SUM(CASE WHEN b.status = 'Booked'    THEN 1 ELSE 0 END) AS spots_in_use,
        b.status
    FROM Vehicles AS v
    LEFT JOIN Bookings AS b ON v.vehicle_id = b.vehicle_id
    GROUP BY v.user_id
) AS us ON u.user_id = us.user_id

-- Join to vehicles and bookings
LEFT JOIN Vehicles AS v ON u.user_id = v.user_id
LEFT JOIN Bookings AS b ON v.vehicle_id = b.vehicle_id

-- Join from Bookings -> ParkingSpots -> ParkingLots
LEFT JOIN ParkingSpots AS s ON b.spot_id = s.spot_id
LEFT JOIN ParkingLots AS pl ON s.lot_id = pl.lot_id

WHERE u.user_id = ? and b.status = ?;
        ''', (userid, 'Booked')
        )
        return cur.fetchall()

def completed(userid):
    with sqlite3.connect(DB) as con:
        cur = con.cursor()
        cur.execute('''
            SELECT
                b.booking_id,
                v.vehicle_number,
                v.user_id,
                b.spot_id,
                pl.address,
                pl.pin_code,
                b.status,
                b.start_time,
                b.end_time,
                pl.price_per_hour,
                ROUND(b.duration_hours, 2),
                ROUND(b.total_amount, 2),
                CAST(
                    (julianday(COALESCE(b.end_time, CURRENT_TIMESTAMP)) - julianday(b.start_time)) * 24 * 60 * 60
                    AS INTEGER
                ) AS duration_seconds
            FROM User AS u
            LEFT JOIN Vehicles AS v ON u.user_id = v.user_id
            LEFT JOIN Bookings AS b ON v.vehicle_id = b.vehicle_id
            LEFT JOIN ParkingSpots AS s ON b.spot_id = s.spot_id
            LEFT JOIN ParkingLots AS pl ON s.lot_id = pl.lot_id
            WHERE u.user_id = ? AND b.status = ?
            ORDER BY b.start_time DESC;
        ''', (userid, 'Completed'))
        return cur.fetchall()

def get_all_user_bookings(userid):
    with sqlite3.connect(DB) as con:
        cur = con.cursor()
        cur.execute('''
            SELECT
                b.booking_id,
                v.vehicle_number,
                v.user_id,
                b.spot_id,
                pl.address,
                pl.pin_code,
                b.status,
                b.start_time,
                b.end_time,
                pl.price_per_hour,
                ROUND(b.duration_hours, 2),
                ROUND(b.total_amount, 2)
            FROM User AS u
            LEFT JOIN Vehicles AS v ON u.user_id = v.user_id
            LEFT JOIN Bookings AS b ON v.vehicle_id = b.vehicle_id
            LEFT JOIN ParkingSpots AS s ON b.spot_id = s.spot_id
            LEFT JOIN ParkingLots AS pl ON s.lot_id = pl.lot_id
            WHERE u.user_id = ? AND b.booking_id IS NOT NULL
            ORDER BY b.start_time DESC;
        ''', (userid,))
        return cur.fetchall()


init_db()
print()
if __name__ == '__main__':
    app.run(debug=True)
