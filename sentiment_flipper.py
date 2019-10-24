import config #the config file with the API keys and passwords
import numpy as np 
import functools
import csv
import collections
import re
import os
import glob
import spacy 
import operator
import time
from spacy.matcher import Matcher
from nltk.corpus import wordnet

# stuff needed for Google Pespective API
import json 
import requests 
import nltk

#import MySQLdb
import mysql.connector

#API key for Google Perspective for toxicity scores
api_key = config.api_key_toxicity

nlp = spacy.load("en_core_web_sm")

#check if the word is negative or not
def check_if_neg(string):
	doc = open('Negative_Adjectives.txt', 'r')
	neg_adj_list = doc.readlines()
	doc.close()
	check = False

	for neg_adj in neg_adj_list:
		if string.lower()+"\n" == neg_adj:
			check = True
			# print(" ----- Found negative word match :  -----")
			# print(string.lower()+"\n")
			# print(neg_adj)
	# print("Negative word found : "+str(check))

	return check


#find the antonym for the adjective
def find_ant(string,w2):
	# NAIMA'S stuff
	#create lists for antonyms
	#syn = list()
	ant_list = list()
	for synset in wordnet.synsets(string):
	   for lemma in synset.lemmas():
	    #  print(lemma)
	    #  syn.append(lemma.name())    #add the synonyms
	       if lemma.antonyms():    #When antonyms are available, add them into the list
	        ant_list.append(lemma.antonyms()[0].name())
	      # else:
	          #ant.append("good")

	#print('Synonyms: ' + str(syn))
	# print('Antonyms: ' + str(ant))
	print()
	print("ant_list : ",ant_list)
	if ant_list:
		best_ant = best_ant_bigrams(ant_list,w2)
	else:
		return "Not Found"


	if not best_ant:
		# print("ant is empty")
		return "Not Found"
	else:
		#return ant[0]
		return best_ant



#replace the word with its antonym if it is adjective and negative, and if it has an antonym
def replace_adj(string, w2):
	#print(w2)
	matcher = Matcher(nlp.vocab)
	# optional adverb + mandatory adjective
	#pattern = [{"POS": "ADV", "OP": "*"},{"POS": "ADJ"}]
	pattern = [{"POS": "ADJ"}]
	matcher.add("ID", None, pattern)
	doc = nlp(string)
	matches = matcher(doc)
	for match_id, start, end in matches:
	    span = doc[start:end]
	    # if the found adjective is negative, then continue replacement, 
	    # if not then just return the adjective
	    print("span.text : ",span.text)
	    if check_if_neg(span.text):	  
		    ant = find_ant(span.text,w2)
		    #if antonym is found, replace the original word with the antonym, 
		    #otherwise keep the original word

		    if ant != "Not Found":
		    	string = re.sub(span.text, ant.upper(), string)

	return string


#remove negations
def remove_not(string):
	tokens = [token for token in nlp.tokenizer(string)]
	#print(tokens)
	return_string = ""
	for token in tokens:
		if str(token).lower() != "not":
			return_string += str(token)+" "

	#print(return_string)
	return return_string

#check if the word is a swearword
def check_if_swearing(string):
	doc = open('swearWords.txt', 'r')
	swear_list = doc.readlines()
	doc.close()
	check = False

	for swear in swear_list:
		if string.lower()+"\n" == swear:
			check = True
	return check

#remove the words if they are identified as swearwords
def remove_swearing(string):
	tokens = [token for token in nlp.tokenizer(string)]
	#print(tokens)
	return_string = ""
	for token in tokens:
		if not check_if_swearing(str(token).lower()):
			return_string += str(token)+" "

	#print(return_string)
	return return_string




# Tokenising all text 
def get_tokens(files):
	doc_tokens = []

	for file in files:
		doc = open(file, "r")
		tokens = [token for token in nlp.tokenizer(doc.read())]
		doc.close()
		#print(tokens)
		for token in tokens:
			if re.search("[a-zA-Z0-9,.!?]", str(token)):
				doc_tokens.append(token)
	#print("DOC_TOKENS")
	#print(doc_tokens)
	return doc_tokens

#get toxicity score of a string with a call to Google Perspective
def get_toxicity(string):
	url = ('https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze' +    
	    '?key=' + api_key)
	data_dict = {
	    'comment': {'text': string},
	    'languages': ['en'],
	    'requestedAttributes': {'TOXICITY': {}}
	}
	response = requests.post(url=url, data=json.dumps(data_dict)) 
	response_dict = json.loads(response.content) 
	if response_dict is None:
		toxicity_score = 0
	else:
		toxicity_score = response_dict["attributeScores"]["TOXICITY"]["summaryScore"]["value"]


	return toxicity_score
	#return 0.55


# run the input sentences through 
# the Google Perspective API and list a toxicity score f
# or each one of them in format 
# "text string"<tab>score
def toxicity_per_sentence(input_file , output_file):
	doc = open(input_file, 'r')
	string_list = doc.readlines()
	#print("string list")
	#print(string_list)
	doc.close()

	#remove " \n" from the strings
	string_list2 = []
	for string in string_list:
		string = re.sub(r'\n', "", string)
		string_list2.append(string)

	# run the strings throug Google Perspective
	# and write each string + toxicity score to a file before.txt
	output =open(output_file,"w+") 
	#slower = 1
	for string in string_list2:
		#slower += 1
		#if slower == 100:
			#time.sleep(150)

		toxicity_score = get_toxicity(string)
		output.write(string+"\t"+str(toxicity_score)+"\n")

	output.close()

#count average toxicity of all the sentences in the given file
def average_toxicity(file):
	doc = open(file, 'r')
	string_list = doc.readlines()
	doc.close()
	text = glob.glob('./'+file)
	tokens = get_tokens(text)
	# count the number orf strings in total
	n = 0
	for string in string_list:
		n += 1

	average = 0
	for token in tokens:
		token_s = str(token)
		if re.search("\d+\.\d+", token_s):
			average += float(token_s)	
	average = average / n
	return average



#find the best fitting antonym to an adjective based on bigram frequencies of antonym + word2 from
#a database provided by University of Twente, the Netherlands
#select the antonym with highest bigram frequency
def best_ant_bigrams(w1_list,w2):
	mydb = mysql.connector.connect(
	host= config.bigrams_host,
	user= config.bigrams_user,
	passwd=config.bigrams_passwd,
	database=config.bigrams_database,
	)

	cHandler = mydb.cursor()
	#Some explanation on how the bigram database works
	# everything in the database is lowercase
	#cHandler.execute("select id,w from vocabulary where w='word';")
	#cHandler.execute("select id,w from vocabulary where w='word' or w='single' or w='multiple';")
	
	# THIS ONE IS GOOD: cHandler.execute("select w1,w2,f from 2grams where (w1=1229 and w2=820) OR (w1=588 and w2=820);")
	#cHandler.execute("select w1,w2,f from 2grams where (w1=1229 and w2=820) OR (w1=588 and w2=820);")

	#save query results in a table to avoid multiple calls to database
	#results = cHandler.fetchall()
	# [(588, 820, 598404), (1229, 820, 19744)]
	# [(w1_id, w2_id, freq), (w1_id, w2_id, freq)]
	#print(results)
	#for items in results:
		#print(items[2])

	#do if antonyms are found
	cHandler.execute("select id,w from vocabulary where w='"+w2+"';")
	w2_id_word = cHandler.fetchall()[0]
	print("w2 : ",w2_id_word)

	w2_id = w2_id_word[0]

	if w1_list:
		#build a query string for 2grams database
		i = 0
		query = "select w1,w2,f from 2grams where "
		for w1 in w1_list:
			cHandler.execute("select id,w from vocabulary where w='"+w1+"';")
			w1_id_word = cHandler.fetchall()[0]
			print("w1 : ",w1_id_word)
			w1_id = w1_id_word[0]

			if i < len(w1_list)-1:
				query += "(w1="+str(w1_id)+" and w2="+str(w2_id)+") OR "
				i += 1
			else:
				query += "(w1="+str(w1_id)+" and w2="+str(w2_id)+")"
				i += 1


			

		query += ";"
		print(query)

		#execute the query
		cHandler.execute(query)
		results = cHandler.fetchall()
		print("query results : ",results)

	else:
		results = "Not Found"
		print("query results not found: ",results)

	max_freq = 0


	if results != "Not Found" and len(results) >= 1:
		check = 0
		for bigram in results:
			print("bigram ",bigram)
			if(max_freq < bigram[2]):
				max_freq = bigram[2]
				best_ant_id = bigram[0]
				check = 1


		#fetch the best word
		if check == 1:
			cHandler.execute("select id,w from vocabulary where id="+str(best_ant_id)+";")
			best_ant = cHandler.fetchall()
			print("best ant" , best_ant)
			return best_ant[0][1]


	else:
		if w1_list:
			return w1_list[0]
		else:
			return None


#main program combining the use of all the methods above
def main():

	print( "START --> ")

	toxicity_per_sentence('input.txt', 'before.txt')

	input_text = glob.glob('./input.txt')
	#files_neg = glob.glob('./movies/train/N*.txt')

	#tokenize the input text
	input_tokens = get_tokens(input_text)
	#print(" -- input tokens --- ")
	#print(input_tokens)


	result =open("output.txt","w+") 
	result_string = ""
	i = 0
	#put tokens back to strings and write them to output.txt
	for token in input_tokens:
			if i+1 < len(input_tokens):
				w2 = str(input_tokens[i+1]).lower()
			else:
				w2 = "\s"
			# here replace the token with an antonym if needed

			token_s = str(token)
			token_s = remove_not(token_s)
			token_s = remove_swearing(token_s)
			token_s = replace_adj(token_s,w2)
			#token_s = re.sub(r'a', "A", token_s)


			if re.search("[.!?]", token_s):
				result_string += token_s+"\n"
				result.write(result_string)
				result_string = ""
				#result.write(token+"\n")
			else:
				#if re.search("[A-Z,]",token_s[0]):
					#result_string += token_s
				#else:
					#result_string += " "+token_s
				result_string += " "+token_s
				#result.write(token+" ")


			i += 1


	result.close()

	toxicity_per_sentence('output.txt', 'after.txt')

	#compute the average toxicity before and after our sentiment flipper
	toxicity_before = average_toxicity('before.txt')
	toxicity_after = average_toxicity('after.txt')
	print("Toxicity before : "+ str(toxicity_before))
	print("Toxicity after : "+ str(toxicity_after))

	print("DONE :--D")


# --------- TESTING THE CODE -------------- #

main()
#bigrams("good","person")

#remove_not("This is not fun!")
#remove_not("Not good.")
#check_if_neg("Bad")

#get_toxicity('what kind of idiot name is foo?')









