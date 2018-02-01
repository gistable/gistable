import numpy as np
from sklearn.model_selection import train_test_split

import torch
import torch.nn as nn
from torch.autograd import Variable

np.random.seed(1337)

MAX_LEN = 30
EMBEDDING_SIZE = 64
BATCH_SIZE = 32
EPOCH = 40
DATA_SIZE = 1000
INPUT_SIZE = 300

def batch(tensor, batch_size):
	tensor_list = []
	length = tensor.shape[0]
	i = 0
	while True:
		if (i+1) * batch_size >= length:
			tensor_list.append(tensor[i * batch_size: length])
			return tensor_list
		tensor_list.append(tensor[i * batch_size: (i+1) * batch_size])
		i += 1

class Estimator(object):

	def __init__(self, model):
		self.model = model

	def compile(self, optimizer, loss):
		self.optimizer = optimizer
		self.loss_f = loss

	def _fit(self, X_list, y_list):
		"""
		train one epoch
		"""
		loss_list = []
		acc_list = []
		for X, y in zip(X_list, y_list):
			X_v = Variable(torch.from_numpy(np.swapaxes(X,0,1)).float())
			y_v = Variable(torch.from_numpy(y).long(), requires_grad=False)

			self.optimizer.zero_grad()
			y_pred = self.model(X_v, self.model.initHidden(X_v.size()[1]))
			loss = self.loss_f(y_pred, y_v)
			loss.backward()
			self.optimizer.step()

			## for log
			loss_list.append(loss.data[0])
			classes = torch.topk(y_pred, 1)[1].data.numpy().flatten()
			acc = self._accuracy(classes, y)
			acc_list.append(acc)

		return sum(loss_list) / len(loss_list), sum(acc_list) / len(acc_list)

	def fit(self, X, y, batch_size=32, nb_epoch=10, validation_data=()):
		X_list = batch(X, batch_size)
		y_list = batch(y, batch_size)

		for t in range(1, nb_epoch + 1):
			loss, acc = self._fit(X_list, y_list)
			val_log = ''
			if validation_data:
				val_loss, val_acc = self.evaluate(validation_data[0], validation_data[1], batch_size)
				val_log = "- val_loss: %06.4f - val_acc: %06.4f" % (val_loss, val_acc)
			print("Epoch %s/%s loss: %06.4f - acc: %06.4f %s" % (t, nb_epoch, loss, acc, val_log))

	def evaluate(self, X, y, batch_size=32):
		y_pred = self.predict(X)

		y_v = Variable(torch.from_numpy(y).long(), requires_grad=False)
		loss = self.loss_f(y_pred, y_v)

		classes = torch.topk(y_pred, 1)[1].data.numpy().flatten()
		acc = self._accuracy(classes, y)
		return loss.data[0], acc

	def _accuracy(self, y_pred, y):
		return sum(y_pred == y) / y.shape[0]

	def predict(self, X):
		X = Variable(torch.from_numpy(np.swapaxes(X,0,1)).float())		
		y_pred = self.model(X, self.model.initHidden(X.size()[1]))
		return y_pred		

	def predict_classes(self, X):
		return torch.topk(self.predict(X), 1)[1].data.numpy().flatten()



class GRU(nn.Module):
	def __init__(self, input_size, hidden_size, output_size):
		super(GRU, self).__init__()

		self.hidden_size = hidden_size

		self.gru = nn.GRU(input_size, hidden_size)
		self.linear = nn.Linear(hidden_size, output_size)

	def forward(self, input, hidden):
		_, hn = self.gru(input, hidden)
		## from (1, N, hidden) to (N, hidden)
		rearranged = hn.view(hn.size()[1], hn.size(2))
		out1 = self.linear(rearranged)
		return out1

	def initHidden(self, N):
		return Variable(torch.randn(1, N, self.hidden_size))

def main():
	class_size = 7

	## Fake data
	X = np.random.randn(DATA_SIZE * class_size, MAX_LEN, INPUT_SIZE)
	y = np.array([i for i in range(class_size) for _ in range(DATA_SIZE)])

	X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.2)

	model = GRU(INPUT_SIZE, EMBEDDING_SIZE, class_size)
	clf = Estimator(model)
	clf.compile(optimizer=torch.optim.Adam(model.parameters(), lr=1e-4),
				loss=nn.CrossEntropyLoss())
	clf.fit(X_train, y_train, batch_size=BATCH_SIZE, nb_epoch=EPOCH,
			validation_data=(X_test, y_test))
	score, acc = clf.evaluate(X_test, y_test)
	print('Test score:', score)
	print('Test accuracy:', acc)

	torch.save(model, 'model.pt')


if __name__ == '__main__':
	main()
