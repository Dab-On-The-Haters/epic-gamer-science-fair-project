from flask_wtf import FlaskForm
from wtforms import ValidationError
import wtforms.fields as f
import wtforms.fields.html5 as f5
import wtforms.validators as v

import db

import string
urlValidChars = string.ascii_letters + string.digits + '._-+'

# message for InputRequired
r = lambda fieldValue : 'Please enter your ' + fieldValue

w3Button = {'class': 'w3-2019-galaxy-blue w3-button w3-padding-large w3-hide-small', 'style': 'background-color : #191970'}

class registerForm(FlaskForm):
    # for checking if password is varied enough
    def PasswordCheck(form, field):
        pswSet = set(field.data)
        if not (pswSet.intersection(set(string.digits)) and pswSet.intersection(set(string.ascii_uppercase)) and pswSet.intersection(set(string.ascii_lowercase))):
            raise ValidationError('Password is not varied enough. Try mixing cases and adding numbers.')
    # for checking if email is taken
    def emailTakenCheck(form, field):
        db.cur.execute('SELECT verified FROM users WHERE email_addr=%s;', (field.data,))
        for verification in db.cur.fetchall():
            if verification['verified']:
                raise ValidationError('An account with that email address has already been verified.')
    # for checking if username is wack or taken
    def usernameStuffCheck(form, field):
        db.cur.execute('SELECT verified FROM users WHERE username=%s;', (field.data,))
        for verification in db.cur.fetchall():
            if verification['verified']:
                raise ValidationError('The username "'+field.data+'" is taken.')

        for char in field.data:
            if char not in urlValidChars:
                raise ValidationError('Usernames can only contain letters, numbers, and the symbols . _ - +')

    email = f5.EmailField('Email address', [v.InputRequired(r('email address')), v.Email('Must be a valid email address'), v.Length(5, 250, 'Must be a complete email address'), emailTakenCheck])
    name = f.StringField('Name', [v.InputRequired(r('name')), v.Length(2, 250, r('name'))])
    username = f.StringField('Username', [v.InputRequired(r('username')), v.Length(3, 100, 'Username must be between 3 and 100 characters long'), usernameStuffCheck])
    password = f.PasswordField('Password', [v.InputRequired(r('password')), v.Length(8, 250, 'Password must be at least 8 characters long'), PasswordCheck])
    confirm = f.PasswordField('Confirm password', [v.InputRequired(r('password confirmation')), v.EqualTo('password', 'Confirmation password does not match')])


class verifyForm(FlaskForm):
    verifyAccountID = int()
    def verificationCodeCheck(form, field):
        db.cur.execute('SELECT codeNumber FROM verification_codes WHERE accountID=%s;', (form.verifyAccountID,))
        if db.cur.fetchone()['codeNumber'] != int(field.data):
            raise ValidationError('Incorrect verification code. Try redoing the register form if you think you might have made a typo over there.')
    
    verificationCode = f.IntegerField('Verification code', [v.InputRequired(message=r("4-digit verification code. You should have received it via email. If it's been a while and you still haven't gotten it, please fill out the register form again in case you mistyped it.")), verificationCodeCheck]) 


class loginForm(FlaskForm):
    def checkLoginValidity(form, field):
        db.cur.execute('SELECT verified FROM users WHERE username=%s AND own_password=%s;', (form.username.data, field.data))
        checkIt = db.cur.fetchone()
        if (not checkIt) or (not checkIt.get('verified', 0)):
            raise ValidationError('Incorrect username or password.')
    
    username = f.StringField('Username', [v.InputRequired(r('username'))])
    password = f.PasswordField('Password', [v.InputRequired(r('password')), checkLoginValidity])

urlm = 'Please enter a valid URL'
class datasetForm(FlaskForm):
    title = f.StringField('Name of this dataset', [v.InputRequired(r('dataset name')), v.length(5, 250, 'Dataset title must be between 5 and 250 characters long')])
    description = f.TextAreaField('Dataset description', [v.length(max=65500, message='Description can not be longer than 65,500 characters.')])
    files = f.FieldList(f.FileField('Custom dataset file from your computer'), max_entries=100)
    newFile = f.SubmitField('Add a new dataset file from your computer', render_kw=w3Button)
    removeFile = f.SubmitField('Remove the last dataset file entry', render_kw=w3Button)
    URLs = f.FieldList(f5.URLField('URL of dataset of file', [v.InputRequired(urlm), v.URL(urlm)]), max_entries=100)
    newURL = f.SubmitField('Add a new dataset URL', render_kw=w3Button)
    removeURL = f.SubmitField('Remove the last URL entry', render_kw=w3Button)
    uploadDataset = f.SubmitField('Upload the dataset', render_kw=w3Button)

#this form is from a stackoverflow answer (https://stackoverflow.com/questions/24296834/wtform-fieldlist-with-selectfield-how-do-i-render/57548509#57548509)
class SelectForm(FlaskForm):
    select = f.SelectField('Placeholder', [v.DataRequired(message='Please select a column to go into the dataset.')], choices=[])


class datasetEditorForm(FlaskForm):
    columnSelections = f.FieldList(f.FormField(SelectForm))
    finalText = f.TextAreaField('Edit your dataset to remove unwanted data', [v.length(min=1000, message='The final text cannot be shorter than 1,000 characters.')], render_kw={'rows':'20', 'cols':'40', 'placeholder':'Click "refresh dataset text" to automatically fill out this field'})
    datasetRefresh = f.SubmitField('Refresh dataset text', render_kw=w3Button)

class modelMakerForm(FlaskForm):
    def datasetCheck(form, field):
        db.cur.execute('SELECT title FROM datasets WHERE ID=%s;', (field.data,))
        if not db.cur.fetchall():
            raise ValidationError('We couldn\'t find any datasets with that ID')



    datasetID = f5.IntegerField('ID of dataset being used', [datasetCheck])
    description = f.TextAreaField('Description of this model')
    #nnType = f.SelectField('Type of RNN for this model')
    # things get real groovy after here, watch out
    layerAmount = f5.IntegerField('Amount of hidden layers in this RNN', [v.NumberRange(1, 250, 'Boi go for a reasonable amount of layers')], default=2)
    learningRate = f5.DecimalField('Learning rate for this RNN', [v.NumberRange(0, 1, 'We need small numbers')], places=4, default=0.002)
    rnnSize = f5.IntegerField('Size of hidden layers in this RNN', [v.NumberRange(min=10, max=1000, message='There should be between 10 and 1,000 neurons. Anything else is ridiculous.')], default=128)
    # maybe add boolean field here so users don't have to say zero?
    dropout = f5.DecimalField('Dropout for reqularization, used after each hidden layer in the RNN', [v.NumberRange(0, 1, 'Dropout is from 0-1')], default=0.5)
    seqLength = f5.IntegerField('Sequence length (amount of timesteps the RNN will unroll for)', [v.NumberRange(1, 250, 'No clue what this is but OK')], default=50)
    batchSize = f5.IntegerField('Size of RNN batches (amount of sequences to train on in parallel)', [v.NumberRange(10, 500, 'Batch size should be between 10 and 500 but really no bigger than 100')], default=50)
    maxEpochs = f5.IntegerField('Maximum amount of epochs', [v.NumberRange(3, 300, 'You gotta have between 3 and 300 epochs (they take a hella long time)')], default=50)
    seed = f5.IntegerField('Seed for making random numbers', [v.NumberRange(1, 250, 'Set your seed between 1 and 250, it really doesn\'t matter')], default=123)


class sampleForm(FlaskForm):
    checkpointID = f5.IntegerField('ID of checkpoint to sample', [v.DataRequired()])
    seed = f.TextAreaField('Text to start the generation with', [v.Length(1, 5000, 'The prompt should be at least one letter and not over 5,000.')], default='a')
    temperature = f5.DecimalRangeField('Temperature for text generation. Higher = more creative / risk taking', [v.NumberRange(0.01, 1, 'Temperature is on a scale of 0 to 1')], default=0.8, render_kw={'min':'0.01','max':'1','step':'0.01'})
    sampleLength = f5.IntegerField('Amount of characters to generate', [v.NumberRange(5, 100000, 'Between 5 and 100,000 characters should be generated.')], default=5000)
    

class survey(FlaskForm):
    fe = lambda s : f.TextAreaField(s if len(s) else 'How should we improve this?', [v.Length(max=50000, message='Feedback cannot be longer than 50,000 characters.')], render_kw={'class':'w3-margin-bottom'})
    q = lambda s : f5.IntegerRangeField('On a scale of 1 to 10, '+s+'?', [v.NumberRange(1, 10, 'Must be between 1 and 10')], render_kw={'min':'1', 'max':'10'}, default=5)

    techComfort = q('how comfortable are you with computers and technology in general')
    navigation = q('how hard/confusing did you find navigating the website')
    navigationF = fe('')
    datasets = q('how hard/confusing was uploading a dataset')
    datasetsF = fe('')
    models = q('how hard/confusing was creating a model')
    modelsF = fe('')
    samples = q('how hard/confusing was generating text from the models')
    samplesF = fe('')
    descriptions = q('how clear were the descriptions and explanations on the website')
    descriptionsF = fe('')

    generalFeedback = fe('What are some overall suggestions?')


