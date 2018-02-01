#!/opt/local/bin/python3.2
# -*- encoding: utf-8 -*-

import sys
import json

sys.path.append('.../myfreeling/APIs/python')
import freeling
import codecs
import re
import time
from datetime import date

FREELINGDIR = "/usr/local"
DATA = FREELINGDIR+"/share/freeling/"
LANG="pt"

freeling.util_init_locale("default") 

op = freeling.maco_options("pt")
op.set_active_modules(1,1,1,1,1,1,1,1,1,1,0)
op.set_data_files("usermap.dat",
                  DATA+LANG+"/locucions.dat", 
                  DATA+LANG+"/quantities.dat", 
                  DATA+LANG+"/afixos.dat",
                  DATA+LANG+"/probabilitats.dat", 
                  DATA+LANG+"/dicc.src", 
                  DATA+LANG+"/np.dat",  
                  DATA+"common/punct.dat", 
                  "")
op.set_retok_contractions(False)

lg  = freeling.lang_ident(DATA+"common/lang_ident/ident-few.dat")
mf  = freeling.maco(op)
tk  = freeling.tokenizer(DATA+LANG+"/tokenizer.dat")
sp  = freeling.splitter(DATA+LANG+"/splitter.dat")
tg  = freeling.hmm_tagger(DATA+LANG+"/tagger.dat",1,2)
sen = freeling.senses(DATA+LANG+"/senses.dat");
ukb = freeling.ukb(DATA+LANG+"/ukb.dat")

def tag (obj):
    sent = obj["text"]
    out = obj
    lang = lg.identify_language(sent)
    l = tk.tokenize(sent)
    ls = sp.split(l,1) # old value 0
    ls = mf.analyze(ls)
    ls = tg.analyze(ls)
    wss = []
    for s in ls:
        ws = s.get_words()
        for w in ws:
            an = w.get_analysis()
            a = an[0]
            wse = dict(wordform =  w.get_form(),
                       lemma = a.get_lemma(),
                       tag = a.get_tag(),
                       prob = a.get_prob(),
                       analysis = len(an))
            wss.append(wse)
    out['words'] = wss
    out['lang'] = lang
    return out

if (len(sys.argv) > 1):
    file= sys.argv[1]
else:
    print("Please give an input filename (with text in utf8)")
    sys.exit(1)

f = codecs.open(file, "r", "utf-8" )
input = json.load(f)
tweets = []
for s in input:
    tweets.append(tag(s))

with open(sys.argv[2], 'w') as outfile:
    json.dump(tweets, outfile, indent=2)
    
