from ipaddress import summarize_address_range
from tkinter import Label
from flask_wtf import Form
from wtforms import TextAreaField, PasswordField, IntegerField, RadioField, SubmitField, EmailField
from wtforms.validators import ValidationError, DataRequired

class signUp(Form):
    Fname = TextAreaField(label = "First Name", validators = [DataRequired()])
    Lname = TextAreaField(label = "Last Name",)
    email = EmailField(label = "Email", validators = [DataRequired()])
    passwd = PasswordField(label = "Password", validators = [DataRequired()])
    gender = RadioField(label = "Gender", choices = [(c, c) for c in ['M', 'F']])
    age = IntegerField(label = "Age")

    submit = SubmitField("Signup")

class logIn(Form):
    email = EmailField(label = "Email", validators = [DataRequired()])
    passwd = PasswordField(label = "Password", validators = [DataRequired()])
    submit = SubmitField("Login")

'''
CREATE TABLE IF NOT EXISTS User (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT, --autoincrement
    fname TEXT NOT NULL,
    lname TEXT NOT NULL,
    age INTEGER
    email TEXT NOT NULL UNIQUE,
    passwd TEXT NOT NULL,
    address TEXT,
    pincode TEXT,
    no_spots_booked INTEGER DEFAULT 0;
);
'''