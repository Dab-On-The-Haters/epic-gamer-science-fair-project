from flask_wtf import FlaskForm
from wtforms import ValidationError
import wtforms.fields as f
import wtforms.fields.html5 as f5
import wtforms.validators as v

import db
from pickle import loads

import string
urlValidChars = string.ascii_letters + string.digits + '._-+'

# message for InputRequired
r = lambda fieldValue : 'Please enter your ' + fieldValue

w3Button = {'class': 'w3-2019-galaxy-blue w3-button w3-padding-large w3-large', 'style': 'background-color : #191970'}

from jinja2 import Template
popup = Template('''
<span class="popup" onmouseenter="document.getElementById('{{ id|escape }}-popuptext').classList.add('show');" onmouseleave="document.getElementById('{{ id|escape }}-popuptext').classList.remove('show');">
    <b>{{ label }}</b>
    <span class="popuptext" id="{{ id|escape }}-popuptext">{{ popupText|escape }}</span>
</span>''')
link = Template('''
    <br><p>On a scale of 1 to 10, {{ label }}?{% if kink %} <a href= {{ kink|escape }}> Haven't done this yet? Here's the link</a>{% endif %}</p>''')



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
                raise ValidationError('The username "{}" is taken.'.format(field.data))

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
        try:
            if db.cur.fetchone()['codeNumber'] != int(field.data):
                raise ValidationError('Incorrect verification code. Try redoing the register form if you think you might have made a typo over there.')
        except TypeError:
            raise ValidationError('This account is already verified! Go ahead and <a class="w3-button w3-2019-galaxy-blue w3-padding-large w3-hover-indigo" href="/login">log in</a>.')

    verificationCode = f.IntegerField('Verification code', [v.InputRequired(message=r('4-digit verification code. You should have received it via email. If it\'s been a while and you still haven\'t gotten it, please fill out the register form again in case you mistyped it.')), verificationCodeCheck]) 


class loginForm(FlaskForm):
    def checkLoginValidity(form, field):
        db.cur.execute('SELECT verified FROM users WHERE username=%s AND own_password=%s;', (form.username.data, field.data))
        checkIt = db.cur.fetchone()
        if (not checkIt) or (not checkIt.get('verified', 0)):
            raise ValidationError('Incorrect username or password.')
    
    username = f.StringField('Username', [v.InputRequired(r('username'))])
    password = f.PasswordField('Password', [v.InputRequired(r('password')), checkLoginValidity])

class datasetForm(FlaskForm):
    title = f.StringField('Name of this dataset', [v.InputRequired(r('dataset name')), v.length(5, 250, 'Dataset title must be between 5 and 250 characters long')])
    description = f.TextAreaField('Dataset description', [v.length(max=65500, message='Description can not be longer than 65,500 characters.')])
    files = f.FieldList(f.FileField('Custom dataset file from your computer'), max_entries=100)
    newFile = f.SubmitField('Add a new dataset file from your computer', render_kw=w3Button)
    removeFile = f.SubmitField('Remove the last dataset file entry', render_kw=w3Button)
    URLs = f.FieldList(f5.URLField('URL of dataset of file', [v.URL('Please enter a valid URL')]), max_entries=100)
    newURL = f.SubmitField('Add a new dataset URL', render_kw=w3Button)
    removeURL = f.SubmitField('Remove the last URL entry', render_kw=w3Button)
    uploadDataset = f.SubmitField('Upload the dataset', render_kw=w3Button)

#this form is from a stackoverflow answer (https://stackoverflow.com/questions/24296834/wtform-fieldlist-with-selectfield-how-do-i-render/57548509#57548509)
class SelectForm(FlaskForm):
    select = f.SelectField('Placeholder', [v.DataRequired(message='Please select a column to go into the dataset.')], choices=[])


class datasetEditorForm(FlaskForm):
    columnSelections = f.FieldList(f.FormField(SelectForm))
    finalText = f.TextAreaField('Edit your dataset to remove unwanted data', [v.length(min=1000, message='The final text cannot be shorter than 1,000 characters.')], render_kw={'rows':'20', 'cols':'100', 'placeholder':'Click \\"refresh dataset text\\"; to automatically fill out this field'})
    datasetRefresh = f.SubmitField('Refresh dataset text', render_kw=w3Button)

class modelMakerForm(FlaskForm):
    def datasetCheck(form, field):
        db.cur.execute('SELECT title FROM datasets WHERE ID=%s;', (field.data,))
        if not db.cur.fetchall():
            raise ValidationError('We couldn\'t find any datasets with that ID')
    
    userMode = f.BooleanField('Show advanced options', render_kw={"onclick: toggle;"})

    datasetID = f5.IntegerField('ID of dataset being used', [datasetCheck])
    description = f.TextAreaField('Description of this model')
    #nnType = f.SelectField('Type of RNN for this model')
    # things get real groovy after here, watch out
    layerAmount = f5.IntegerField(popup.render(id='layerAmount', label='Amount of hidden layers in this RNN', popupText='Hidden layers are layers of neurons in the neural network, which are between the input layer and the output layers. Changing this value has a drastic impact on the model\'s structure.'), [v.NumberRange(1, 250, 'Boi go for a reasonable amount of layers')], default=2)
    learningRate = f5.DecimalField(popup.render(id='learningRate', label='Learning rate for this RNN', popupText='The learning rate is basically how quickly the model will adapt to new information. Things go badly if it adapts to quickly but you don\'t want it to be lagging behind as information passes by. Slow values are good.'), [v.NumberRange(0, 1, 'We need small numbers')], places=4, default=0.002)
    rnnSize = f5.IntegerField(popup.render(id='rnnSize', label='Size of hidden layers in this RNN', popupText='This is the amount neurons (values) in each hidden layer, which has a large impact on the model\'s structure.'), [v.NumberRange(min=10, max=1000, message='There should be between 10 and 1,000 neurons. Anything else is ridiculous.')], default=128)
    # maybe add boolean field here so users don't have to say zero?
    dropout = f5.DecimalField(popup.render(id='dropout', label='Dropout for reqularization, used after each hidden layer in the RNN', popupText='Dropout is a system which disconnects certain neurons from others where weights might get messed up, meaning that some things will stop influencing the model (but usually not in noticeable ways).'), [v.NumberRange(0, 1, 'Dropout is from 0-1')], default=0.5)
    seqLength = f5.IntegerField(popup.render(id='seqLength', label='Sequence length (amount of timesteps the RNN will unroll for)', popupText='This is the amount of times that inputs are fully passed to the outputs during a forward pass through the dataset.'), [v.NumberRange(3, 250, 'Should be between 3 and 250')], default=50)
    batchSize = f5.IntegerField(popup.render(id='batchSize', label='Size of RNN batches (amount of sequences to train on in parallel)', popupText='The training data is split up into batches to be processed by Joe individually. This is the amount of characters in each batch.'), [v.NumberRange(10, 500, 'Batch size should be between 10 and 500 but really no bigger than 100')], default=50)
    maxEpochs = f5.IntegerField(popup.render(id='maxEpochs', label='Maximum amount of epochs', popupText='An epoch is when Joe goes through the entire datasets forwards and backwards. This is the amount of epochs before this model stops training.'), [v.NumberRange(3, 300, 'You gotta have between 3 and 300 epochs (they take a hella long time)')], default=50)
    seed = f5.IntegerField(popup.render(id='seed', label='Seed for making random numbers', popupText='This is the number that is used to create other random numbers. Keeping a consistent seed will mean consistent results.'), [v.NumberRange(1, 250, 'Set your seed between 1 and 250, it really doesn\'t matter')], default=123)


class sampleForm(FlaskForm):
    modelID = int()
    def primeCharCheck(form, field):
        db.cur.execute('SELECT char_file FROM models WHERE ID=%s;', (form.modelID,))
        availableChars = loads(db.cur.fetchone()['char_file'], encoding='utf-8')
        for char in field.data:
            if char not in availableChars:
                raise ValidationError('The model is currently unaware that the character "{}" exists, meaning that you can\'t use it in the priming string.'.format(char))

    checkpointID = f5.IntegerField('ID of checkpoint to sample', [v.DataRequired()])
    seed = f.TextAreaField('Text to start the generation with', [v.Length(1, 5000, 'The prompt should be at least one letter and not over 5,000.'), primeCharCheck], default='a')
    temperature = f5.DecimalRangeField('Temperature for text generation. Higher = more creative / risk taking', [v.NumberRange(0.01, 1, 'Temperature is on a scale of 0 to 1')], default=0.8, render_kw={'min':'0.01','max':'1','step':'0.01'})
    sampleLength = f5.IntegerField('Amount of characters to generate', [v.NumberRange(5, 100000, 'Between 5 and 100,000 characters should be generated.')], default=5000)
    
def q(label, kink):
    return f5.IntegerRangeField(link.render(label=label, kink=kink), [v.NumberRange(1, 10, 'Must be between 1 and 10')], render_kw={'min':'1', 'max':'10'}, default=5)

class survey(FlaskForm):
    fe = lambda s : f.TextAreaField(s if len(s) else 'How should we improve this?', [v.Length(max=50000, message='Feedback cannot be longer than 50,000 characters.')], render_kw={'class':'w3-margin-bottom'})
    
    techComfort = q('how comfortable are you with computers and technology in general', False)
    navigation = q('how hard/confusing did you find navigating the website', False)
    navigationF = fe('')
    datasets = q('how hard/confusing was uploading a dataset', '/upload-dataset')
    datasetsF = fe('')
    models = q('how hard/confusing was creating a model', '/new-model')
    modelsF = fe('')
    samples = q('how hard/confusing was generating text from the models', '/generate/4')
    samplesF = fe('')
    descriptions = q('how clear were the descriptions and explanations on the website', False)
    descriptionsF = fe('')

    generalFeedback = fe('What are some overall suggestions?')
