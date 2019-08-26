import json
from pprint import pprint

def transformDisease():
	with open('../rawdata/disease.json') as f:
		diseases = json.load(f)
		intents = []
		for dID in diseases:
			tags = diseases[dID]["disease"]
			for tag in tags:
				diseaseIntent = {}
				diseaseIntent["tag"]=tag
				diseaseIntent['patterns']=diseases[dID]["symptoms"]
				response = "It looks like you may have "+diseases[dID]["disease"][0]
				diseaseIntent["responses"]=["We will be with you as soon as we can",response]
				intents.append(diseaseIntent)
			
		intents_dictionary ={}
		intents_dictionary["intents"]=intents
		pprint(intents_dictionary)

	with open('../intents/intents.json', 'w') as fs:
		json.dump(intents_dictionary,fs)

#transformDisease()


def transformHealthTap():
	with open('../rawdata/ehealth.json') as f:
		questAns = json.load(f)
		with open('../intents/intents.json') as fs:
			data = json.load(fs)
			originalIntents=data["intents"]
			for qa in questAns:
				tags = qa['tags']
				if len(tags) != 0:
					for tag in tags:
						flag=False
						for i in originalIntents:
						#print(i)
							if i["tag"]==tag:
								if qa["question"] not in i["patterns"]:
					
									i["patterns"].append(qa["question"])
								if qa["answer"] not in i["responses"]:
								
									i["responses"].append(qa["answer"])
								flag=True
						if flag == False:
							qaIntent = {}
							qaIntent["tag"]=tag
							qaIntent["patterns"]=[qa["question"]]
							qaIntent["responses"]=[qa["answer"]]
							originalIntents.append(qaIntent)

			
		intents_dictionary ={}
		intents_dictionary["intents"]=originalIntents
		pprint(intents_dictionary)
	with open('../intents/intents.json', 'w') as fs:
		json.dump(intents_dictionary,fs)
	
transformHealthTap()
