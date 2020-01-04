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
from flask import Flask, request, redirect, render_template, session, jsonify # etc...
# initialize flask as "app". this matters not just for literally everything but for the WSGI as well
app = Flask(__name__)

# login tracking stuff, I both hate and love Todd Birchard
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
loginManager = LoginManager()

#import super secure stuff (passwords stored in json)
import json
with open('/home/thomas/.private-stuff.json') as f:
    passwords = json.load(f)

import forms as f

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

    """
    username = str()
    name = str()
    ID = int()
    email = str()
    is_anonymous = True # duh
    is_authenticated = False
    is_active = False
    """

    def __init__ (self, fieldName, fieldRequest, authenticated):
        db.cur.execute('SELECT verified, ID, username, email_addr, real_name, self_description FROM users WHERE '+fieldName+'=%s;', (fieldRequest,))
        if db.cur.rowcount:
            self.is_anonymous = False
            
            QA = db.cur.fetchone()
            self.is_active = QA['verified']
            self.is_authenticated = authenticated
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
            self.email = ''
            self.name = 'Anonymous User'
    
    def get_id(self):
        return str(self.ID).encode('utf-8')


@loginManager.user_loader
def load_user(ID):
    if type(ID)==str and ID.startswith('b'):
        ID = ID.split("'")[1]
    return User('ID', int(ID), True)

import subprocess as subp

# for reading datasets as they're uploaded
import csv

# for downloading dataset files
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
    DF = f.datasetForm()

    if DF.is_submitted():
        if DF.uploadDataset.data and DF.validate():
            db.cur.execute('INSERT INTO datasets (title,  user_description, posterID) VALUES (%s, %s, %s);',
            (DF.title.data, DF.description.data, current_user.ID))
            db.conn.commit()
            datasetID = db.cur.lastrowid
            session['datasetID'] = datasetID
            # moved from post-validation to pre and back to post again lol
            files = dict()
            
            # get local uploaded files
            for FN, data in request.files.items():
                files[data.filename] = data.read().decode(data.mimetype_params.get('charset', 'utf-8'))
            
            # get file links from urllib3
            for URL in DF.URLs.data:
                req = http.request('GET', URL)
                if req.status == 200:
                    files[URL] = req.data.decode(req.headers.get('charset', 'utf-8'))
            
            columnLists = dict()
            for FN in files:
                if FN.endswith('.zip'): return 'UNZIP YOUR DATASETS U DUMB B'
                db.cur.execute('INSERT INTO datafiles (file_name, file_data, datasetID) VALUES (%s, %s, %s);', (FN, files[FN], datasetID))
                
                # if it's a csv add it to column selections
                splitFN = FN.split('.')
                if len(splitFN) > 1:
                    if splitFN[-1] == 'csv':
                        columnLists[FN] = csv.DictReader(io.StringIO(files[FN], newline='')).fieldnames
                    else: continue
                else: continue
                
            db.conn.commit()

            session['columnLists'] = json.dumps(columnLists)
            return redirect('/edit-dataset')
        try: # do other submitted operations
            if DF.newURL.data: DF.URLs.append_entry()
            elif DF.newFile.data: DF.files.append_entry()
            elif DF.removeURL.data: DF.URLs.pop_entry()
            elif DF.removeFile.data: DF.files.pop_entry()
        except: pass

    return render_template('new-dataset.html', form=DF, user=current_user)

 
@app.route('/edit-dataset', methods=['GET', 'POST'])
@login_required
def datasetEditor():
    
    datasetIDF = (int(session.get('datasetID', 0)),)
    # check if user has permissions to edit dataset

    db.cur.execute('SELECT title, posterID from datasets WHERE ID=%s;', datasetIDF)
    TS = db.cur.fetchone()
    if not TS.get('title', False):
        return 'lol we can\'t find that dataset'
    
    if TS['posterID'] != current_user.ID:
        return 'you don\'t have permission to edit that dataset'

    EF = f.datasetEditorForm()

    columnInquiries = json.loads(session.get('columnLists', '{}'))
    
    # add in selections to the form
    selectEntries = []
    for FN in columnInquiries:
        newEntry = f.SelectForm()
        newEntry.select.label = FN
        newEntry.select.id = FN
        newEntry.id = FN

        choices = []
        for choice in columnInquiries[FN]:
            choices.append((choice, choice))
        newEntry.select.choices = choices

        selectEntries.append(newEntry)
    EF.columnSelections = selectEntries

    #db.cur.execute('SELECT title, final_text FROM datasets WHERE ID=%s;', datasetIDF)
    #TS = db.cur.fetchone()
    
    
    if EF.validate_on_submit() and not EF.datasetRefresh.data:
        # set dataset final text
        db.cur.execute('UPDATE datasets SET final_text = %s WHERE ID = %s;', (EF.finalText.data, session['datasetID']))
        db.conn.commit()
        return redirect('/teach')
        
    # if finaltext isn't filled out
    if (not EF.finalText.data) or len(EF.finalText.data) < 1000:
    # deal with adding in text files
        db.cur.execute('SELECT file_data FROM datafiles WHERE datasetID = %s AND file_name NOT LIKE "%.csv";', datasetIDF)
        defaultTexts = []
        for result in db.cur.fetchall():
            defaultTexts.append(result['file_data'])

        # if column selections are entered / submitted...
        if request.method == 'POST' and (len(EF.columnSelections) == 0 or not EF.columnSelections[-1].errors):
            # get dataset's CSVs and check them against column selections, select and add in column data
            db.cur.execute('SELECT file_name, file_data FROM datafiles WHERE datasetID = %s AND file_name LIKE "%.csv";', datasetIDF)
            for result in db.cur.fetchall():
                CSVreader = csv.DictReader(io.StringIO(result['file_data'], newline=''))
                for entry in EF.columnSelections:
                    if entry.id == result['file_name']:
                        correctColumn = entry.select.data
                        CSVtexts = []
                        for row in CSVreader:
                            try:
                                CSVtexts.append(row[correctColumn])
                            except KeyError:
                                continue
                        defaultTexts.append('\n\n'.join(CSVtexts))
            
        EF.finalText.data = '\n\n\n'.join(defaultTexts)

    return render_template('dataset-editor.html', datasetName=TS['title'], form=EF, user=current_user)

trainerCommands = '''python3 /var/www/epic-gamer-science-fair-project/flaskr/train.py {} &
echo $!'''

@app.route('/new-model', methods=['GET', 'POST'])
@login_required
def modelMaker():
    MF = f.modelMakerForm()

    if MF.validate_on_submit():
        db.cur.execute('''INSERT INTO models
            (datasetID, trainerID, user_description, seed,
            num_layers, learning_rate, learning_rate_decay, dropout, seq_length, batch_size, max_epochs, grad_clip, train_frac, val_frac
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);''',
            (MF.datasetID.data, current_user.ID, MF.description.data, MF.seed.data,
            MF.layerAmount.data, MF.learningRate.data, MF.learningRateDecay.data, MF.dropout.data, MF.seqLength.data, MF.batchSize.data, MF.maxEpochs.data, MF.gradClip.data, MF.trainFrac.data, MF.valFrac.data))
        db.conn.commit()
        modelID = db.cur.lastrowid
        modelPID = subp.check_call(trainerCommands.format(modelID), shell=True)
        db.cur.execute('UPDATE models SET pid = %s WHERE ID = %s;', (modelPID, modelID))
        db.conn.commit()
        return redirect('/model-progress/'+str(modelID))
    if not MF.datasetID.data:
        try: MF.datasetID.data = int(session['dataset'])
        except: pass
    return render_template('model-maker.html', form=MF, user=current_user)

@app.route('/model-progress/<int:ID>')
@login_required
def showProgress(ID):
    db.cur.execute('SELECT max_epochs FROM models WHERE ID = %s;', (ID,))
    return render_template('model-progress.html', ID=ID, maxEpochs = db.cur.fetchone()['max_epochs'], user=current_user)

@app.route('/epoch-progress/<int:ID>')
def epochProgress(ID):
    db.cur.execute('SELECT epoch FROM logs WHERE modelID = %s ORDER BY epoch DESC LIMIT 1;', (ID,))
    if db.cur.rowcount:
        return jsonify([db.cur.fetchone()['epoch']])
    else: return jsonify([0, {'boi': True}])

# return json of progress for showprogress route, used for google charts
@app.route('/get-progress/<int:ID>')
def progressJson(ID):
    db.cur.execute('SELECT time_saved, loss, iteration, epoch FROM logs WHERE modelID = %s ORDER BY time_saved ASC;', (ID,))

    logEntries = db.cur.fetchall()
    
    lossChartRows = []
    
    prevEp = 420 # nice
    for i, e in enumerate(logEntries):
        ep = e['epoch']
        lossChartRows.append([i, # checkpoint
            e['loss'],
            'Batch {} on epoch {} has loss {}'.format(e['iteration'], ep, e['loss']),
            None if ep == prevEp else str(ep),
            'pee pee poo poo'])
            
        prevEp = ep

    return jsonify(lossChartRows) # will return more stuff in future


generatorCommands = 'python3 /var/www/epic-gamer-science-fair-project/flaskr/generate.py {} &'

@app.route('/generate/<int:ID>', methods=['GET', 'POST'])
@login_required
def generateText(ID):
    SF = f.sampleForm()
    if SF.validate_on_submit():
        db.cur.execute('INSERT INTO samples (modelID, checkpointID, temperature, sample_length, seed) VALUES (%s, %s, %s, %s, %s);',
        (ID, SF.checkpointID.data, SF.temperature.data, SF.sampleLength.data, SF.seed.data))
        db.conn.commit()
        subp.call(generatorCommands.format(ID), shell=True)
        return redirect('/generated/'+str(db.cur.lastrowid))

    return render_template('generate-text.html', form=SF, ID=ID, user=current_user)

# id here is for sample, not for model
@app.route('/generated/<int:ID>')
@login_required
def generatedText(ID):
    db.cur.execute('SELECT result, modelID FROM samples WHERE ID = %s;', (ID,))
    if not db.cur.rowcount: return 'boi'
    qResults = db.cur.fetchone()
    generatedText = qResults.get('results')

    if generatedText:
        return render_template('generated-text.html', ID=ID, generatedText=generatedText, user=current_user)
    return render_template('generating.html', ID=qResults['modelID'],)

@app.route('/exploremodels', methods=['GET', 'POST'])
@login_required
def exploreModels():
    return render_template('explore/models.html')

@app.route('/about')
def aboutPage():
    return render_template('about-index.html', user=current_user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(request.args.get('next', '/'))

    LF = f.loginForm()

    if LF.validate_on_submit():
        login_user(User('username', LF.username.data, True), remember=True)
        
        return redirect(request.args.get('next', '/'))
    
    return render_template('login.html', form=LF)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(request.args.get('next', '/'))



@app.route('/verify/<int:ID>', methods=['GET', 'POST'])
def verifyUser(ID):
    #ID = current_user.ID

    VF = f.verifyForm()
    VF.verifyAccountID = ID

    if VF.validate_on_submit():
        # verify the user in the DB
        db.cur.execute('UPDATE users SET verified=1 WHERE ID=%s;', (ID,))
        # delete the verification code, we don't need it anymore
        db.cur.execute('DELETE FROM verification_codes WHERE accountID=%s;', (ID,))
        db.conn.commit()

        login_user(User('ID', ID, True), remember=True)

        return redirect('/')
    
    return render_template('verify-email.html', form=VF)



# for generating verification codes
from random import randint

# message for verifying email
verifyMsg = Message('Verify your email to talk to Joe!', sender='joethernn@gmail.com')

@app.route('/register', methods=['GET', 'POST'])
def registerUser():
    RF = f.registerForm()

    if RF.validate_on_submit():
        
        # add the user to DB
        db.cur.execute('INSERT INTO users (email_addr, own_password, username, real_name) VALUES (%s, %s, %s, %s);',
            (RF.email.data, RF.password.data, RF.username.data, RF.name.data))
        db.conn.commit()

        accountID = db.cur.lastrowid

        #add the verification code to DB
        verificationCode = randint(1000,9999)
        db.cur.execute('INSERT INTO verification_codes (codeNumber, accountID) VALUES (%s, %s);',
            (verificationCode, accountID))
        db.conn.commit()

        # log in unverified user
        newUser = User()
        newUser.setValues('ID', accountID)
        login_user(newUser, remember=True)

        # send the verification message
        verifyMsg.recipients = [RF.email.data]
        verifyMsg.body = 'Hi '+RF.name.data+', use the code '+str(verificationCode)+' to verify your email address and get your account with Joe up and running.\nIf you don\'t know about the amazing Joe project, then just ignore this email. Thanks!'
        with app.app_context(): mail.send(verifyMsg)

        return redirect('/verify/' + str(accountID))

    return render_template('register.html', form=RF)
