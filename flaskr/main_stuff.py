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
import sys


import datetime as dt

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
class User:

    """
    username = str()
    name = str()
    ID = int()
    email = str()
    is_anonymous = True # duh
    is_authenticated = False
    is_active = False
    """

    def __init__ (self, fieldName, fieldRequest, authenticated=True):
        db.cur.execute('SELECT verified, ID, username, email_addr, real_name, self_description FROM users WHERE {}=%s;'.format(fieldName), (fieldRequest,))
        QA = db.cur.fetchone()
        if db.cur.rowcount:
            self.is_anonymous = False
            
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
    return User('ID', int(ID))

import subprocess as subp

# for reading datasets as they're uploaded
import csv
csv.field_size_limit(sys.maxsize)

# for downloading dataset files
import urllib3
http = urllib3.PoolManager()


class Votes:
    def __init__(self, userID, datasetID=None, modelID=None):
        self.failed = False
        if datasetID:
            self.tableIDF = 'datasetID'
            self.tableID = datasetID
        elif modelID:
            self.tableIDF = 'modelID'
            self.tableID = modelID
        else:
            self.failed = True

        self.userID = userID
        self.datasetID = datasetID
        self.modelID = modelID

        self.voterStatus()

    
    def voterStatus(self):
        db.conn.commit()
        db.cur.execute('SELECT positivity, negativity FROM votes WHERE {}=%s AND userID=%s;'.format(self.tableIDF), (self.tableID, self.userID))
        UV = db.cur.fetchone()
        
        if not db.cur.rowcount: self.userVote = 0
        elif UV['positivity']: self.userVote = 1
        elif UV['negativity']: self.userVote = -1
        
    
    def countVotes(self):
        db.cur.execute('SELECT COUNT(positivity), COUNT(negativity) FROM votes WHERE {}=%s;'.format(self.tableIDF), (self.tableID,))
        voteCounts = db.cur.fetchone()
        self.upvotes = voteCounts['COUNT(positivity)']
        self.downvotes = voteCounts['COUNT(negativity)']
        try:
            self.positivity = (self.upvotes / (self.upvotes + self.downvotes)) * 100
        except ZeroDivisionError:
            self.positivity = 0


    def upvote(self):
        self.voterStatus()

        if not self.userVote:
            db.cur.execute('INSERT INTO votes (userID, positivity, {}) VALUES (%s, 1, %s);'.format(self.tableIDF),
            (self.userID, self.tableID))
        else:
            db.cur.execute('UPDATE votes SET negativity=NULL, positivity=1 WHERE userID = %s AND {} = %s;'.format(self.tableIDF),
            (self.userID, self.tableID))
        db.conn.commit()
        self.userVote = 1
    
    def downvote(self):
        self.voterStatus()

        if not self.userVote:
            db.cur.execute('INSERT INTO votes (userID, negativity, {}) VALUES (%s, 1, %s);'.format(self.tableIDF),
            (self.userID, self.tableID))
        else:
            db.cur.execute('UPDATE votes SET positivity=NULL, negativity=1 WHERE userID = %s AND {} = %s;'.format(self.tableIDF),
            (self.userID, self.tableID))
        db.conn.commit()
        self.userVote = -1

@app.route('/votes/<int:ID>', methods=['GET', 'POST'])
def votePage(ID):
    #return 'work in progress'
    #sleep(randint(20, 80) / 100)
    votes = Votes(ID, int(request.args.get('datasetID', 0)), int(request.args.get('modelID', 0)))
    if votes.failed: return 'bruh moment', 500
    if request.method == 'POST':
        if request.form.get('upvote', -1) != -1: votes.upvote()
        elif request.form.get('downvote', -1) != -1: votes.downvote()
    
    votes.countVotes()
    bgColour = request.args.get('bg-colour', 'w3-bruh-blue')
    if bgColour not in ['w3-bruh-blue', 'w3-indigo', 'w3-2019-galaxy-blue']: bgColour = 'w3-bruh-blue'

    selectedBCs =     {'w3-indigo': 'w3-blue',         'w3-2019-galaxy-blue': 'w3-indigo',          'w3-bruh-blue': 'w3-indigo'}
    unselectedBCs =   {'w3-indigo': 'w3-bruh-blue',    'w3-2019-galaxy-blue': 'w3-bruh-blue',       'w3-bruh-blue': 'w3-2019-galaxy-blue'}
    hoverBCs =        {'w3-indigo': 'w3-hover-blue',   'w3-2019-galaxy-blue': 'w3-hover-indigo',    'w3-bruh-blue': 'w3-hover-indigo'}

    return render_template('votes.html', bgC=bgColour, selectedBC=selectedBCs[bgColour], unselectedBC=unselectedBCs[bgColour], hoverBC=hoverBCs[bgColour],
        upvotes=votes.upvotes, downvotes=votes.downvotes, upvoted=(votes.userVote==1), downvoted=(votes.userVote==-1), positivity=votes.positivity)


@app.template_filter('datetime')
def friendlyTime(dateAndTime):
    return dateAndTime.strftime('%-I:%M %p on %a. %b. %-d, %Y')

@app.errorhandler(404)
def pageNotFound(e):
    return render_template('404.html', missing='page'), 404

@app.errorhandler(500)
def internalError(e):
    return render_template('500.html'), 500

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
                files[data.filename] = data.read().decode(data.mimetype_params.get('charset', 'utf-8'), errors='ignore')
                    
            
            # get file links from urllib3
            for URL in DF.URLs.data:
                req = http.request('GET', URL)
                if req.status == 200:
                    files[URL] = req.data.decode(req.headers.get('charset', 'utf-8'), errors='ignore')
            
            columnLists = dict()
            for FN in files:
                if FN.endswith('.zip'): return 'Make sure you unzip your datasets first.'
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
    if not db.cur.rowcount:
        return render_template('404.html', missing='dataset'), 404
    
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
            (datasetID, trainerID, model_description, seed,
            num_layers, learning_rate, dropout, seq_length, batch_size, max_epochs 
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);''',
            (MF.datasetID.data, current_user.ID, MF.description.data, MF.seed.data,
            MF.layerAmount.data, MF.learningRate.data, MF.dropout.data, MF.seqLength.data, MF.batchSize.data, MF.maxEpochs.data,))
        db.conn.commit()
        modelID = db.cur.lastrowid
        modelPID = subp.check_call(trainerCommands.format(modelID), shell=True)
        db.cur.execute('UPDATE models SET pid = %s WHERE ID = %s;', (modelPID, modelID))
        db.conn.commit()
        return redirect('/m/'+str(modelID))
    if not MF.datasetID.data:
        MF.datasetID.data = int(request.args.get('datasetID', session.get('datasetID', 1)))
    
    return render_template('model-maker.html', form=MF, user=current_user)

@app.route('/epoch-progress/<int:ID>')
def epochProgress(ID):
    db.conn.commit()
    db.cur.execute('SELECT finished_naturally FROM models WHERE ID = %s;', (ID,))
    finished = db.cur.fetchone()['finished_naturally']

    db.cur.execute('SELECT epoch FROM logs WHERE modelID = %s ORDER BY epoch DESC LIMIT 1;', (ID,))
    if db.cur.rowcount:
        return jsonify([db.cur.fetchone()['epoch'], finished != None])
    else: return jsonify([0, False])


generatorCommands = 'python3 /var/www/epic-gamer-science-fair-project/flaskr/generate.py {} &'

@app.route('/generate/<int:ID>', methods=['GET', 'POST'])
@login_required
def generateText(ID):
    SF = f.sampleForm()
    SF.modelID = ID

    if SF.validate_on_submit():
        db.cur.execute('SELECT modelID FROM checkpoints WHERE ID = %s;', (SF.checkpointID.data,))
        cpRow = db.cur.fetchone()
        if not db.cur.rowcount: return render_template('404.html', missing='checkpoint'), 404
        if cpRow['modelID'] != ID: return render_template('404.html', missing='sample in that model'), 404

        surveyRequest(current_user)

        db.cur.execute('INSERT INTO samples (modelID, checkpointID, temperature, sample_length, seed, userID) VALUES (%s, %s, %s, %s, %s, %s);',
        (ID, SF.checkpointID.data, SF.temperature.data, SF.sampleLength.data, SF.seed.data, current_user.ID))
        db.conn.commit()
        sampleID = db.cur.lastrowid
        subp.call(generatorCommands.format(sampleID), shell=True)
        
        return redirect('/generated/'+str(sampleID))
    
    db.cur.execute('SELECT time_finished FROM models WHERE ID=%s;', (ID,))
    modelStuff = db.cur.fetchone()
    if not (db.cur.rowcount and modelStuff['time_finished']):
        return render_template('404.html', missing='model'), 404

    if not SF.checkpointID.data:
        db.cur.execute('SELECT ID FROM checkpoints WHERE modelID=%s AND final=1;', (ID,))
        SF.checkpointID.data = db.cur.fetchone()['ID']

    
    return render_template('generate-text.html', form=SF, ID=ID, user=current_user)

# id here is for sample, not for model
@app.route('/generated/<int:ID>')
@login_required
def generatedText(ID):
    db.conn.commit()
    db.cur.execute('SELECT result, modelID FROM samples WHERE ID = %s;', (ID,))
    if not db.cur.rowcount: return render_template('404.html', missing='sample'), 404
    qResults = db.cur.fetchone()
    generatedText = qResults.get('result')

    if generatedText:
        return render_template('generated-text.html', ID=qResults['modelID'], generatedText=generatedText, user=current_user)
    return render_template('generating.html', ID=qResults['modelID'],)


@app.route('/explore-models', methods=['GET', 'POST'])
def exploreModels():
    db.cur.execute('''SELECT models.ID, models.model_description, users.username, models.datasetID,
    datasets.title, datasets.user_description, LENGTH(datasets.final_text), datasets.time_posted AS dataset_time_posted
    FROM models LEFT JOIN (users, datasets)
    ON (users.ID = models.trainerID AND datasets.ID = models.datasetID)
    LEFT JOIN votes ON votes.modelID = models.ID
    GROUP BY models.ID
    ORDER BY COUNT(votes.positivity) - COUNT(votes.negativity) DESC;''')
    return render_template('explore-models.html', models=db.cur.fetchall(), user=current_user)

@app.route('/explore-datasets', methods=['GET', 'POST'])
def exploreDatasets():
    db.cur.execute('''SELECT datasets.ID, datasets.title, datasets.user_description, LENGTH(datasets.final_text), users.username
        FROM datasets LEFT JOIN users
        ON users.ID = datasets.posterID
        LEFT JOIN votes ON votes.datasetID = datasets.ID
        GROUP BY datasets.ID
        ORDER BY COUNT(votes.positivity) - COUNT(votes.negativity) DESC;''')
    return render_template('explore-datasets.html', datasets=db.cur.fetchall(), user=current_user)


@app.route('/u/<username>')
@login_required
def showUser(username):
    db.cur.execute('SELECT username, self_description, time_joined FROM users WHERE verified=1 AND username = %s;', (username,))
    u=db.cur.fetchone()
    if not db.cur.rowcount: return render_template('404.html', missing='user'), 404
    return render_template('user.html', u=u, user=current_user)

@app.route('/m/<int:ID>')
@login_required
def showModel(ID):
    db.conn.commit()
    db.cur.execute('SELECT finished_naturally FROM models WHERE ID = %s;', (ID,))
    
    if not db.cur.rowcount: return render_template('404.html', missing='model'), 404
    
    # return progress page if it isn't done training yet
    if db.cur.fetchone()['finished_naturally'] == None:
        db.cur.execute('SELECT max_epochs FROM models WHERE ID = %s;', (ID,))
        return render_template('model-progress.html', ID=ID, maxEpochs = db.cur.fetchone()['max_epochs'], user=current_user)

    # get model info
    db.cur.execute('''SELECT models.*, users.username
        FROM models LEFT JOIN users ON users.ID=models.trainerID WHERE models.ID = %s;''', (ID,))
    m=db.cur.fetchone()
    
    # get dataset info
    db.cur.execute('''SELECT datasets.title, datasets.user_description, datasets.time_posted, LENGTH(datasets.final_text), users.username
        FROM datasets LEFT JOIN users ON users.ID=datasets.posterID WHERE datasets.ID = %s;''', (m['datasetID'],))
    d=db.cur.fetchone()

    # get log
    db.cur.execute('SELECT loss, iteration, epoch FROM logs WHERE modelID = %s ORDER BY epoch, iteration ASC;', (ID,))
    logEntries = db.cur.fetchall()
    
    lossChartRows = []
    prevEp = 420 # nice
    for i, e in enumerate(logEntries):
        ep = e['epoch']
        lossChartRows.append([i, # checkpoint
            e['loss'],
            'Batch {} on epoch {} has loss {}'.format(e['iteration'], ep, e['loss']),
            None if ep == prevEp else str(ep),
            'Start of epoch {}'.format(ep)])
            
        prevEp = ep
    return render_template('model.html', m=m, d=d, user=current_user, chartRows=json.dumps(lossChartRows))

@app.route('/d/<int:ID>')
@login_required
def showDataset(ID):
    db.cur.execute('''SELECT datasets.title, datasets.user_description, datasets.time_posted, LENGTH(datasets.final_text), users.username
        FROM datasets LEFT JOIN users ON users.ID=datasets.posterID WHERE datasets.ID = %s;''', (ID,))
    d=db.cur.fetchone()
    if not db.cur.rowcount: return render_template('404.html', missing='dataset'), 404
    return render_template('dataset.html', d=d, user=current_user, ID=ID)


@app.route('/about')
def aboutPage():
    return render_template('about-index.html', user=current_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(request.args.get('next', '/'))

    LF = f.loginForm()

    if LF.validate_on_submit():
        login_user(User('username', LF.username.data), remember=True)
        
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
        db.cur.execute('UPDATE users SET verified=1 WHERE ID = %s;', (ID,))
        # delete the verification code, we don't need it anymore
        db.cur.execute('DELETE FROM verification_codes WHERE accountID = %s;', (ID,))
        db.conn.commit()

        login_user(User('ID', ID), remember=True)

        return render_template('noobs.html', user=current_user)
    
    return render_template('verify-email.html', form=VF)


#test
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
        newUser = User('ID', accountID, True)
        login_user(newUser, remember=True)

        # send the verification message
        verifyMsg.recipients = [RF.email.data]
        verifyMsg.body = 'Hi '+RF.name.data+', use the code '+str(verificationCode)+' to verify your email address and get your account with Joe up and running.\nIf you don\'t know about the amazing Joe project, then just ignore this email. Thanks!'
        with app.app_context(): mail.send(verifyMsg)

        return redirect('/verify/' + str(accountID))

    return render_template('register.html', form=RF)


@app.route('/survey', methods=['GET', 'POST'])
@login_required
def survey():
    SF = f.survey()
    if SF.validate_on_submit():
        db.cur.execute('''INSERT INTO survey (userID, generalF, tech_comfort,
        navigation, navigationF, datasets, datasetsF, models, modelsF, samples, samplesF, descriptions, descriptionsF)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''', (current_user.ID, SF.generalFeedback.data, SF.techComfort.data,
        SF.navigation.data, SF.navigationF.data, SF.datasets.data, SF.datasetsF.data, SF.models.data, SF.modelsF.data, SF.samples.data, SF.samplesF.data, SF.descriptions.data, SF.descriptionsF.data))
        db.conn.commit()
        return render_template('thank-you.html', user=current_user)
    
    return render_template('survey.html', form=SF)

def surveyRequest(user):
    uID = user.ID
    """
    db.cur.execute('SELECT ID FROM samples WHERE userID = %s;', (uID,))
    db.cur.fetchone()
    if db.cur.rowcount: return False
    """
    db.cur.execute('SELECT ID FROM survey WHERE userID = %s;', (uID,))
    db.cur.fetchone()
    if db.cur.rowcount: return False
    """
    db.cur.execute('SELECT ID FROM datasets WHERE posterID = %s;', (uID,))
    db.cur.fetchone()
    if not db.cur.rowcount: return False
    db.cur.execute('SELECT ID FROM models WHERE trainerID = %s;', (uID,))
    db.cur.fetchone()
    if not db.cur.rowcount: return False
    """
    
    firstName = user.name.split()[0]
    reqBody = '''Hi {},
    please fill out a quick survey for Joe at http://99.199.44.233/survey. Your feedback is essential to keep on improving our service.'''
    reqHTML= ''' Hi {},<br>
    please fill out a quick survey for Joe <a href="http://99.199.44.233/survey">right here</a>. Your feedback is essential to keep on improving our service.'''
    
    surveyReq = Message(recipients=[user.email], body=reqBody.format(firstName), html=reqHTML.format(firstName), subject='Please give us some feedback on how to improve our site!', sender='joethernn@gmail.com')
    with app.app_context(): mail.send(surveyReq)
    return True
