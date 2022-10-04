from flask import Flask, render_template, flash, redirect, url_for, request
from app import app, query_db, load_user, login_manager, User
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from app.forms import IndexForm, PostForm, FriendsForm, ProfileForm, CommentsForm
from datetime import datetime
import os
import rsa
import zlib
import hashlib
import hmac

#############################
from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, SubmitField, TextAreaField, IntegerField, BooleanField, RadioField)
from wtforms.validators import InputRequired, Length

# this file contains all the different routes, and the logic for communicating with the database

@app.route('/logout') # This route is called when you press the Log Out button found on line 50 in base.html
def logout():
    logout_user() # User is logged out...
    return redirect("/index") #... and sent to the 'index' route

# home page/login/registration
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = IndexForm()
    
    if form.login.is_submitted() and form.login.submit.data:
        if not form.login.validate_on_submit():

            user = User() #Vi lager en tom bruker
            sql = query_db('SELECT * FROM Users WHERE username="{}";'.format(form.login.username.data), one=True) #Finner informasjon om navnet du skriver inn i "Username" feltet i index"...
            id = sql["id"] #...Trekker ut brukerens ID fra sql requesten...
            user.SetUser(id) #...og bruker ID-en til å sette all annen informasjon om brukeren. !!!!!!!!!!!!!!!!
            
            inserted_pw = form.login.password.data.encode() #fra string til byte

            inserted_pw_hash = str(hashlib.pbkdf2_hmac("sha256", inserted_pw, user.username.encode(), 100000)).replace("\\", "")
            
            correct_pw_hash = user.password
            print("Type Correct PW    : ",type(correct_pw_hash))
            print("Correct PW String  : ",correct_pw_hash.replace("\\", ""))
            print("Type Inserted PW   : ",type((inserted_pw_hash)))
            print("Inserted PW string : ", inserted_pw_hash.replace("\\", ""))
            if user == None:
                flash('Wrong username and/or password') #Vi skriver dette for ikke å røpe om den som prøver å logge seg inn har skrevet noe rett...
            elif inserted_pw_hash.replace("\\", "") == correct_pw_hash.replace("\\", ""):
            #elif user.password == form.login.password.data:
                login_user(user, remember = form.login.remember_me.data) #Dersom remember me er hooket av, vil brukeren bli remembered til neste gang


                return redirect(url_for('stream'))
            else:
                flash('Wrong username and/or password')

    elif form.register.is_submitted() and form.register.submit.data:
        if form.register.validate_on_submit():
            flash("New user registered!")
            hashed_pw = hashlib.pbkdf2_hmac("sha256", form.register.password.data.encode(), form.register.username.data.encode(), 100000)
            query_db('INSERT INTO Users (username, first_name, last_name, password) VALUES("{}", "{}", "{}", "{}");'.format(form.register.username.data, form.register.first_name.data,
            form.register.last_name.data,  str(hashed_pw).replace("\\", "")))
            return redirect(url_for('index'))
    
    return render_template('index.html', title='Welcome', form=form)

# content stream page
@app.route('/stream', methods=['GET', 'POST'])
def stream():
    if current_user.is_active:
        username = current_user.username
        form = PostForm()
        user = query_db('SELECT * FROM Users WHERE username="{}";'.format(username), one=True)
        if form.is_submitted():
            if form.validate_on_submit():
                if form.image.data:
                    path = os.path.join(app.config['UPLOAD_PATH'], form.image.data.filename)
                    form.image.data.save(path)
                query_db('INSERT INTO Posts (u_id, content, image, creation_time) VALUES({}, "{}", "{}", \'{}\');'.format(user['id'], form.content.data, form.image.data.filename, datetime.now()))
                return redirect(url_for('stream', username=username))

        posts = query_db('SELECT p.*, u.*, (SELECT COUNT(*) FROM Comments WHERE p_id=p.id) AS cc FROM Posts AS p JOIN Users AS u ON u.id=p.u_id WHERE p.u_id IN (SELECT u_id FROM Friends WHERE f_id={0}) OR p.u_id IN (SELECT f_id FROM Friends WHERE u_id={0}) OR p.u_id={0} ORDER BY p.creation_time DESC;'.format(user['id']))
        return render_template('stream.html', title='Stream', username=username, form=form, posts=posts)
    return redirect("/index")

# comment page for a given post and user.
@app.route('/comments/<username>/<int:p_id>', methods=['GET', 'POST'])
def comments(username, p_id):
    form = CommentsForm()
    if form.is_submitted():
        user = query_db('SELECT * FROM Users WHERE username="{}";'.format(username), one=True)
        query_db('INSERT INTO Comments (p_id, u_id, comment, creation_time) VALUES({}, {}, "{}", \'{}\');'.format(p_id, user['id'], form.comment.data, datetime.now()))

    post = query_db('SELECT * FROM Posts WHERE id={};'.format(p_id), one=True)
    all_comments = query_db('SELECT DISTINCT * FROM Comments AS c JOIN Users AS u ON c.u_id=u.id WHERE c.p_id={} ORDER BY c.creation_time DESC;'.format(p_id))
    return render_template('comments.html', title='Comments', username=username, form=form, post=post, comments=all_comments)

# page for seeing and adding friends
#@app.route('/friends/<username>', methods=['GET', 'POST'])
@app.route('/friends/', methods=['GET', 'POST'])
#def friends(username):
def friends():
    username = current_user.username
    form = FriendsForm()
    user = query_db('SELECT * FROM Users WHERE username="{}";'.format(username), one=True)
    if form.is_submitted():
        friend = query_db('SELECT * FROM Users WHERE username="{}";'.format(form.username.data), one=True)
        if friend is None:
            flash('Something went wrong')
        else:
            query_db('INSERT INTO Friends (u_id, f_id) VALUES({}, {});'.format(user['id'], friend['id']))
    
    all_friends = query_db('SELECT * FROM Friends AS f JOIN Users as u ON f.f_id=u.id WHERE f.u_id={} AND f.f_id!={} ;'.format(user['id'], user['id']))
    return render_template('friends.html', title='Friends', username=username, friends=all_friends, form=form)

# see and edit detailed profile information of a user
@app.route('/profile/<username>', methods=['GET', 'POST'])
@app.route('/profile', methods=['GET', 'POST'])
def profile(username = ""):
    if current_user.is_active:
        can_edit = False
        if username =="":
            can_edit = True
            username = current_user.username
        form = ProfileForm()
        if form.is_submitted():
            query_db('UPDATE Users SET education="{}", employment="{}", music="{}", movie="{}", nationality="{}", birthday=\'{}\' WHERE username="{}" ;'.format(
                form.education.data, form.employment.data, form.music.data, form.movie.data, form.nationality.data, form.birthday.data, username
            ))
            return redirect(url_for('profile', username=username, can_edit = can_edit))
        
        user = query_db('SELECT * FROM Users WHERE username="{}";'.format(username), one=True)
        return render_template('profile.html', title='profile', username=username, user=user, form=form, can_edit = can_edit)
    return redirect("/index")
