# Authors: Saurin Patel, Sagar Patel
# Program Name: Utivity Productivity app
# Program Description: Page dedicated for database and related stuff and modules for our app
# Last Revision Date: 2021 - 1 - 30
# ICS 4U1
# Mr. Moore
#-------------------------------------------------------------------------------------------#
#importing all the necessary modules to run the app effectively
from __future__ import division
import os
import secrets
from datetime import datetime
from flask import Flask, render_template, url_for, flash, redirect, request #module for flask
from flask_sqlalchemy import SQLAlchemy #module for flask database
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user
from flask_bcrypt import Bcrypt #hashing module to encrypt password
from PIL import Image #convert images into small bits
from sqlalchemy import create_engine #module to run raw SQL if need be
from flask_wtf import FlaskForm #flask user input form module
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from pytz import timezone #timezone module
from sqlalchemy import func #module to use functions from sqlalchemy, like sum()
tz = timezone('EST') # function to convert time into EST

#-Configuration of database and flask logic-------------------#
app = Flask(__name__) #initialize Flask app
app.config.from_object('config') #create app confix
app.config['SECRET_KEY'] = '04d48666f760c424461548b3570ea97e2e4e05325b5751ca6' #create a secret key to prevent injection attacks
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db' #created and configs database
db = SQLAlchemy(app) # creates instance of the SQLAlchemy class
bcrypt = Bcrypt(app) # creates instance of the Bcrypt class for encryption usage
login_manager = LoginManager(app) # creates instance of LoginManager class
#-Tables/Models-----------------------------------------------#
@login_manager.user_loader
def load_user(user_id): #loads the user_id so we know which user is logged in so we can query and filter databases
    return User.query.get(int(user_id))
#-------------------------------------------------------------#
class User(db.Model, UserMixin): #Creates the user database table
    id = db.Column(db.Integer, primary_key=True) #primary user id key
    username = db.Column(db.String(25), unique=True, nullable=False) #username 
    email = db.Column(db.String(120), unique=True, nullable=False) #email
    image_file = db.Column(db.String(20), nullable=False, default='default.png') #profile picture
    password = db.Column(db.String(60), nullable=False) #password
#-------------------------------------------------------------#
class Tasks(db.Model): #Creates the database table for the user's tasks
    id = db.Column(db.Integer, primary_key=True) #primary user id key
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now(tz)) #current time the todo was posted
    task = db.Column(db.String(150)) #The user's task
    author = db.Column(db.String(100)) #The author's username who wrote this
#-------------------------------------------------------------#
class Times(db.Model): #Creates the database table for the user's times
    id = db.Column(db.Integer, primary_key=True) #primary user id key
    start_time = db.Column(db.String(100), nullable=False, default=datetime.now(tz)) #start time of the session
    elapsed_time = db.Column(db.String(100), nullable=False, default=datetime.now(tz)) #total elapsed time of session
    author = db.Column(db.String(103)) #the author's username who did the session
#-------------------------------------------------------------#
#Registration for where the user can sign up
class RegistrationForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired(), Length(min=2, max=20)]) #They must input a username
    email = StringField('Email',validators=[DataRequired(), Email()]) #input an email
    password = PasswordField('Password', validators=[DataRequired()]) #Input a password
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')]) #reenter password
    submit = SubmitField('Sign Up') #Finally press the submit button to push all values into the database

    def validate_username(self, username): #this function validates the username by querying making sure no one else took it
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.') #Raises error if someone did take it

    def validate_email(self, email):  #this function validates the email by querying making sure no one else took it
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.') #Raises error if someone did take it
#-------------------------------------------------------------#
class LoginForm(FlaskForm): #Login form for where the user can sign into their account
    email = StringField('Email',validators=[DataRequired(), Email()]) #They must provide their email
    password = PasswordField('Password', validators=[DataRequired()]) #they must provide their password
    submit = SubmitField('Login') #and they must press submit so the data is pushed to the database
#-------------------------------------------------------------#
class UpdateAccountForm(FlaskForm): #This is the update account form in settings where the user can update...
    picture = FileField('', validators=[FileAllowed(['jpg', 'png'])]) #Their profile picture!
    submit = SubmitField('Update Profile Picture') #once they press submit it will replace the previous image in the db
# Templates---------------------------------------------------#
@app.route('/') #Main route for Flask, which is in our case, the splash screen since it is the first one to load in
def splash():
    return render_template('splash.html') #Renders the splash screen
#-------------------------------------------------------------#
@app.route('/home') #Screen where the user can read a brief description about our app and choose to sign up/in
def home():
    return render_template('home.html') #Renders the home screen
#-------------------------------------------------------------#
@app.route("/help") #Help page 
def help():
    image_file = url_for('static', filename='img/' + current_user.image_file) #Returns the image for the user
    return render_template('help.html', image_file=image_file) #renders the template and provides variable for user pfp
#-------------------------------------------------------------#
@app.route("/register", methods=['GET', 'POST']) #Registration page
def register():
    if current_user.is_authenticated: #If the user is logged in
        return redirect(url_for('dashboard')) #Bring them to the dasboard
    form = RegistrationForm() #If not, then show them the registration form
    if form.validate_on_submit(): #If they pressed submit and everything was ok...
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8') #Hash their password
        user = User(username=form.username.data, email=form.email.data, password=hashed_password) #Insert their credentials into db
        db.session.add(user) #Add the user to the db session
        db.session.commit() #And commit their data to the User Table to be stored permanently
        flash(f'Account created for {form.username.data}!', 'flash success') #Then give off a flash showing their account was created
        return redirect(url_for('login')) #redirect them to the login url page so they can sign in
    return render_template('register.html', title='Register', form=form) #If they didn't enter the form, just return the register file
#-------------------------------------------------------------#
@app.route("/login", methods=['GET', 'POST']) #Login page 
def login():
    if current_user.is_authenticated: #If the user is logged in
        return redirect(url_for('dashboard')) #Bring them to the dashboard
    form = LoginForm() #Display a form of a login page

    #If the user signs in sucessfully and their hashed password matches the password, they are logged in
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first() 
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user) #Initiate the login user function so they stay logged in
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard')) #Redirect them to their dashboard
        else:
            flash('Login Unsuccessful. Please check email and password', 'flash fail') #Return fail screen if they failed registration
    return render_template('login.html', title='Login', form=form) #Return template that displays the login page and the form
#-------------------------------------------------------------#
@app.route("/logout") #Logout template
def logout():
    logout_user() #If they request to log out, then run the log out function to do so
    return redirect(url_for('home')) #Return the user back to home
#-------------------------------------------------------------#
def save_picture(form_picture): #Function to save the picture to the database
    random_hex = secrets.token_hex(8) #Creates a random token of 8 bits
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/img', picture_fn) #The pictures path will lead to images folder
    output_size = (50, 50) #The image will be 50px by 50px
    i = Image.open(form_picture) #Open the image
    i.thumbnail(output_size) 
    i.save(picture_path) #Save the picture to our images folder
    return picture_fn #Return the hex token
#-------------------------------------------------------------#
@app.route("/settings", methods=['GET', 'POST']) #Settings page
def settings():
    form = UpdateAccountForm() #The user has the update form so they can change their profile picture if they want
    if form.validate_on_submit():
        if form.picture.data: #If they wish to change their pfp...
            picture_file = save_picture(form.picture.data) #Assign the picture they chose to a variable
            current_user.image_file = picture_file #Assign the users current image to the picture file they chose
        db.session.commit() #Add the new image to the database so the session is created
        return redirect(url_for('settings')) #Return the user back to settings so it refreshes
    image_file = url_for('static', filename='img/' + current_user.image_file) #Return the user logo in top right corner
    return render_template('settings.html', image_file=image_file, form=form) #Return the settings html template
#-------------------------------------------------------------#
@app.route('/todo') #To do Page
def todo():
    image_file = url_for('static', filename='img/' + current_user.image_file) #Image for the user'f pfp
    tasks = Tasks.query.filter_by(author=current_user.username).all() #Query all the tasks by returning the ones that match with the username
    return render_template('todo.html', username=current_user.username, tasks=tasks,image_file=image_file) #Return the todot template and tasks
#-------------------------------------------------------------#
@app.route('/create_task', methods=['POST']) #Create task for todo list
def create_task():
    task = request.form.get('task_field') #Requests the data from the form 
    new_task = Tasks(task=task, author=current_user.username) #Creates a new task in the database and assigned to the current user
    db.session.add(new_task) #Create the session for the task
    db.session.commit() #And commit the session so their todo is saved to the db
    return redirect(url_for('todo')) #Refresh the page so the new task appears
#-------------------------------------------------------------#
@app.route('/edit_task/<task_id>', methods=['POST']) #Edit task function
def edit_task(task_id):
    edit = request.form.get('task_field') #Request the new information in the task text field
    if edit: #If there is a change
        task = Tasks.query.filter_by(id=task_id).first() #Then query the tasks by the id that matches with it
        task.task = edit #And add the edits to the original task so it is replaced
        db.session.commit() #Commit the tasks to the database there so it is saved
    return redirect(url_for('todo')) #Refresh the to do page
#-------------------------------------------------------------#
@app.route('/remove_task/<task_id>', methods=['POST']) #Delete task function
def remove_task(task_id): 
    task = Tasks.query.filter_by(id=task_id).first() #Look for the task the user wants to delete
    db.session.delete(task) #If they press delete, then it will remove the session from the database
    db.session.commit() #It will commit these changes so that the task is no longer there
    return redirect(url_for('todo')) #Refreshes the do page so the deletion is evident
#-------------------------------------------------------------#
@app.route("/timer", methods=['GET', 'POST']) #timer page
def timer():
    if request.method == "POST": #If the user presses the submit button from the timer
        start_time = request.form.get('todaydate') #Then request the start date (hidden form)
        elapsed_time = request.form.get('time') #And request the elapsed time (hidden form)
        new_time = Times(start_time=start_time, elapsed_time=elapsed_time, author=current_user.username) #Createdb entry 
        db.session.add(new_time) #Add the new timestamp to the database entry
        db.session.commit() #Commit the entry so it premanently saves
        return redirect(url_for('history')) #Redirect the user to the history page so they can see their new time
    image_file = url_for('static', filename='img/' + current_user.image_file) #Return the user's pfp
    return render_template('timer.html',image_file=image_file) #Render the timer template
#-------------------------------------------------------------#
@app.route("/history") #History page
def history():
    image_file = url_for('static', filename='img/' + current_user.image_file) #Return the users pfp
    times = Times.query.filter_by(author=current_user.username).all() #It takes all the times from the database that associate with the current user
    return render_template('history.html', username=current_user.username, times=times, image_file=image_file) #And returns it to the history .html
#-------------------------------------------------------------#
def time_into_sec(time_as_a_string): #function to convert dateTime string into hours, minutes, and seconds
    h, m, s = time_as_a_string.split(':') #It takes the string and splits it into hrs, min, and sec
    return int(h) * 3600 + int(m) * 60 + int(s) #It calculates the total elapsed time in seconds
#-------------------------------------------------------------#
@app.route('/dashboard', methods=['GET', 'POST']) #Dashboard page
def dashboard():
    image_file = url_for('static', filename='img/' + current_user.image_file) #Returns the user icon
    #----------- TOTAL PRODUCTIVITY LIFETIME -----------#
    # The code within this section calculates the total productivity the user has ever done using this app
    # The function takes all the elapsed times which associate with the current user
    # Then a for loop is used to add all the times in the elapsed list into a single totaled variables
    #this variable is ran through some calculations and then pushed into the dashboard .html to be displayed
    list_of_elapsed_times = [time.elapsed_time for time in Times.query.filter_by(author=current_user.username).all()]
    total_productivity_lifetime = 0
    for time in list_of_elapsed_times:
        updated_time = time_into_sec(time)        
        total_productivity_lifetime += round((updated_time/3600.0),4)
    total_productivity_lifetime = round(total_productivity_lifetime,5)
    total_productivity_lifetime = str(total_productivity_lifetime) + " HRS" #Total productivity of all user's account-life
    #----------- TOTAL PRODUCTIVITY TODAY -----------#
    # The code within this section calculates the total productivity the user has done during the current day
    # The function takes all the elapsed times which associate with the current user and where the current day equals the start date
    # Then a for loop is used to add all the times in the elapsed list into a single totaled variables
    #this variable is ran through some calculations and then pushed into the dashboard .html to be displayed
    list_of_today_elapsed_times = [time.elapsed_time for time in Times.query.filter_by(author=current_user.username,start_time=datetime.today().strftime("%m/%d/%Y")).all()]
    total_productivity_today = 0
    for time in list_of_today_elapsed_times:
        updated_time = time_into_sec(time)        
        total_productivity_today += round((updated_time/3600.0),4)
    total_productivity_today = round(total_productivity_today,5)
    total_productivity_today_temp = total_productivity_today
    total_productivity_today =  str(total_productivity_today) + " HRS" #Final calculated productivity in today
    #----------- TOTAL PRODUCTIVITY TODAY PERCENTAGE -----------#
    # The final is the productivity percentage which displays the percentage of the current days productivity in relation to the whole day
    total_productivity_today_perc = total_productivity_today_temp/24.0
    total_productivity_today_perc = total_productivity_today_perc * 100.0
    total_productivity_today_perc = round(total_productivity_today_perc,5)
    total_productivity_today_perc = str(total_productivity_today_perc) + "%" #Final calculated productivity %
    #-----------------------------------------------------------#
    # Return the template with all three variables above to be displayed on the page
    return render_template('dashboard.html',total_productivity_today=total_productivity_today,total_productivity_lifetime=
    total_productivity_lifetime,total_productivity_today_perc=total_productivity_today_perc,image_file=image_file)
#-------------------------------------------------------------#
