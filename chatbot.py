# started 19 Sept 2018 at 3:27 AM (2nd Year ECE)

# Training a Deep NLP Chatbot with Movie-Lines

#importing libraries
import numpy as np; 
import tensorflow as tf;                
import re;   #regex
import time; #training time measurement

#...................................... Part 1 - "Preprocessing" the Data ......................................

# Datasets 
lines=open("movie_lines.txt",encoding = 'utf-8',errors='ignore').read().split('\n'); # list of movie-lines (MLs) w/ unique ID#                  
conversations=open("movie_conversations.txt",encoding='utf-8',errors='ignore').read().split('\n');  # (sets of line-IDs [conversations]) form crucial training data 

# Dictionary: mapping line-ID to Line  
id2line = {}
for l in lines:                             
    _line = l.split(' +++$+++ ')  
    if len(_line)==5: # do not map blank-lines 
        id2line[_line[0]] = _line[4] 

# List (of Lists): Line-Groups/Conversations
conversations_ids = []
for conversation in conversations[:-1]: 
    _conv = conversation.split(" +++$+++ ")[-1][1:-1].replace("'","").replace(" ","") #noise-removal
    conversations_ids.append(_conv.split(','))

# Lines are split between Qs & As (mirror lists)
questions = []
answers = []
for conv in conversations_ids:
    for i in range(len(conv)-1):
            questions.append(id2line[conv[i]])
            answers.append(id2line[conv[i+1]])        
    if(len(questions) > len(answers)):
        answers.append("no comment")    # Preventing [Q's w/o A's] from de-aligning lists   
        
# Q&A-text is simplified to "vanilla"
def clean(text):
    text = text.lower()
    # contractions are rm'd
    text = re.sub(r"n't"," not", text);  			text = re.sub(r"'re"," are", text)
    text = re.sub(r"'m"," am", text); 	 			text = re.sub(r"'ll"," will", text)
    text = re.sub(r"'ve"," have", text); 			text = re.sub(r"'d"," would", text)
    # families ↑ , specifics ↓ 
    text = re.sub(r"i'm","i am", text);				text = re.sub(r"she's","she is", text)
    text = re.sub(r"he's","he is", text);			text = re.sub(r"what's","what is", text)
    text = re.sub(r"where's","where is", text);		text = re.sub(r"how's","how is", text)
    text = re.sub(r"who's","who is", text);			text = re.sub(r"won't","will not", text)
    text = re.sub(r"can't","can not", text)
    text = re.sub(r"[-()\"#/@;:<>{}`+=~|.!?,]","",text) #abolished symbols list
    return text
for thing in range(len(questions)): # text-formatting is applied
    questions[thing],answers[thing] = clean(questions[thing]), clean(answers[thing])

# freq. of words (in corpus) are computed
word2freq = {}
def count(dictionary, sentences):
    for sent in sentences:
        for word in sent.split(' '):
            if word not in dictionary:
                dictionary[word] = 1
            else:
                dictionary[word] += 1
count(word2freq, questions)
count(word2freq, answers) 

# Words are mapped to a unique-identifying integer (data compression)
qWord2code, aWord2code = {}, {}       # the vocabulary for Q-interp & A-generation may vary 
qThreshhold, aThreshhold = 20, 20     # decrease training-time by discarding in-frequent words 
qWord_num, aWord_num = 0, 0 

# non-frequent words are "forgotten" to speed-up training
for word, freq in word2freq.items():
    if(freq > qThreshhold):
        qWord2code[word] = qWord_num
        qWord_num += 1
    if(freq > aThreshhold):
        aWord2code[word] = aWord_num
        aWord_num += 1

tokens = ['<PAD>','EOS','OUT','SOS'] # special tokens in list
for token in tokens:
	qWord2code[token] = len(qWord2code) + 1
	aWord2code[token] = len(aWord2code) + 1
 
# Inverse mapping (form index to word) is facilitated 
Anum2word = {index : word , for word, index in aWord2code.items()}
# <EOS> is appended to each answer 
for ans in range(len(answers)): answers[ans] += ' <EOS>'	# EOS token @ end of each answer

# Q&As are simplified to contain equivalent-Integer-IDs instead of Words
def compress_word_to_int(inputList):
	outList = []
	for sentence in inputList:
		ints = []
		for word in sentence.split(' '):
			if word not in qWord2code:	# voided word
				ints.append(qWord2code['<OUT>'])
			else: ints.append(qWord2code[word])
		outList.append(ints)
	return outList
questions_compressed = compress_word_to_int(questions)
answers_compressed = compress_word_to_int(answers)


# Sort Q's & A's by [length of question] to speeden training    ---------------  Test this!
sorted_questions = []
sorted_answers = []
# Ignore null-qustions & questions w/ +24 words
for question_length in range(1 : 25 + 1):
    for question in enumerate(questions_compressed):
        if(question[1] == l):
            sorted_questions.append(questions_compressed[q[0]])
            sorted_answers.append(answers_compressed[q[0]])