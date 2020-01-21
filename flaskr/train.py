# Special thanks to Kyle McDonald, this is based on his example
# https://gist.github.com/kylemcdonald/2d06dc736789f0b329e11d504e8dee9f
# Thanks to Laurent Dinh for examples of parameter saving/loading in PyTorch
# Thanks to Sean Robertson for https://github.com/spro/practical-pytorch

#from tqdm import tqdm
import db

from torch.autograd import Variable
import torch.nn as nn
import torch

import numpy as np
import math
import os

from sys import argv

import pickle

from rnn import *

db.cur.execute('SELECT * FROM models WHERE ID = %s;', (int(argv[1]),))
args = db.cur.fetchone()


outputPath = '/home/thomas/pytorch-models'

saveString = 'INSERT INTO checkpoints (modelID, loss, iteration, epoch, epoch_final, final) VALUES (%s, %s, %s, %s, %s, %s);'

#use_cuda = torch.cuda.is_available()

# randomise runs
torch.manual_seed(np.random.randint(1,9999))
random_state = np.random.RandomState(np.random.randint(1,9999))

seq_length =  args['seq_length']
batch_size = args['batch_size']
hidden_size = args['rnn_size']
epoch_count = args['max_epochs']
n_layers = args['num_layers']
lr = args['learning_rate']
dropout = args['dropout']
datasetID = args['datasetID']
modelID = args['ID']
logEvery = 19

db.cur.execute('SELECT final_text FROM datasets WHERE ID = %s;', (datasetID,))
text = db.cur.fetchone()['final_text']

chars = sorted(list(set(text)))

db.cur.execute('UPDATE models SET char_file = %s WHERE ID = %s;', (pickle.dumps(chars), modelID))
db.conn.commit()

chars_len = len(chars)
char_to_index = {}
index_to_char = {}
for i, c in enumerate(chars):
    char_to_index[c] = i
    index_to_char[i] = c

def chunks(l, n):
    for i in range(0, len(l) - n, n):
        yield l[i:i + n]

def index_to_tensor(index):
    tensor = torch.zeros(1, 1).long()
    tensor[0,0] = index
    return Variable(tensor)

def train():
    # saves to log and resets every 5 iters
    iTracker = 0

    # convert all characters to indices
    batches = [char_to_index[char] for char in text]

    # chunk into sequences of length seq_length + 1
    batches = list(chunks(batches, seq_length + 1))

    # chunk sequences into batches
    batches = list(chunks(batches, batch_size))

    # convert batches to tensors and transpose
    # each batch is (sequence_length + 1) x batch_size
    batches = [torch.LongTensor(batch).transpose_(0, 1) for batch in batches]

    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    loss_function = nn.CrossEntropyLoss()
    hidden = Variable(model.create_hidden(batch_size)).cuda()

    model.cuda()

    all_losses = []

    best_ep_loss = float('inf')
    try:
        best_tl_loss = float('inf')
        for epoch in range(1, epoch_count + 1):
            random_state.shuffle(batches)

            best_loss = float('inf')
            for batch, batch_tensor in enumerate(batches):
                batch_tensor = batch_tensor.cuda()

                # reset the model
                model.zero_grad()

                # everything except the last
                input_variable = Variable(batch_tensor[:-1])

                # everything except the first, flattened
                # what does this .contiguous() do?
                target_variable = Variable(batch_tensor[1:].contiguous().view(-1))

                # prediction and calculate loss
                output, _ = model(input_variable, hidden)
                loss = loss_function(output, target_variable)

                # backprop and optimize
                loss.backward()
                optimizer.step()

                loss = loss.item() #.data[0]
                best_tl_loss = min(best_tl_loss, loss)
                all_losses.append(loss)

                if iTracker == logEvery:
                    db.cur.execute('INSERT INTO logs (modelID, loss, iteration, epoch) VALUES (%s, %s, %s, %s);', (modelID, loss, batch, epoch))
                    db.conn.commit()
                    iTracker = 0
                else: iTracker += 1

                #batches_progress.set_postfix(loss='{:.03f}'.format(loss))
                if loss < 1.3 and loss == best_tl_loss:
                    db.cur.execute(saveString, (modelID, loss, batch, epoch, False, False))
                    db.conn.commit()
                    checkpoint_path = os.path.join(outputPath, str(db.cur.lastrowid))
                    #checkpoint_path = checkpoint_path + str('{:.03f}'.format(loss)) + '.cp'
                    torch.save({
                        'model': model.state_dict(),
                        'optimizer': optimizer.state_dict()
                    }, checkpoint_path)
   
            #epoch_progress.set_postfix(loss='{:.03f}'.format(best_loss))
            best_ep_loss = min(best_ep_loss, loss)

            if loss == best_ep_loss:
                db.cur.execute(saveString, (modelID, loss, seq_length, epoch, True, False))
                db.conn.commit()
                checkpoint_path = os.path.join(outputPath, str(db.cur.lastrowid))
                #checkpoint_path = checkpoint_path + str('{:.03f}'.format(loss)) + '.cp'
                torch.save({
                    'model': model.state_dict(),
                    'optimizer': optimizer.state_dict()
                }, checkpoint_path)

    except KeyboardInterrupt:
        return 0

    # final save str('{:.03f}'.format(loss))

    db.cur.execute(saveString, (modelID, loss, seq_length, epoch_count, False, True))
    db.conn.commit()
    final_path = os.path.join(outputPath, str(db.cur.lastrowid))
    #final_path = final_path +  + '.cp'
    torch.save({
        'model': model.state_dict(),
        'optimizer': optimizer.state_dict()
    }, final_path)

    return 1

model = RNN(chars_len, hidden_size, chars_len, n_layers, dropout)
try:
    finishStatus = train()
    
except RuntimeError:
    finishStatus = 0

db.cur.execute('UPDATE models SET finished_naturally = %s, time_finished = CURRENT_TIMESTAMP WHERE ID = %s;', (finishStatus, modelID))

db.conn.commit()
db.cur.close()
db.conn.close()