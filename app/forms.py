from flask_wtf import Form
from wtforms.fields import StringField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length
from models import User

class EmailForm(Form):
    email = StringField('email', validators= [DataRequired()])

class EditForm(Form):
    nickname = StringField('nickname', validators = [DataRequired()])
    about_me = TextAreaField('about_me', validators = [Length(min=0, max=140)])

    def __init__(self, original_nickname, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.original_nickname = original_nickname

    def validate(self):
        if not Form.validate(self): #Normal flask's built in check.
            return False
        if self.nickname.data == self.original_nickname: #If it's just the same, no worries
            return True
        user = User.query.filter_by(nickname=self.nickname.data).first() #Check database now for
        #the nickname guy wants
        if user != None: #If result returns non-none, already in use.
            self.nickname.errors.append('This nickname is already in use. Please choose another one.')
            return False
        return True

class PostForm(Form):
    post = StringField('post', validators=[DataRequired()])