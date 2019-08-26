import nltk
import numpy as np
import random
import string
import json
from flask import Flask, render_template, request
from search_biopython import search, fetch_details
from symptoms import what_are_your_symptoms
import os
from wikiTrain import getWikiText
from prediction import response, classify


trainingTexts = os.listdir('../msgHistory/')

current = open('../msgHistory/currentChat.txt','r')
patient_name=current.read()
if patient_name+'.txt' in trainingTexts:
	f=open('../msgHistory/'+patient_name+'.txt','r',errors = 'ignore')
else:
	f=open('../rawdata/medtext.txt','r',errors = 'ignore')

raw=f.read()

raw=raw.lower()# converts to lowercase

nltk.download('punkt') # first-time use only
nltk.download('wordnet') # first-time use only

sent_tokens = nltk.sent_tokenize(raw)# converts to list of sentences 
word_tokens = nltk.word_tokenize(raw)# converts to list of words

print(sent_tokens[:2])
print(word_tokens[:2])

lemmer = nltk.stem.WordNetLemmatizer()
#WordNet is a semantically-oriented dictionary of English included in NLTK.

def LemTokens(tokens):
    return [lemmer.lemmatize(token) for token in tokens]
remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)
def LemNormalize(text):
    return LemTokens(nltk.word_tokenize(text.lower().translate(remove_punct_dict)))

GREETING_INPUTS = ("hello", "hi", "greetings", "sup", "what's up","hey",)

GREETING_RESPONSES = ["hi", "hey", "*nods*", "hi there", "hello", "I am glad! You are talking to me"]

def greeting(sentence):
 
    for word in sentence.split():
        if word.lower() in GREETING_INPUTS:
            return random.choice(GREETING_RESPONSES)

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def backup_response(user_response):
    robo_response=''
    sent_tokens.append(user_response)

    TfidfVec = TfidfVectorizer(tokenizer=LemNormalize, stop_words='english')
    tfidf = TfidfVec.fit_transform(sent_tokens)
    vals = cosine_similarity(tfidf[-1], tfidf)
    idx=vals.argsort()[0][-2]
    flat = vals.flatten()
    flat.sort()
    req_tfidf = flat[-2]

    if(req_tfidf==0):
        robo_response=robo_response+"I am sorry! I don't understand you"+doctorInfo()
        return robo_response
    else:
        robo_response = robo_response+sent_tokens[idx]
        return robo_response

def patientIntake(index):
	switch = {
		0:["Phone Number","Hello, welcome to the MAIA clinic.  I am here to help with patient intake.  First tell me your phone number."],
		1:["Street Address" ,"And what is your street address?"],
		2:["City", "What city is that in?"],
		3:["Birthdate", "What is your date of birth?"],
		4:["Gender", "And what is your gender?"],
		5:["Symptoms","Could you tell me some of your symptoms?"],
		6:["Medications", "Are you on any medications at the moment?"],
		7:["Perfect, now that we know a bit about you do you have any questions for me?"]
	}

	return switch[index]


def doctorRegistration(index):
	switch = {
		0:["Phone Number","Hello, welcome to the MAIA clinic.  I am here to help with your doctor profile.  First tell me your phone number."],
		1:["Street Address" ,"And what is your street address?"],
		2:["City", "What city is that in?"],
		3:["Birthdate", "What is your date of birth?"],
		4:["Gender", "And what is your gender?"],
		5:["Specialty","Do you have a specialty?"],
		6:["Patients", "Are there any specific patients you would like to keep an eye on?"],
		7:["Perfect, now that we know a bit about you do you have any questions for me?\n"+doctorInfo()]
	}

	return switch[index]

def doctorInfo():
	bot_response = "If you would like to see the record of a particular patient ask 'record for patient X.'\n"\
		"If you would like to get articles on a subject ask 'can I see articles on X.'\n"\
		"If you would like me to have knowledge in a particular subject, ask 'can you learn about X.'\n"\
		"If you would like a potential diagnosis for a patient, ask 'diagnose patient with symptoms X.'"

	return bot_response

def retrieveRecord(name):
	print('../msgHistory/patients/'+name+'.json')
	try:
		with open('../msgHistory/patients/'+name+'.json') as f:
			print('Hello')
			data = json.load(f)
			record = 'Name: '+data["name"]+'\n'
			record = record + 'Phone Number: '+data["Phone Number"]+', '+'Street Address: '+data["Street Address"]+', '\
				'City: '+data["City"]+', '+'Birthdate: '+data["Birthdate"]+', '+'Gender: '+data["Gender"]+', '\
				'Symptoms: '+data["Symptoms"]+', '+'Medications: '+data["Medications"]

	except Exception as e:
		record = 'Sorry that patient record does not exist'

	return record

def convert_to_doctor(response):
	print(response)
	return response.replace('you', 'the patient')
	

app = Flask(__name__)


def newPatient(name):
	print("new patient")
	patientfile = '../msgHistory/patients/'+name+'.json'
	patientinfo = {}
	patientinfo["name"]=name
	patientinfo["PATIENTINDEX"]=0
	patientinfo["messages"]=[]
	with open(patientfile,'w+') as f:
		json.dump(patientinfo,f)

def newDoctor(name):
	print("new doctor")
	patientfile = '../msgHistory/doctors/'+name+'.json'
	patientinfo = {}
	patientinfo["name"]=name
	patientinfo["DOCTORINDEX"]=0
	patientinfo["messages"]=[]
	with open(patientfile,'w+') as f:
		json.dump(patientinfo,f)

@app.route('/')
def home():
	return render_template('home.html')

@app.route('/patientQ', methods=['POST'])
def patientQ():
	return render_template('patientQ.html')

@app.route('/doctorQ', methods=['POST'])
def doctorQ():
	return render_template('doctorQ.html')

@app.route('/doctor', methods=['POST'])
def doctor():

	doctor_name=request.form['doctor_name'].lower().replace(' ','')
	print(doctor_name)
	doctors = os.listdir('../msgHistory/doctors/')
	if doctor_name+'.json' not in doctors:
		newDoctor(doctor_name)
		with open('../msgHistory/doctors/'+doctor_name+'.json') as f:
			history=json.load(f)
		bot_response = doctorRegistration(history["DOCTORINDEX"])[1]
	else:
		with open('../msgHistory/doctors/'+doctor_name+'.json') as f:
			history=json.load(f)
		bot_response = greeting('Hi')

	messages=history["messages"]

	botBlock={}
	botBlock["message"]=bot_response
	botBlock["sender"]='bot'

	messages.append(botBlock)
	MESSAGES=history

	with open('../msgHistory/doctors/'+doctor_name+'.json', 'w') as fs:
		json.dump(history,fs)

	current=open('../msgHistory/currentChat.txt','w')
	current.write(doctor_name)
	current.close()

	return render_template('doctor.html',MESSAGES=MESSAGES)

@app.route('/patient', methods=['POST'])
def patient():

	patient_name=request.form['patient_name'].lower().replace(' ','')
	print(patient_name)
	patients = os.listdir('../msgHistory/patients/')
	if patient_name+'.json' not in patients:
		newPatient(patient_name)
		with open('../msgHistory/patients/'+patient_name+'.json') as f:
			history=json.load(f)
		bot_response = patientIntake(history["PATIENTINDEX"])[1]
	else:
		with open('../msgHistory/patients/'+patient_name+'.json') as f:
			history=json.load(f)
		bot_response = greeting('Hi')

	messages=history["messages"]

	botBlock={}
	botBlock["message"]=bot_response
	botBlock["sender"]='bot'

	messages.append(botBlock)
	MESSAGES=history
	print(MESSAGES)

	with open('../msgHistory/patients/'+patient_name+'.json', 'w') as fs:
		json.dump(history,fs)

	current=open('../msgHistory/currentChat.txt','w')
	current.write(patient_name)
	current.close()

	return render_template('patient.html', MESSAGES=MESSAGES)

@app.route('/patientprocess', methods=['POST'])
def patientprocess():
	current = open('../msgHistory/currentChat.txt','r')
	patient_name=current.read()
	with open('../msgHistory/patients/'+patient_name+'.json') as f:
			history=json.load(f)
	PATIENTINDEX=history["PATIENTINDEX"]
	user_response = request.form['user_input'].lower()
	userBlock={}
	userBlock["message"]=user_response
	userBlock["sender"]='user'
	if PATIENTINDEX<7 and PATIENTINDEX>-1:
		data = patientIntake(PATIENTINDEX)[0]
		history[data]=user_response
		PATIENTINDEX=PATIENTINDEX+1
		if PATIENTINDEX==7:
			bot_response=patientIntake(PATIENTINDEX)[0]
		else:
			bot_response=patientIntake(PATIENTINDEX)[1]
	else:
		bot_response=response(user_response)

	messages=history["messages"]
	history["PATIENTINDEX"]=PATIENTINDEX

	botBlock={}
	botBlock["message"]=bot_response
	botBlock["sender"]='bot'

	messages.append(userBlock)
	messages.append(botBlock)
	MESSAGES=history

	with open('../msgHistory/patients/'+patient_name+'.json', 'w') as fs:
		json.dump(history,fs)


	return render_template('patient.html', MESSAGES=MESSAGES)


@app.route('/doctorprocess', methods = ['POST'])
def doctorprocess():
	bot_response=''
	current = open('../msgHistory/currentChat.txt','r')
	doctor_name = current.read()
	with open('../msgHistory/doctors/'+doctor_name+'.json') as f:
		history = json.load(f)
	DOCTORINDEX = history["DOCTORINDEX"]
	user_response = request.form['user_input']
	messages=history["messages"]
	user_input=request.form['user_input'].lower()
	userBlock = {}
	userBlock["message"]=user_input
	userBlock["sender"]='user'
	if('can i see articles' in user_input):
		tokens = nltk.word_tokenize(user_input)
		length = len(tokens)
		results = search(tokens[length-1])
		id_list = results['IdList']
		papers = fetch_details(id_list)
		bot_response=''
		for i, paper in enumerate(papers['PubmedArticle']): 
			bot_response=bot_response + "%d) %s" % (i+1, paper['MedlineCitation']['Article']['ArticleTitle'])+'\n'
			# try:
			# 	bot_response=bot_response + paper['MedlineCitation']['Article']['Abstract']['AbstractText'][0]+'\n'
			# except Exception as e:
			# 	bot_response = bot_response+"No Abstract\n"
	elif DOCTORINDEX<7 and DOCTORINDEX>-1:
		data = doctorRegistration(DOCTORINDEX)[0]
		history[data]=user_response
		DOCTORINDEX=DOCTORINDEX+1
		if DOCTORINDEX==7:
			bot_response=doctorRegistration(DOCTORINDEX)[0]
		else:
			bot_response=doctorRegistration(DOCTORINDEX)[1]
	elif('record for' in user_input):
		tokens = nltk.word_tokenize(user_input)
		patient_name = tokens[3:]
		sep = ''
		print(patient_name)
		bot_response = retrieveRecord(sep.join(patient_name))

	elif('diagnose patient' in user_input):
		tokens = nltk.word_tokenize(user_input)
		symptoms=tokens[4:]
		strSympt = ''
		for i in range(len(symptoms)):
			strSympt = strSympt+symptoms[i]
		print(strSympt)
		bot_response=str(classify(strSympt))
		print(str(response))

	elif('can you learn' in user_input):
		try:
			tokens=nltk.word_tokenize(user_input)
			lookfor = tokens[4:]
			joined = (' ').join(lookfor)
			getWikiText(lookfor)
			bot_response= "I learned a bit about "+joined
		except Exception as e:
			raise e

	else:
		classified = classify(user_input)
		patient_response = response(user_input)
		try:
			bot_response = convert_to_doctor(patient_response)
		except Exception as e:
			bot_response = "Sorry, I don't understand you"
		
		if bot_response == "We will be with the patient as soon as we can":
			bot_response=backup_response(user_input)
		

	messages=history["messages"]
	history["DOCTORINDEX"]=DOCTORINDEX

	botBlock = {}
	botBlock["message"]=bot_response
	botBlock["sender"]='bot'

	messages.append(userBlock)
	messages.append(botBlock)
	MESSAGES=history

	with open('../msgHistory/doctors/'+doctor_name+'.json', 'w') as fs:
		json.dump(history,fs)

	return render_template('doctor.html',user_input=user_input, bot_response=bot_response, MESSAGES=MESSAGES)

if __name__=='__main__':
	app.run(debug=True,port=5002)
























