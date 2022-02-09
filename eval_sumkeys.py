import glob
from pydoc import doc
import sys
import os
import random

import rouge_stats as rs
import key_stats as ks
from itertools import islice

import textcrafts
from textcrafts import deepRank as dr
from textcrafts.sim import *

from systems.textstar import Textstar
from systems.stanzagraphs import StanzaGraphs

from dataset.Krapivin2009 import Karpivin2009
from dataset.cnn_big import CnnBig
from dataset.nus import NUS

# SETTINGS ------------------------------------------------

# number of keyphrases and summary sentences
#wk,sk=6,6
#wk,sk=10,9
# wk,sk=14,9 #best
wk, sk = 10, 8

# max number of documents to process (None to process all)
max_docs = 30

# 2 forces deletion of json in temp_dir, 1=forces deletion of keys+abs
force=2

#Stop running on errors
show_errors=True

# shows moving averages if on
trace_mode=False

# choice of NLP summarizer and key-word extractor
# SYSTEM = StanzaGraphs(
#   stanza_path="/Users/brockfamily/Documents/UNT/StanzaGraphs/"
# )
SYSTEM = Textstar(
  stanza_path="/Users/brockfamily/Documents/UNT/StanzaGraphs/"
)

# choice of dataset
# DATASET = Karpivin2009(
#   path="dataset/Krapivin2009/",
#   count=max_docs,
#   include_abs=True,
#   direct=True
# )
# DATASET = CnnBig(
#   path="dataset/cnn_big/",
#   count=max_docs
# )
DATASET = NUS(
  path="dataset/NUS/",
  count=max_docs,
  include_abs=False
)

# SETTINGS ------------------------------------------------



out_dir =  DATASET.path + "out/"
out_abs_dir  = out_dir + "abs/"
out_keys_dir = out_dir + "keys/"
temp_dir = DATASET.path + 'temp_docs/'


# sizes of silver abs and keys will match sizes in gold
# match_sizes = False


'''
#NUS

data_dir = 'dataset/NUS/' 
doc_dir=data_dir+'docsutf8_noAbstract/'
DIRECT=True
'''
'''
#SemEval2010_full

data_dir = 'dataset/SemEval2010_full/test/' 
doc_dir=data_dir+'docsutf8_noAbstract/'
DIRECT=True
'''

#arxiv-dataset
'''
data_dir = 'dataset/arxiv-dataset/'
doc_dir=data_dir+'docsutf8/'
DIRECT=True
'''
#pubmed-dataset
'''
data_dir = 'dataset/PubMed/'
doc_dir=data_dir+'docsutf8/'
DIRECT=True
'''

if DATASET.has_kwds:
  print('keyfiles_count: ', DATASET.count)

# clean output directories
def clean_all() :
  os.makedirs(out_dir,exist_ok=True)
  os.makedirs(out_abs_dir,exist_ok=True)
  os.makedirs(out_keys_dir,exist_ok=True)
  os.makedirs(temp_dir,exist_ok=True)
  if not force : return
  if sys.platform != 'win32':
    #linux
    clean_path(out_abs_dir)
    clean_path(out_keys_dir)
    if force>1 : clean_path(temp_dir)
  else:
    #windows
    clean_path(out_abs_dir + '/docsutf8/')
    clean_path(out_keys_dir + '/docsutf8/')
    if force>1 : clean_path(temp_dir + '/docsutf8/')

def clean_temp() :
  if not force : return
  clean_path(temp_dir)

# clean files at given directory path 
def clean_path(path) :
  if not force : return
  os.makedirs(path,exist_ok=True)

  files = glob.glob(path+"/*")
  for f in files:
    os.remove(f)


def customGraphMaker():  # CHOICE OF PARSER TOOLKIT
  return dr.GraphMaker(params=dr.params)
  # return dr.GraphMaker(api_classname=CoreNLP_API)

# extract triple (title,abstract,body) with refs trimmed out
# def disect_doc(doc_file) :
#   title=[]
#   abstract=[]
#   body=[]
#   mode=None
#   with open(doc_file) as f:
#     for line in f:
#       if line.startswith('--T')   : mode='TITLE'
#       elif line.startswith('--A') : mode ='ABS'
#       elif line.startswith('--B') : mode = 'BODY'
#       elif line.startswith('--R'): mode = 'DONE'
#       else :
#         if   mode=='TITLE': title.append(line.strip()+' ')
#         elif mode=='ABS'  : abstract.append(line.strip()+' ')
#         elif mode=='BODY' : body.append(line.strip()+' ')
#         elif mode=='DONE' : break
#   return {'TITLE':title,'ABSTRACT':abstract,'BODY':body}

# process string text give word count,sentence count and filter
# def runWithText(text,wk,sk,filter) :
#   gm=customGraphMaker()
#   gm.digest(text)
#   keys= gm.bestWords(wk)
#   sents=[s for (_,s) in gm.bestSentences(sk)]
#   #keys_text=interleave_with('\n','\n',keys)
#   #sents_text=interleave_with('\n','\n',sents)
#   #return (keys_text,sents_text)
#   nk=gm.nxgraph.number_of_nodes()
#   vk=gm.nxgraph.number_of_edges()
#   return (keys,sents,nk,vk)

# def runWithTextAlt(fname,wk,sk, filter) :
#   params = talk_params()
#   params.top_sum=sk
#   params.max_sum = params.top_sum*(params.top_sum-1)/2
#   params.top_keys=wk  
#   params.max_keys = 1+2*params.top_keys
#   talker=Talker(from_file=fname,params=params)
#   ranked_sents=talker.get_summary()
#   keys=talker.get_keys()
#   def clean_sents():
#     for r, s, ws in ranked_sents:
#       yield ws

#   #print('!!!KEYS',keys)
#   #print('!!!SENT',list(clean_sents()))
#   keys=nice_keys(keys)
#   return (keys,clean_sents(),talker.g.number_of_nodes(),talker.g.number_of_edges())


# def runWithText_StanzaGraphs(fname, wk, sk):  
#   fname = fname[:-4]
#   print('runWithText_StanzaGraphs:',fname)
#   '''
#   # summarizer.py  
#   nlp = Summarizer() #new
#   nlp.from_file(fname)
#   kws, _, sents, _ = nlp.info(wk, sk)
#   '''
#   '''
#   #refiner.py
  
#   nlp = process_file_with_sims(fname=fname)
#   kws, _, sents, _ = nlp.info(wk, sk)
#   '''
  
#   #textstar/textstar.py
#   with open(fname + ".txt", 'r') as f:
#     text = f.read()
#   sentids, kws = process_text(
#         text=text,
#         ranker=nx.pagerank,
#         kwsize=wk,
#         sumsize=sk)
#   sents = [s for _,s in sentids]
#   print('runWithText_StanzaGraphs, kws:\n', kws)
#   print('runWithText_StanzaGraphs, sents:\n', sents) 
  
#   return (kws,sents)

# def runWithPyTR(text,wk,sk,filter) :

#   talker=Talker(from_file=fname)
#   ranked_sents,keys=talker.extract_content(sk,wk)

#   def clean_sents():
#     for r, s, ws in ranked_sents:
#       yield ws

#   #print('!!!KEYS',keys)
#   #print('!!!SENT',list(clean_sents()))
#   keys=nice_keys(keys)
#   return (keys,clean_sents(),talker.g.number_of_nodes(),talker.g.number_of_edges())

     
# turns a sequence/generator into a file, one line per item yield     
def seq2file(fname,seq) :
  xs=map(str,seq)
  ys=interleave_with('\n','\n',xs)
  text=''.join(ys)

  string2file(fname,text)

# turns a file into a (string) generator yielding each of its lines
def file2seq(fname) :
   with open(fname,'r', encoding='utf8') as f :
     for l in f : yield l.strip()

# turns a string into given file
def string2file(fname,text) :

  with open(fname,'w', encoding='utf8') as f :  
    f.write(text)

# turns content of file into a string
def file2string(fname) :
  try :
    with open(fname,'r', encoding='utf8') as f :
      s = f.read()
      return s.replace('-',' ')
  except:
    return None

# interleaves list with separator
def interleave(sep,xs) :
  return interleave_with(sep,None,xs)
  
def interleave_with(sep,end,xs) :
  def gen() :
    first=True
    for x in xs : 
      if not first : yield sep
      yield x
      first=False
    if end : yield(end)
      
  return ''.join(gen())

def process_file(document,wk,sk):
  doc_file = document.fname
  kf = out_keys_dir + doc_file
  af = out_abs_dir + doc_file

  keys, exabs = SYSTEM.process_text(
    document,
    summarize=True,
    key_words=True,
    sum_len=sk,
    kwds_len=wk
  )

  seq2file(kf, keys)
  seq2file(af, exabs)


# extracts keys and abstacts from resource directory  
def extract_keys_and_abs(wk,sk,show_errors=show_errors) :
  clean_all()
  
  for i, document in enumerate(DATASET):
    if show_errors:
      process_file(document, wk, sk)
    else:
      try :
        process_file(document, wk, sk)
      except :
        print('*** FAILING on:', document, 'ERROR:', sys.exc_info()[0])
  
# apply Python base rouge to abstracts from given directory
def eval_with_rouge(i) :
  files=[]
  f=[]
  p=[]
  r=[]  
  for document in DATASET:
    fname = document.fname
    abs_name=out_abs_dir+fname
    #if trace_mode : print(fname)
    gold = document.summary()   
    silver=file2string(abs_name)
    
    if not silver:
      print('silver file missing:', abs_name)
      continue
    k=0
    for res in rs.rstat(silver,gold) :
      if k==i:    
        d=res[0]
      
        px=d['p'][0]
        rx=d['r'][0]
        fx=d['f'][0]

        files.append(fname)
        p.append(px)
        r.append(rx)
        f.append(fx)
        
      elif k>i : break
      k+=1
    if trace_mode : print('  ABS ROUGE MOV. AVG',i,fname,avg(p),avg(r),avg(f))
  rouge_name=(1,2,'l','w')  
  print ("ABS ROUGE",rouge_name[i],':',avg(p), '  ' , avg(r), '  ', avg(f))

  #save ABS ROUGE scores into file
  content = 'fileName, Precision, Recall, F-Measure' + '\n'
  content += score2txt(files, p, r, f)
  toFile = "AbsRouge_" + str(rouge_name[i]) + ".csv"
  string2file(out_abs_dir + toFile, content)



# apply Python base rouge to abstracts from given directory
def keys_with_rouge(i):
  files = []
  f = []
  p = []
  r = []
  for document in DATASET:
    fname = document.fname
    abs_name = out_keys_dir + fname
    #if trace_mode : print(fname)
    gold = document.key_words()
    silver = file2string(abs_name)
    
    if not silver:
      print('silver file missing:', abs_name)
      continue
    k = 0
    for res in rs.rstat(silver, gold):
      if k == i:
        d = res[0]

        px = d['p'][0]
        rx = d['r'][0]
        fx = d['f'][0]

        files.append(fname)
        p.append(px)
        r.append(rx)
        f.append(fx)

      elif k > i:
        break
      k += 1
    if trace_mode: print('  ABS ROUGE MOV. AVG', i, fname, avg(p), avg(r), avg(f))
  rouge_name = (1, 2, 'l', 'w')
  print("KEYS ROUGE", rouge_name[i], ':', avg(p), '  ', avg(r), '  ', avg(f))

  #save KEYS ROUGE scores into file
  content = 'fileName, Precision, Recall, F-Measure' + '\n'
  content += score2txt(files, p, r, f)
  string2file(out_keys_dir + 'KeysRouge.csv',content)



# our own
def eval_abs() :
  files = []
  f=[]
  p=[]
  r=[]  
  for document in DATASET :
    fname = document.fname
    abs_name=out_abs_dir+fname
    gold = document.summary()
    silver=file2string(abs_name)
    
    if not silver:
      print('silver file missing:', abs_name)
      continue
    #print(gold)
    #print(silver)
    d=ks.kstat(silver,gold)
    if not d :
      print('FAILING on',fname)
      continue
    if trace_mode: print('  ABS SCORE:',d)
    px=d['p']
    rx=d['r']
    fx=d['f']
    if px and rx and fx :
      files.append(fname)
      p.append(px)
      r.append(rx)
      f.append(fx)
    if trace_mode : print('  ABS MOV. AVG',fname,avg(p),avg(r),avg(f))
  print ("ABS SCORES  :",avg(p),avg(r),avg(f))

  #save ABS SCORES into file
  content = 'fileName, Precision, Recall, F-Measure' + '\n'
  content += score2txt(files, p, r, f)
  string2file(out_abs_dir + 'AbsScores.csv',content)


  
# 0.22434732994628803 0.24271988542882067 0.22280040709372084
def eval_keys() :
  files = []
  f=[]
  p=[]
  r=[]  
  for document in DATASET:
    fname = document.fname
    keys_name=out_keys_dir+fname
    #if trace_mode : print(fname) 
    gold = document.key_words()
    silver=file2string(keys_name)
    
    if not silver:
      print('silver file missing:', keys_name)
      continue
    #print(gold)
    #print(silver)
    d=ks.kstat(silver,gold)
    if not d :
      print('FAILING on',fname)
      print('SILVER',silver)
      print('GOLD',gold)
      continue
    if trace_mode : print('  KEYS',d)    
    px=d['p']
    rx=d['r']
    fx=d['f']
    files.append(fname)
    p.append(px)
    r.append(rx)
    f.append(fx)
    #if trace_mode : print('  KEYS . AVG:',fname,avg(p),avg(r),avg(f))
  print('KEYS SCORES :',avg(p),avg(r),avg(f))

  #save keys scores into file
  content = 'fileName, Precision, Recall, F-Measure' + '\n'
  content += score2txt(files, p, r, f)
  string2file(out_keys_dir + 'KeysScores.csv',content)
  

def score2txt(files, p, r, f) :
  zipped = zip(files, p, r, f)
  txt = ''
  for item in zipped :
    file,pre,recall,fm=item
    txt += file + ', '
    txt += str(pre) + ', '
    txt += str(recall) + ', '
    txt += str(fm) + '\n'
  return txt
  
def txt2key(fname) :
  return fname.replace('.txt','.key')
    
def exists_file(fname):
  """ if it exists as file or dir"""
  return os.path.exists(fname)

def avg(xs) :
  s=sum(xs)
  l=len(xs)
  if 0==l : return None
  return s/l  

######### main evaluator #############
def go() :

  #fill_out_abs


  def showParams(p=dr.params) :
    print("SYSTEM :" ,SYSTEM)
    # print("DATASET :", doc_dir)
    print("DATASET :", DATASET)
    print(
          'wk',wk,'sk',sk,'\n'
          # 'with_full_text = ',with_full_text,'\n',
          'docs = ', DATASET.count,'\n',
          'force = ', force, '\n'
          )

  print("STARTING")
  showParams()
  random.seed(42)
  extract_keys_and_abs(wk, sk)
  print("EXTRACTED KEYS AND ABSTRACTS")

  print('                Precision,          Recall,           F-Measure')
  
  if DATASET.has_kwds:
    eval_keys()
    keys_with_rouge(0)

  eval_abs()
  eval_with_rouge(0)  # 1
  eval_with_rouge(1)  # 2
  eval_with_rouge(2)  # l
  eval_with_rouge(3)  # w
  print('DONE')
  showParams()
  

if __name__ == '__main__' :
  # pass
  go()

