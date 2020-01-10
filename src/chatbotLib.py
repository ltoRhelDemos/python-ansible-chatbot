
# -*- coding: utf-8 -*-
#
#  chatbot.py
#  
#  Copyright 2020 Dirgan <Dirgan@DESKTOP-RJGI65M>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

try:
	import nltk
except: 
	print( 'chatbotLib: nltk lib not found'   )
	exit(1)

try:
	import numpy
except: 
	print( 'chatbotLib: numpy lib not found'   )
	exit(1)

try:
	import tflearn
except: 
	print( 'chatbotLib: tflearn lib not found'   )
	exit(1)

try:
	import tensorflow
except: 
	print( 'chatbotLib: tensorflow lib not found'   )
	exit(1)

import random
import json
import pickle
import signal

from nltk.stem.lancaster import LancasterStemmer



###########
##   C   ##
###########
class ltoChatbot():
#-------------------------------------------------------------------------------------------------------------------
	def __init__(self, botName = "ltoChatbot", corpusFile = "ltoChatbotCorpus.json", specialization="Specialized topic", neurons=10, iterations = 1000, levels = 2, forceTraining=False):
#-------------------------------------------------------------------------------------------------------------------
		self._modelOnDisk = "ltoChatBot.tflearn"
		self._dataOnDisk = "ltoChatbot.pdata"
		self._conversationOnDisk = "ltoChatbotConversationCorpus.json"
		self._botName = botName
		self._specialization = specialization
		
		self._corpusFile = corpusFile
		self._corpusData = None
		
		self._model = None
		
		self._stemmer = LancasterStemmer()

		self._words = []
		self._labels = []
		self._dx = []
		self._dy = []
		
		nltk.download('punkt')	

		self._notKnownResponses = ["I'm not quite sure what you are asking for... could you repeat your question?",
								"Don't understand your question, rephrase your question please!",
								"I got lost, could you please repeat what you are looking for?",
								"I think I don´t get you question, please ask again",
								"I am a specialized bot for responding on an specific topic, please ask something about %s"%self._specialization]

		self.setup()
	
		self.train(force=forceTraining, neurons=neurons, trainingIterations = iterations, levels = levels)
		
#-------------------------------------------------------------------------------------------------------------------
	def setup(self):
#-------------------------------------------------------------------------------------------------------------------


		try:
			with open(self._corpusFile) as file:
				self._corpusData = json.load(file)
		except:
			print("ERROR: no Corpus was found!")
			exit(1)

		try:
			with open(self._conversationOnDisk) as file:
				_conversationalData = json.load(file)
			
			self._corpusData["topics"].extend(_conversationalData["topics"])
		except Exception as err:
			print("ERROR: no Conversation Corpus was found, so the bot won't be polite!")		

		try:
			with open(self._dataOnDisk, "rb") as f:
				self._words, self._labels, self._training, self._output = pickle.load(f)
			print("Found data preprocessed on disk!")
		except:
			for topic in self._corpusData["topics"]:
				for pattern in topic["patterns"]:
					wordsTokenized = nltk.word_tokenize(pattern)
					wordsLowerized = [i.lower() for i in wordsTokenized if i!="?"]
					self._words.extend(wordsLowerized)
					self._dx.append(wordsLowerized)
					self._dy.append(topic["tag"].lower())

				if topic["tag"].lower() not in self._labels:
					self._labels.append(topic["tag"].lower())

			self._words = [self._stemmer.stem(w) for w in self._words if w != "?"]
			
			self._words = sorted(list(set(self._words)))
			self._labels = sorted(self._labels)

			self._training = []
			self._output = []

			_outEmpty = [0 for _ in range(len(self._labels))]

			for index, dx in enumerate(self._dx):
				_bagOfWords = []

				wrds = [self._stemmer.stem(w.lower()) for w in dx]

				for w in self._words:
					if w in wrds:
						_bagOfWords.append(1)
					else:
						_bagOfWords.append(0)

				_outputRow = _outEmpty[:]
				_outputRow[self._labels.index(self._dy[index])] = 1

				self._training.append(_bagOfWords)
				self._output.append(_outputRow)


			self._training = numpy.array(self._training)
			self._output = numpy.array(self._output)

			with open(self._dataOnDisk, "wb") as f:
				pickle.dump((self._words, self._labels, self._training, self._output), f)

#-------------------------------------------------------------------------------------------------------------------
	def train(self, force = False, levels = 2, neurons = 10, trainingIterations = 1000, verbose = True):
#-------------------------------------------------------------------------------------------------------------------
		tensorflow.reset_default_graph()

		_net = tflearn.input_data(shape=[None, len(self._training[0])])

		for i in range(levels): 
			_net = tflearn.fully_connected(_net, neurons)

		_net = tflearn.fully_connected(_net, len(self._output[0]), activation="softmax")
		_net = tflearn.regression(_net)

		self._model = tflearn.DNN(_net)
		if force:
			print("recreating the model!")
			try:
				self._model.fit(self._training, self._output, n_epoch=trainingIterations, batch_size=neurons, show_metric=True)
				print("Saving model on Disk!")
				self._model.save(self._modelOnDisk)	
			except:
				print("Something wrong has happended training your model!")
		else:
			try:
				self._model.load(self._modelOnDisk)	
				print("found model on disk!")
			except:	
				print("recreating the model!")
				try:
					self._model.fit(self._training, self._output, n_epoch=trainingIterations, batch_size=neurons, show_metric=True)
					print("Saving model on Disk!")
					self._model.save(self._modelOnDisk)	
				except:
					print("Something wrong has happended training your model!")

#-------------------------------------------------------------------------------------------------------------------
	def retrain(self, levels = 2, neurons = 10, iterations = 1000, verbose = True):
#-------------------------------------------------------------------------------------------------------------------
		self.train(force=True, levels=levels, neurons=neurons, trainingIterations=iterations)

#-------------------------------------------------------------------------------------------------------------------
	def askBot(self, question = "Who are you?", accuracy = .7):
# ~ #-------------------------------------------------------------------------------------------------------------------
		_inWords = question.lower()
		_bagOfInWords = [0 for _ in range(len(self._words))]
		_inWordsTokenized = nltk.word_tokenize(_inWords)
		_inWordsTokenized = [self._stemmer.stem(w) for w in _inWordsTokenized]
		
		for word in _inWordsTokenized:
			for i,w in enumerate(self._words):
				if w == word: 
					_bagOfInWords[i] = 1
		
		_result =self._model.predict([numpy.array(_bagOfInWords)])
		
		if  max(_result[0]) > accuracy:
			_resultIndex = numpy.argmax(_result)
			_tagPredicted = self._labels[_resultIndex].lower()
			
			for _tag in self._corpusData["topics"]:
				if _tag['tag'].lower() == _tagPredicted:
					_responses = _tag['responses']			


			if _tagPredicted == "content":
				_resp = " ,".join([ tag["tag"].lower() for tag in self._corpusData["topics"] ])
			else:
				_resp = random.choice(_responses)
		else:
			_resp = random.choice(self._notKnownResponses)
			_tagPredicted = "not Known Responses"
	
		return {"tag":_tagPredicted, "answer":_resp}


#-------------------------------------------------------------------------------------------------------------------
def stopServerHandler(signum, frame):
#-------------------------------------------------------------------------------------------------------------------
	print( 'Stopping Chatbot with Ctrl-C')
	exit(0)
	
############################################
############################################
############################################
if __name__ == '__main__':
	
	signal.signal(signal.SIGINT, stopServerHandler)

	chatBot = ltoChatbot(corpusFile="Ansible_Corpus.json", forceTraining=False, levels=2, iterations = 300)
	
	chatBot.retrain(iterations=300)
	
	while True:
		resp = chatBot.askBot(input("Alejandro: ").lower(), accuracy=.8)
		print()
		print("BOT: ",resp["answer"])
		print()
		if (resp["tag"] == "goodbye"): exit(0)

