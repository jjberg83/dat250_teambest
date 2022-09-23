from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FormField, TextAreaField, FileField
from wtforms.fields.html5 import DateField
from wtforms.validators import InputRequired, Length, EqualTo, NoneOf, DataRequired
from flask_wtf.recaptcha.fields import RecaptchaField
# defines all forms in the application, these will be instantiated by the template,
# and the routes.py will read the values of the fields
# TODO: Add validation, maybe use wtforms.validators??
# TODO: There was some important security feature that wtforms provides, but I don't remember what; implement it

invalidInput = ["105 OR 1=1", "name'; DELETE FROM items; --"]

class LoginForm(FlaskForm):
    username = StringField('Username', render_kw={'placeholder': 'Username'}
    , validators=[DataRequired(), NoneOf(invalidInput, message='Wrong username')]) # Redigert. -stian
    password = PasswordField('Password', render_kw={'placeholder': 'Password'}
    , validators=[DataRequired(), NoneOf(invalidInput, message='Wrong password')]) # redigert. -stian

    remember_me = BooleanField('Remember me') # TODO: It would be nice to have this feature implemented, probably by using cookies
    recaptcha = RecaptchaField()
    submit = SubmitField('Sign In')

class RegisterForm(FlaskForm):
    # La til min og maks lengde på fornavn under: -stian
    first_name = StringField('First Name', render_kw={'placeholder': 'First Name'}, validators=[DataRequired()
    , Length(min = 1, max = 20, message = 'Too many characters'), NoneOf(invalidInput, message="Invalid input")]) # redigert -stian
    # La til min og maks lengde på efternamn under: -stian
    last_name = StringField('Last Name', render_kw={'placeholder': 'Last Name'}, validators=[DataRequired()
    , Length(min = 1, max = 20, message = 'Too many characters')]) # redigert -stian

    username = StringField('Username', render_kw={'placeholder': 'Username'}, validators=[
                           DataRequired(), Length(min=5, max=50, message="Must be between 5 and 50 characters"), NoneOf(invalidInput, message="Invalid input")])
    password = PasswordField('Password', render_kw={'placeholder': 'Password'}, validators=[
                             DataRequired(), Length(min=8, max=50, message="Must be between 8 and 50 characters"), NoneOf(invalidInput, message="Invalid input"), EqualTo('confirm_password', message='Passwords must match')])
    confirm_password = PasswordField('Confirm Password', render_kw={'placeholder': 'Confirm Password'}, validators=[
                                     DataRequired(), Length(min=8, max=50, message="Must be between 8 and 50 characters"), NoneOf(invalidInput, message="Invalid input")])
    recaptcha = RecaptchaField()
    submit = SubmitField('Sign Up')

class IndexForm(FlaskForm):
    login = FormField(LoginForm)
    register = FormField(RegisterForm)
    #recaptcha = RecaptchaField()

class PostForm(FlaskForm):
    content = TextAreaField('New Post', render_kw={'placeholder': 'What are you thinking about?'}
    , validators=[Length(min = 1, max = 1000, message="Message must be between 1 and 1000 charakters")])
    # ^ Max length on a post. -stian
    image = FileField('Image')
    submit = SubmitField('Post')

class CommentsForm(FlaskForm):
    comment = TextAreaField('New Comment', render_kw={'placeholder': 'What do you have to say?'}
    , validators=[Length(min = 1, max = 500, message='Comment must be between 1 and 500 charakters')])
    # ^ Max length on a comment. -stian
    submit = SubmitField('Comment')

class FriendsForm(FlaskForm):
    username = StringField('Friend\'s username', render_kw={'placeholder': 'Username'})
    submit = SubmitField('Add Friend')

class ProfileForm(FlaskForm):
    # Legger til maks lengde under -stian

    education = StringField('Education', render_kw={'placeholder': 'Highest education'}, validators=[DataRequired(), Length(min=1,max=50, message='Must be between 1 and 50 charakters')])
    employment = StringField('Employment', render_kw={'placeholder': 'Current employment'}, validators = [DataRequired(), Length(min = 1, max = 50, message='Must be between 1 and 50 charakters')])
    music = StringField('Favorite song', render_kw={'placeholder': 'Favorite song'}, validators = [DataRequired(), Length(min = 1, max = 50, message='Must be between 1 and 50 charakters')])
    movie = StringField('Favorite movie', render_kw={'placeholder': 'Favorite movie'}, validators = [DataRequired(), Length(min = 1, max = 50, message='Must be between 1 and 50 charakters')])
    nationality = StringField('Nationality', render_kw={'placeholder': 'Your nationality'}, validators = [DataRequired(), Length(min = 1, max = 50, message='Must be between 1 and 50 charakters')])

    birthday = DateField('Birthday')
    submit = SubmitField('Update Profile')
