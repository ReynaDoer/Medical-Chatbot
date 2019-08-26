import json
import nltk
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()
from nltk import word_tokenize
from nltk.corpus import stopwords
import numpy as np
import tflearn
import tensorflow as tf
import random


def what_are_your_symptoms(patient_symptoms):
	print(patient_symptoms)
	potential_diagnosis = []
	with open('../rawdata/disease.json','r') as f:
		diseases = json.load(f)
		for patient_symptom in patient_symptoms:
			for disease in diseases:
				if patient_symptom in diseases[disease]['symptoms']:
					potential_diagnosis.append(diseases[disease]['disease'])
		print(potential_diagnosis)
	return potential_diagnosis
				

#what_are_your_symptoms()






