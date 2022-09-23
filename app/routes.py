from flask import Flask, render_template, flash, redirect, url_for, request
from app import app, query_db, load_user, login_manager, User
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from app.forms import IndexForm, PostForm, FriendsForm, ProfileForm, CommentsForm
from datetime import datetime
import os
import rsa
import zlib

#############################
from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, SubmitField, TextAreaField, IntegerField, BooleanField, RadioField)
from wtforms.validators import InputRequired, Length

# this file contains all the different routes, and the logic for communicating with the database

@app.route('/logout') #Denne routen blir kalt når du trykker på logout knappen
def logout():
    logout_user() # Vi logger ut bruker...
    return redirect("/index") #... og sender bruker til startsiden

# home page/login/registration
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = IndexForm()
    
    if form.login.is_submitted() and form.login.submit.data:
        if not form.login.validate_on_submit():
            user = User() # Creates an empty user
            sql = query_db('SELECT * FROM Users WHERE username="{}";'.format(form.login.username.data), one=True) #Finner informasjon om navnet du skriver inn i "Username" feltet i index"...
            id = sql["id"] # Pulls out the user´s ID from the SQL request...
            user.SetUser(id) #...and uses the ID to set all attributes of the user
            if user == None:
                flash('Wrong username and/or password') # Written like this to not give away any clues to the user trying to log in if they wrote something correctly...
            elif user.password == form.login.password.data:
                login_user(user, remember = form.login.remember_me.data) # If "Remember me" is checked, the user will be remembered the next time.
                return redirect(url_for('stream'))
            else:
                flash('Wrong username and/or password')

    elif form.register.is_submitted() and form.register.submit.data:
        if form.register.validate_on_submit():
            flash("New user registered!")
            query_db('INSERT INTO Users (username, first_name, last_name, password) VALUES("{}", "{}", "{}", "{}");'.format(form.register.username.data, form.register.first_name.data,
            form.register.last_name.data, form.register.password.data))
            print(form.register.username.data)
            print(form.register.password.data)
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
        if friend is None: # Flash under was 'User does not exist', this can reveal which usernames do not exit (and therefore, which ones do...)
            flash('User does not exist')
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