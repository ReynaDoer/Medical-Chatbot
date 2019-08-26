import nltk, re, pprint
from nltk import word_tokenize
from urllib import request
from bs4 import BeautifulSoup
import json
import wikipedia
import os

def getWikiText(search, name):
	url = wikipedia.page(search).url
	html = request.urlopen(url).read()

	#Removes the html from the text
	raw = BeautifulSoup(html,'html.parser').get_text()
	trainingTexts = os.listdir('../msgHistory/')

	if(name+'.txt' in trainingTexts):
		with open('../msgHistory/'+name+'.txt') as f:
			data = json.load(f)
		with open('../msgHistory/'+name+'.txt') as fs:
			newText = data.append(raw)
			json.dump(newText, fs)
	else:
		with open('../rawdata/medtext.txt') as f:
			data = json.load(f)
		with open('../msgHistory/'+name+'.txt', 'w+') as fs:
			newText=data.append(raw)
			json.dump(newText, fs)

	print(raw.get_text())
