import torch
import torchvision
from torchvision import transforms, datasets

train = datasets.MNIST("", train=True, download = True, transform = transforms.Compose([transforms.ToTensor()]))

test = datasets.MNIST("", train=False, download = True, transform = transforms.Compose([transforms.ToTensor()]))

trainset = torch.utils.data.DataLoader(train, batch_size = 10, shuffle = True)
testset = torch.utils.data.DataLoader(test, batch_size = 10, shuffle = True)

import torch.nn as nn
import torch.nn.functional as F

class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(28*28, 64)
        self.fc2 = nn.Linear(64, 64)
        self.fc3 = nn.Linear(64, 64)
        self.fc4 = nn.Linear(64, 10)
    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        x = self.fc4(x)


        return F.log_softmax(x, dim=1)
net = Net()

X = torch.rand((28, 28))
import torch.optim as optim
optimizer = optim.Adam(net.parameters(), lr = 0.001)

EPOCHS = 3
for epochs in range(EPOCHS):
    for data in trainset:
        X, y = data
        net.zero_grad()
        output = net(X.view(-1, 28*28))
        loss = F.nll_loss(output, y)
        loss.backward()
        optimizer.step()
    print(loss)


correct = 0
total = 0
with torch.no_grad():
    for data in testset:
        X, y = data
        output = net(X.view(-1, 28*28))
        for idx, i in enumerate(output):
            if torch.argmax(i) == y[idx]:
                correct += 1
            total += 1

print("Accuracy was", round(correct/total, 3))

import matplotlib.pyplot as plt
plt.imshow(X[0].view(28, 28))
plt.show()
'''for data in trainset:
    print(data)
    break

x, y = data[0][0], data[1][0]
print(y)

import matplotlib.pyplot as plt
plt.imshow(data[0][0].view(28, 28))
plt.show()

counter_dict = {0:0, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0}

for data in trainset:
    Xs, Ys = data
    for y in Ys:
        counter_dict[int(y)]+= 1
print(counter_dict)'''