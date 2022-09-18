from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FormField, TextAreaField, FileField
from wtforms.fields.html5 import DateField
from wtforms.validators import InputRequired, Length, EqualTo, NoneOf

# defines all forms in the application, these will be instantiated by the template,
# and the routes.py will read the values of the fields
# TODO: Add validation, maybe use wtforms.validators??
# TODO: There was some important security feature that wtforms provides, but I don't remember what; implement it

invalidInput = ["marit", "stian", "benjamin", "jørund"]

class LoginForm(FlaskForm):
    username = StringField('Username', render_kw={'placeholder': 'Username'}, validators=[InputRequired()])
    password = PasswordField('Password', render_kw={'placeholder': 'Password'}, validators=[InputRequired()])
    remember_me = BooleanField('Remember me') # TODO: It would be nice to have this feature implemented, probably by using cookies
    submit = SubmitField('Sign In')

class RegisterForm(FlaskForm):
    first_name = StringField('First Name', render_kw={'placeholder': 'First Name'}, validators=[InputRequired(), NoneOf(invalidInput, message="Invalid input")])
    last_name = StringField('Last Name', render_kw={'placeholder': 'Last Name'}, validators=[InputRequired()])

    username = StringField('Username', render_kw={'placeholder': 'Username'}, validators=[
                           InputRequired(), Length(min=5, max=50, message="Must be between 5 and 50 characters")])
    password = PasswordField('Password', render_kw={'placeholder': 'Password'}, validators=[
                             InputRequired(), Length(min=8, max=50, message="Must be between 8 and 50 characters"), EqualTo('confirm_password', message='Passwords must match')])
    confirm_password = PasswordField('Confirm Password', render_kw={'placeholder': 'Confirm Password'}, validators=[
                                     InputRequired(), Length(min=8, max=50, message="Must be between 8 and 50 characters")])
    submit = SubmitField('Sign Up')

class IndexForm(FlaskForm):
    login = FormField(LoginForm)
    register = FormField(RegisterForm)

class PostForm(FlaskForm):
    content = TextAreaField('New Post', render_kw={'placeholder': 'What are you thinking about?'})
    image = FileField('Image')
    submit = SubmitField('Post')

class CommentsForm(FlaskForm):
    comment = TextAreaField('New Comment', render_kw={'placeholder': 'What do you have to say?'})
    submit = SubmitField('Comment')

class FriendsForm(FlaskForm):
    username = StringField('Friend\'s username', render_kw={'placeholder': 'Username'})
    submit = SubmitField('Add Friend')

class ProfileForm(FlaskForm):
    education = StringField('Education', render_kw={'placeholder': 'Highest education'})
    employment = StringField('Employment', render_kw={'placeholder': 'Current employment'})
    music = StringField('Favorite song', render_kw={'placeholder': 'Favorite song'})
    movie = StringField('Favorite movie', render_kw={'placeholder': 'Favorite movie'})
    nationality = StringField('Nationality', render_kw={'placeholder': 'Your nationality'})
    birthday = DateField('Birthday')
    submit = SubmitField('Update Profile')
