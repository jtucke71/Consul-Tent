from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, RadioField
from wtforms.validators import Length, Regexp, DataRequired, EqualTo, Email
from wtforms import ValidationError
from models import User
from database import db


class RegisterForm(FlaskForm):
    class Meta:
        csrf = False

    firstname = StringField('First Name', validators=[Length(1, 10)])

    lastname = StringField('Last Name', validators=[Length(1, 20)])

    username = StringField('Username', validators=[Length(1, 20)])

    email = StringField('Email', [
        Email(message='Not a valid email address.'),
        DataRequired()])

    password = PasswordField('Password', [
        DataRequired(message="Please enter a password."),
        EqualTo('confirmPassword', message='Passwords must match')
    ])

    confirmPassword = PasswordField('Confirm Password', validators=[
        Length(min=6, max=10)
    ])
    submit = SubmitField('Submit')

    def validate_username(self, field):
        if db.session.query(User).filter_by(username=field.data).count() != 0:
            raise ValidationError('Username already in use.')

    def validate_email(self, field):
        if db.session.query(User).filter_by(email=field.data).count() != 0:
            raise ValidationError('Email already in use.')


class LoginForm(FlaskForm):
    class Meta:
        csrf = False

    email = StringField('Email', [
        Email(message='Not a valid email address.'),
        DataRequired()])

    password = PasswordField('Password', [
        DataRequired(message="Please enter a password.")])

    submit = SubmitField('Submit')

    def validate_email(self, field):
        if db.session.query(User).filter_by(email=field.data).count() == 0:
            raise ValidationError('Incorrect username or password.')

class CommentForm(FlaskForm):
    class Meta:
        csrf = False

    comment = TextAreaField('Type your reply here:',validators=[Length(min=1)])

    submit = SubmitField('Reply')

class VoteForm(FlaskForm):
    class Meta:
        csrf = False

    vote = RadioField('Vote Post', choices=['upvote', 'downvote'])

    submit = SubmitField('Vote')

class FilterForm(FlaskForm):
    class Meta:
        csrf = False

    attribute = SelectField('Sort Posts', choices=['Best', 'New', 'Worst', 'Old'])

    submit = SubmitField('Sort')

class FavoriteForm(FlaskForm):
    class Meta:
        csrf = False

    submit = SubmitField('Favorite Post')

class UnfavoriteForm(FlaskForm):
    class Meta:
        csrf = False

    submit = SubmitField('Unfavorite Post')

class TopicForm(FlaskForm):
    class Meta:
        csrf = False

    genre = SelectField('Topics', choices=['All', 'General', 'Computers', 'Math', 'Science', 'Nature', 'Entertainment', 'Gaming', 'School', 'Art', 'Music', 'Work', 'Sports'])

    submit = SubmitField('Filter')

class NameForm(FlaskForm):
    class Meta:
        csrf = False

    firstname = StringField('First Name', validators=[Length(1, 10)])

    submit = SubmitField('Change')
