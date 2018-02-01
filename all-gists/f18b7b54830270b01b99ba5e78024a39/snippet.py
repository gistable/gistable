import graphlab as gl
import pandas
import numpy as np
import string
import re
import unicodedata
import math
# attempt to load text files
import os
files = os.listdir(os.getcwd())
def get_word_vector(file_name):
    word_dict = {}
    file_object = open(file_name,'r')
    file_text = file_object.readlines()
    file_object.close()
    final_text = ""
    replace_punctuation = string.maketrans(string.punctuation, ' '*len(string.punctuation))
    for line in file_text:
        new_line = line.decode('utf8', 'replace').encode('ascii', 'replace')
        new_line = new_line.translate(replace_punctuation).lower()
        final_text = final_text + new_line.strip()
    
    word_list = final_text.split()

    for word in word_list:
        if word_dict.has_key(word):
            word_dict[word] = word_dict[word]+1
        else:
            word_dict[word] = 1
    return word_dict
text_files = []
for a_filename in files:
    if a_filename.find(".txt") >0:
        text_files.append(a_filename)
word_lists = {}

for a_file in text_files:
    word_lists[a_file] = get_word_vector(a_file)

textFrame={}
for key in word_lists.keys():
    textFrame[key] = gl.SFrame({'words':word_lists[key].keys(), 'count': word_lists[key].values()})

for key in textFrame.keys():
    textFrame[key]['filename'] = key


for i in range(0,len(text_files)):
    if i == 0:
        all_files = textFrame[text_files[i]]
    else:
        all_files = all_files.append(textFrame[text_files[i]])


word_df = all_files.groupby(['words'],{'df':gl.aggregate.COUNT()})

all_files = all_files.join(word_df,on='words')

all_files['tf_idf'] = all_files.apply(lambda x: x['count']/(math.log(1+x['df'])))

word_corpus = all_files['words'].unique()

word_corpus = gl.SFrame({'words':word_corpus})

def get_cosine_similarity(file1, file2):
    doc1 = all_files[all_files['filename']==file1]
    doc2 = all_files[all_files['filename']==file2]
    compare_vec = word_corpus.join(doc1[['words', 'tf_idf']], on='words', how='left')
    compare_vec = compare_vec.rename({'tf_idf':'file1_tf_idf'})
    compare_vec = compare_vec.join(doc2[['words', 'tf_idf']], on='words', how='left')
    compare_vec = compare_vec.rename({'tf_idf':'file2_tf_idf'})
    compare_vec = compare_vec.fillna('file1_tf_idf',0.0)
    compare_vec = compare_vec.fillna('file2_tf_idf',0.0)
    compare_vec['xx'] = compare_vec.apply(lambda x: x['file1_tf_idf']**2)
    compare_vec['yy'] = compare_vec.apply(lambda x: x['file2_tf_idf']**2)
    compare_vec['xy'] = compare_vec.apply(lambda x: x['file1_tf_idf']*x['file2_tf_idf'])
    compare_vec = compare_vec.groupby([],{'sumxy':gl.aggregate.SUM('xy'), 'sumxx':gl.aggregate.SUM('xx'),'sumyy':gl.aggregate.SUM('yy')})
    return compare_vec[0]['sumxy']/(math.sqrt(compare_vec[0]['sumxx']*compare_vec[0]['sumyy']))

similarity_all = {}

for i in range(0,len(text_files)-1):
    similarity = {}
    for j in range(i+1,len(text_files)):
        similarity[text_files[j]] = get_cosine_similarity(text_files[i],text_files[j])
    similarity_all[text_files[i]] = similarity


similarity_frames={}
for key in similarity_all.keys():
    similarity_frames[key]=gl.SFrame({'file2':similarity_all[key].keys(), 'similarity':similarity_all[key].values()})

for key in similarity_frames.keys():
    similarity_frames[key]['file1'] = key

similarity_keys = similarity_frames.keys()
for i in range(0,len(similarity_keys)):
    if i == 0:
        all_similarity = similarity_frames[similarity_keys[i]]
    else:
        all_similarity = all_similarity.append(similarity_frames[similarity_keys[i]])


data_frame_similarity = all_similarity.to_dataframe()

