#!/usr/bin/python3
"""
Hi fellow epic gamers,
this will be the main WEB server script. it handles all the requests from the site.
It isn't the WSGI though, that'll be in a separate file, probs one located wherever on the machine
we choose to host the file on.

For the long term, please don't use this to host static files
(but it's fine temporarily)
we can do that on Apache2 more efficiently.

FLASK DOCUMENTATION IS AT https://flask.palletsprojects.com/en/1.1.x/ YOU'LL WANT IT
"""


# import all the flask stuff we'll be needing
from flask import Flask, escape, request, redirect, render_template, send_file, send_from_directory, url_for # etc...
# initialize flask as "app". this matters not just for literally everything but for the WSGI as well
app = Flask(__name__)

# login tracking stuff, I both hate and love Todd Birchard
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
loginManager = LoginManager()

#import super secure stuff (passwords stored in json)
import json
with open('/home/thomas/.private-stuff.json') as f:
    passwords = json.load(f)


#import mail stuff (pip3 install flask-mail)
from flask_mail import Mail, Message
mail = Mail(app)
# configure it to work with thse
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'joethernn@gmail.com'
app.config['MAIL_PASSWORD'] = passwords['JOE_MAIL_PASSWORD']
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

# OH MY GOSH YES
import io

# code with new db model begins here
import db

# start login manager
loginManager.init_app(app)
loginManager.login_view = '/login'

# dumb classes just for flask-login
class User():
    username = str()
    name = str()
    ID = int()
    email = str()
    is_anonymous = False # duh
    is_authenticated = True
    is_active = True

    def setValues(self, fieldName, fieldRequest):
        db.cur.execute('SELECT verified, ID, username, email_addr, real_name, self_description FROM users WHERE '+fieldName+'=%s;', (fieldRequest,))
        if db.cur.rowcount:
            self.is_anonymous = False
            
            QA = db.cur.fetchone()
            self.is_active = QA['verified']
            self.is_authenticated = QA['verified']
            self.ID = QA['ID']
            self.username = QA['username']
            self.email = QA['email_addr']
            self.name = QA['real_name']
            self.description = QA['self_description']
        else:
            self.ID = 0 # wow i'm such a good person
            self.is_anonymous = True
            self.is_authenticated = False
            self.is_active = False
            self.username = ''
            self.name = 'Anonymous User'

    def get_id(self):
        return str(self.ID).encode('utf-8')


    def get_id(self):
        return str(self.ID).encode('utf-8')

@loginManager.user_loader
def load_user(ID):
    user = User()
    if type(ID)==str and ID.startswith('b'):
        ID = ID.split("'")[1]
    user.setValues('ID', int(ID))
    return user


#WTForm stuff
from flask_wtf import FlaskForm
from wtforms import ValidationError
import wtforms.fields as f
import wtforms.fields.html5 as f5
import wtforms.validators as v

import string

import subprocess as subp

# for reading datasets as they're uploaded
import csv

urlValidChars = string.ascii_letters + string.digits + '._-+'

# message for InputRequired
r = lambda fieldValue : 'Please enter your ' + fieldValue

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
                raise ValidationError('An account with that email address is already verified')
    # for checking if username is wack or taken
    def usernameStuffCheck(form, field):
        db.cur.execute('SELECT verified FROM users WHERE username=%s;', (field.data,))
        for verification in db.cur.fetchall():
            if verification['verified']:
                raise ValidationError('The username "'+field.data+'" is taken')

        for char in field.data:
            if char not in urlValidChars:
                raise ValidationError('Usernames can only contain letters, numbers, and the symbols . _ - +')

    email = f5.EmailField('Email address', [v.InputRequired(r('email address')), v.Email('Must be a valid email address'), v.Length(5, 250, 'Must be a complete email address'), emailTakenCheck])
    name = f.StringField('Name', [v.InputRequired(r('name')), v.Length(2, 250, r('name'))])
    username = f.StringField('Username', [v.InputRequired(r('username')), v.Length(5, 250, 'Username must be between 5 and 250 characters long'), usernameStuffCheck])
    password = f.PasswordField('Password', [v.InputRequired(r('password')), v.Length(8, 250, 'Password must be at least 8 characters long'), PasswordCheck])
    confirm = f.PasswordField('Confirm password', [v.InputRequired(r('password confirmation')), v.EqualTo('password', 'Confirmation password does not match')])


class verifyForm(FlaskForm):
    verifyAccountID = int()
    def verificationCodeCheck(form, field):
        db.cur.execute('SELECT codeNumber FROM verification_codes WHERE accountID=%s;', (form.verifyAccountID,))
        codeNumber = db.cur.fetchone()
        if codeNumber['codeNumber'] != int(field.data):
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
    files = f.FieldList(f.FileField('Custom dataset file'), max_entries=100)
    newFile = f.SubmitField('Add a new dataset file')
    removeFile = f.SubmitField('Remove the last dataset file')
    URLs = f.FieldList(f5.URLField('URL of dataset of file', [v.InputRequired(urlm), v.URL(urlm)]), max_entries=100)
    newURL = f.SubmitField('Add a new dataset URL')
    removeURL = f.SubmitField('Remove the last URL')
    uploadDataset = f.SubmitField('Upload the dataset')

#this form is from a stackoverflow answer (https://stackoverflow.com/questions/24296834/wtform-fieldlist-with-selectfield-how-do-i-render/57548509#57548509)
class SelectForm(FlaskForm):
    select = f.SelectField('Placeholder', choices=[])


class datasetEditorForm(FlaskForm):
    columnSelections = f.FieldList(f.FormField(SelectForm))
    finalText = f.TextAreaField('Edit your dataset to remove unwanted data', [v.length(min=1000, message='The final text cannot be shorter than 1,000 characters.')])

class modelMakerForm(FlaskForm):
    def datasetCheck(form, field):
        db.cur.execute('SELECT title FROM datasets WHERE ID=%s;', (field.data,))
        if not db.cur.fetchall():
            raise ValidationError('We couldn\'t find any models with that ID')



    datasetID = f5.IntegerField('ID of dataset being used', [datasetCheck])
    description = f.TextAreaField('Description of this model')
    #nnType = f.SelectField('Type of RNN for this model')
    nlpOptions = f.BooleanField('Settings for NLP')
    # things get real groovy after here, watch out
    layerAmount = f5.IntegerField('Amount of layers in this RNN', [v.NumberRange(1, 250, 'Boi go for a reasonable amount of layers')], default=2)
    learningRate = f5.DecimalField('Learning rate for this RNN', [v.NumberRange(0, 1, 'We need small numbers')], default=0.002)
    learningRateDecay = f5.DecimalField('Learning rate decay for this RNN', [v.NumberRange(0, 1, 'Should be almost at one, not more or less')], default=0.97)
    learningRateDecayAfter = f5.IntegerField('Amount of epochs before the learning rate starts decaying', [v.NumberRange(1, 250, 'Between 1 and 250 epochs guys they are full passes')], default=10)
    decayRate = f5.DecimalField('Decay rate for the optimizer', [v.NumberRange(0, 1, 'Needs to be close to one')], default=0.95)
    # maybe add boolean field here so users don't have to say zero?
    dropout = f5.DecimalField('Dropout for reqularization, used after each hidden layer in the RNN', [v.NumberRange(0, 1, 'Dropout is from 0-1')], default=0)
    seqLength = f5.IntegerField('Sequence length (amount of timesteps the RNN will unroll for)', [v.NumberRange(1, 250, 'No clue what this is but OK')], default=50)
    batchSize = f5.IntegerField('Size of RNN batches (amount of sequences to train on in parallel)', [v.NumberRange(10, 500, 'Batch size should be between 10 and 500 but really no bigger than 100')], default=50)
    maxEpochs = f5.IntegerField('Maximum amount of epochs', [v.NumberRange(3, 300, 'You gotta have between 3 and 300 epochs (they take a hella long time)')], default=50)
    gradClip = f5.DecimalField('Value to clip gradients at', [v.NumberRange(1, 100, 'IDK what this should be but that seems ridiculous')], default=5)
    valFrac = f5.DecimalField('Amount of data going into the validation set', [v.NumberRange(0, 1, 'BETWEEN 0 AND 1 FIGURE IT OUT')], default=0.05)
    trainFrac = f5.DecimalField('Amount data going into the training set', [v.NumberRange(0, 1, 'BETWEEN 0 AND 1 FIGURE IT OUT')], default=0.95)
    seed = f5.IntegerField('Seed for making random numbers', [v.NumberRange(1, 250, 'Set your seed between 1 and 250, it really doesn\'t matter')], default=123)


import urllib3
http = urllib3.PoolManager()


@app.route('/')
def welcome():
    return render_template('homepage.html', user=current_user)


@app.route('/teach')
@login_required
def teachTeach():
    return render_template('teach.html', user=current_user)


@app.route('/upload-dataset', methods=['GET', 'POST'])
@login_required
def newDataset():
    DF = datasetForm()

    if DF.is_submitted():
        if DF.uploadDataset.data and DF.validate():
            db.cur.execute('INSERT INTO datasets (title,  user_description, posterID) VALUES (%s, %s, %s);',
            (DF.title.data, DF.description.data, current_user.ID))
            db.conn.commit()
            datasetID = db.cur.lastrowid
            # moved from post-validation to pre and back to post again lol
            files = dict()
            
            # get local uploaded files
            for FN, data in request.files.items():
                files[data.filename] = data.read()
            
            # get file links from urllib3
            for URL in DF.URLs.data:
                req = http.request('GET', URL)
                if req.status == 200:
                    files[URL] = req.data
            
            columnLists = dict()
            for FN in files:
                # tidy up file and put it into db
                files[FN] = files[FN].decode('utf-8')
                db.cur.execute('INSERT INTO datafiles (file_name, file_data, datasetID) VALUES (%s, %s, %s);', (FN, files[FN], datasetID))
                
                # if it's a csv add it to column selections
                splitFN = FN.split('.')
                if len(splitFN) > 1:
                    if splitFN[-1] == 'csv':
                        columnLists[splitFN[0]] = csv.DictReader(io.StringIO(files[FN], newline='')).fieldnames
                    else: continue
                else: continue
                
            db.conn.commit()
            return redirect(url_for('.datasetEditor', ID=datasetID, columnLists=json.dumps(columnLists).replace(' ', '')))
        try: # do other submitted operations
            if DF.newURL.data: DF.URLs.append_entry()
            elif DF.newFile.data: DF.files.append_entry()
            elif DF.removeURL.data: DF.URLs.pop_entry()
            elif DF.removeFile.data: DF.files.pop_entry()
        except: pass

    return render_template('new-dataset.html', form=DF)

 
@app.route('/edit-dataset', methods=['GET', 'POST'])
@login_required
def datasetEditor():
    
    datasetIDF = (int(request.args.get('ID', 0)),)
    # check if user has permissions to edit dataset

    db.cur.execute('SELECT title, posterID from datasets WHERE ID=%s;', datasetIDF)
    TS = db.cur.fetchone()
    if not TS.get('title', False):
        return 'lol we can\'t find that dataset'
    
    if TS['posterID'] != current_user.ID:
        return 'you don\'t have permission to edit that dataset'

    EF = datasetEditorForm()

    #db.cur.execute('SELECT title, final_text FROM datasets WHERE ID=%s;', datasetIDF)
    #TS = db.cur.fetchone()
    """
    if EF.validate_on_submit():
        # set dataset final text
        db.cur.execute('UPDATE datasets SET final_text = %s WHERE ID = %s;', (EF.finalText.data, request.args['ID']))
        db.conn.commit()
        return redirect(url_for('.modelMaker', dataset=request.args['ID']))"""
    
    columnInquiries = json.loads(request.args.get('columnLists', '{}'))
    
    # add in selections to the form
    selectEntries = []
    for FN in columnInquiries:
        newEntry = SelectForm()
        newEntry.select.label = FN
        newEntry.select.id = FN
        newEntry.id = FN
        newEntry.select.validators = [v.DataRequired(message='Please select a column to go into the dataset.')]

        choices = []
        for choice in columnInquiries[FN]:
            choices.append((choice, choice))
        newEntry.select.choices = choices

        selectEntries.append(newEntry)
    EF.columnSelections = selectEntries

    # if finaltext isn't filled out
    if (not EF.finalText.data) or len(EF.finalText.data) < 1000:
        # deal with adding in text files
        db.cur.execute('SELECT file_data FROM datafiles WHERE datasetID = %s AND file_name NOT LIKE "%.csv";', datasetIDF)
        defaultTexts = []
        for result in db.cur.fetchall():
            defaultTexts.append(result['file_data'].decode('utf-8'))

        # if column selections are entered / submitted...
        if not EF.columnSelections[-1].errors:
            # get dataset's CSVs and check them against column selections, select and add in column data
            db.cur.execute('SELECT file_name, file_data FROM datafiles WHERE datasetID = %s AND file_name LIKE "%.csv";', datasetIDF)
            results = db.cur.fetchall()
            for result in results:
                CSVreader = csv.DictReader(io.StringIO(result['file_data'].decode('utf-8'), newline=''))
                for entry in EF.columnSelections:
                    if entry.id == result['file_name']:
                        correctColumn = entry.select.data
                        CSVtexts = []
                        for row in CSVreader:
                            CSVtexts.append(row[correctColumn])
                        defaultTexts.append('\n\n'.join(CSVtexts))
           
        EF.finalText.data = '\n\n\n\n'.join(defaultTexts)
    #EF.finalText.data = 'pee pee poo poo'
    return render_template('dataset-editor.html', datasetName=TS['title'], form=EF, user=current_user)


@app.route('/new-model', methods=['GET', 'POST'])
@login_required
def modelMaker():
    MF = modelMakerForm()

    if MF.validate_on_submit():
        db.cur.execute('''INSERT INTO models
            (datasetID, trainerID, user_description, seed,
            num_layers, learning_rate, learning_rate_decay, dropout, seq_length, batch_size, max_epochs, grad_clip, train_frac, val_frac
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);''',
            (MF.datasetID.data, current_user.ID, MF.description.data, MF.seed.data,
            MF.layerAmount.data, MF.learningRate.data, MF.learningRateDecay.data, MF.dropout.data, MF.seqLength.data, MF.batchSize.data, MF.maxEpochs.data, MF.gradClip.data, MF.trainFrac.data, MF.valFrac.data))
        db.conn.commit()
        subp.Popen(['python3', 'train.py', str(db.cur.lastrowid)], cwd='rnn')
        return ('we just friccin died OK')
    if not MF.datasetID.data:
        try: MF.datasetID.data = int(request.args['dataset'])
        except: pass
    return render_template('model-maker.html', form=MF)

@app.route('/exploremodels', methods=['GET', 'POST'])
@login_required
def exploreModels():
    return render_template('explore/models.html')


@app.route('/about')
def aboutPage():
    return render_template('about-index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(request.args.get('next', '/'))

    LF = loginForm()

    if LF.validate_on_submit():
        user = User()
        user.setValues('username', LF.username.data)
        login_user(user, remember=True)
        
        return redirect(request.args.get('next', '/'))
    
    return render_template('login.html', form=LF)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(request.args.get('next', '/'))



@app.route('/verify/<int:ID>', methods=['GET', 'POST'])
def verifyUser(ID):
    VF = verifyForm()
    VF.verifyAccountID = ID

    if VF.validate_on_submit():
        # verify the user in the DB
        db.cur.execute('UPDATE users SET verified=1 WHERE ID=%s;', (ID,))
        # delete the verification code, we don't need it anymore
        db.cur.execute('DELETE FROM verification_codes WHERE accountID=%s;', (ID,))
        db.conn.commit()

        user = User()
        user.setValues('ID', ID)
        login_user(user, remember=True)

        return redirect('/')
    
    return render_template('verify-email.html', form=VF)



# for generating verification codes
from random import randint

# message for verifying email
verifyMsg = Message('Verify your email to talk to Joe!', sender='joethernn@gmail.com')

@app.route('/register', methods=['GET', 'POST'])
def registerUser():
    RF = registerForm()
    if RF.validate_on_submit():
        
        # add the user to DB
        db.cur.execute('INSERT INTO users (email_addr, own_password, username, real_name) VALUES (%s, %s, %s, %s);',
            (RF.email.data, RF.password.data, RF.username.data, RF.name.data))
        db.conn.commit()

        # get the user's ID
        db.cur.execute('SELECT ID FROM users WHERE email_addr=%s;', (RF.email.data,))
        accountID = db.cur.fetchone()
        accountID = accountID['ID']

        #add the verification code to DB
        verificationCode = randint(1000,9999)
        db.cur.execute('INSERT INTO verification_codes (codeNumber, accountID) VALUES (%s, %s);',
            (verificationCode, accountID))
        db.conn.commit()

        # send the verification message
        verifyMsg.recipients = [RF.email.data]
        verifyMsg.body = 'Hi '+RF.name.data+', use the code '+str(verificationCode)+' to verify your email address and get your account with Joe up and running.\nIf you don\'t know about the amazing Joe project, then just ignore this email. Thanks!'
        with app.app_context(): mail.send(verifyMsg)

        return redirect('/verify/'+str(accountID))

    return render_template('register.html', form=RF)
