# started 19 Sept 2018 at 3:27 AM (2nd Year ECE)

# Training a Deep NLP Chatbot with Movie-Lines

#importing libraries
import numpy as np; 
import tensorflow as tf;                
import re;   #regex
import time; #training time measurement


#...................................... Part 1 - "Preprocessing" the Data ......................................
# Datasets 
lines=open("movie_lines.txt",encoding = 'utf-8',errors='ignore').read().split('\n'); # list: movie-lines (MLs) have unique ID#                  
conversations=open("movie_conversations.txt",encoding='utf-8',errors='ignore').read().split('\n');  # (sets of ID#s [conversations]) form crucial training data 

# Dictionary: ID-to-Line map 
id2line = {}
for l in lines:                             
    _line = l.split(' +++$+++ ')  
    if len(_line)==5: # skip blank-lines
        id2line[_line[0]] = _line[4] 

# List (Type List): Conversations
conversations_ids = []
for conversation in conversations[:-1]: 
    _conv = conversation.split(" +++$+++ ")[-1][1:-1].replace("'","").replace(" ","") #noise-removal
    conversations_ids.append(_conv.split(','))

# Mirror Qs & As as separate Lists
questions = []
answers = []
for conv in conversations_ids:
    for i in range(len(conv)-1):
            questions.append(id2line[conv[i]])
            answers.append(id2line[conv[i+1]])        
    if(len(questions) > len(answers)):
        answers.append("no comment")    # Preventing [Q's w/o A's] from de-aligning lists   
        
# process text into its "vanilla form" 
def clean(text):
    text = text.lower()
    # removing contractions
    text = re.sub(r"n't"," not", text)
    text = re.sub(r"'re"," are", text)
    text = re.sub(r"'m"," am", text)
    text = re.sub(r"'ll"," will", text)
    text = re.sub(r"'ve"," have", text)
    text = re.sub(r"'d"," would", text)
    # specifics
    text = re.sub(r"i'm","i am", text)
    text = re.sub(r"she's","she is", text)
    text = re.sub(r"he's","he is", text)
    text = re.sub(r"what's","what is", text)
    text = re.sub(r"where's","where is", text)
    text = re.sub(r"how's","how is", text)
    text = re.sub(r"who's","who is", text)
    text = re.sub(r"won't","will not", text)
    text = re.sub(r"can't","can not", text)
    text = re.sub(r"[-()\"#/@;:<>{}`+=~|.!?,]","",text) # manipulate this later
    #text = re.sub(r"[~!@#$%^&*\"\'()-=_+{}[]|\:;\"\'`<>,?.]","", text)      
    return text

# apply text-formatting on all MLs
for thing in range(len(questions)):
    questions[thing] = clean(questions[thing])
    answers[thing] = clean(answers[thing])

# determine freq. of each word (in corpus) to eliminate trivial ones
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
    

    