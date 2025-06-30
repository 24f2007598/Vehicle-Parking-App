from flask import Flask, request, render_template, flash, redirect, session, url_for
# from flask_sqlalchemy import SQLAlchemy
# from flask_login import LoginManager, UserMixin
import sqlite3

from signing_up import signUp
app = Flask(__name__)
app.secret_key = "private_key"

@app.route('/')
def defaultHome():
    return render_template('home.html')

#home
@app.route('/home')
def home():
    return render_template('home.html')

# #login
# @app.route('/login/yeah')
# def login():
#     return render_template('login.html')

#dashboard
@app.route('/dashboard')
def dashboard():
    dic = {'Joe': 101, 'Ann': 102, 'Bob': 103}
    return render_template('dashboard.html', dashboard = dic)

#signup
@app.route('/signup', methods = ['POST', 'GET'])
def sign_up():
    signup = signUp()
    if request.method == 'POST':
        session['Fname'] = request.form['Fname']
        session['Lname'] = request.form['Lname']
        if signup.validate() == "False":
            flash("Required Field")
            return render_template('signup.html', form = signup)
        else:
            return redirect(url_for('signupSuccess'))
    elif request.method == 'GET':
        return render_template('signup.html', form=signup)
    else:
        return home()



@app.route('/welcome')
def signupSuccess():
    Fname = "HOAX"
    # Fname = session.get('Fname', None)
    # Lname = session.get('Lname', None)
    return render_template('signupSuccessful.html', Fname)

#login
@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        user = request.form['userName']
        passwd = request.form['userPasswd']
        if user == 'lion' and passwd == 'abc123':
            return dashboard()
        else:
            return home()
    else:
        user = request.args.get('userName')
        return render_template('login.html', name = user)

#logout
@app.route('/logout/<name>')
def log_out(name):
    return f'bye, {name}'

#DATABASE CREATION
def create_db():
    with sqlite3.connect(DB) as c:
        c.execute(
            '''CREATE TABLE IF NOT EXISTS User (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT, --autoincrement
    user_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    pwd_hash TEXT NOT NULL,
    address TEXT,
    pincode TEXT,
    no_spots_booked INTEGER NOT NULL;
);
'''
        )

@app.route("/add", methods=["POST"])
def add():
    title = request.form["title"]
    if title:
        add_user(title)
    return redirect("/")

def add_user(title: str):
    with sqlite3.connect(DB) as c:
        c.execute("INSERT INTO User (title) VALUES (?)", (title,))

def get_users():
    with sqlite3.connect(DB) as c:
        c.row_factory = sqlite3.Row
        return c.execute("SELECT * FROM tasks").fetchall()

# NEW ───────────────────────────────────────────────────────────────
def snapshot_db():
    rows = get_users()
    print("\n--- DB snapshot ---")
    for r in rows:
        print(f"{r['id']}: {r['title']}")
    print("-------------------\n")
# ───────────────────────────────────────────────────────────────────


if __name__ == '__main__':
    app.run(debug=True)


# app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///db.db'
# app.config['SECRET_KEY']='619619'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True
# db = SQLAlchemy(app)
#
# login_manager = LoginManager()
# login_manager.init_app(app)
#
# class user(UserMixin, db.Model):
#     id = db.Column(db.Integer, primary_key=True,autoincrement=True)
#     username = db.Column(db.String(200))
#     email = db.Column(db.String(200))
#     passwd = db.Column(db.String(200))
