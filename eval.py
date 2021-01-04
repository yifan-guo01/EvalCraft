import glob
import sys
import os
import random

import rouge_stats as rs
import key_stats as ks
from itertools import islice

import textcrafts
from textcrafts import deepRank as dr
from textcrafts.sim import *

from doctalk.talk import Talker, nice_keys, exists_file
from doctalk.params import talk_params


# shows moving averages if on
trace_mode=False

# choice of processor
SYSTEM = "DOCTALK"
#SYSTEM = "TEXTCRAFT"
#SYSTEM = "TEXTRANK"


if SYSTEM == "TEXTRANK":
   from tr import keys_and_abs

CNN_DM=False

# 2 forces deletion of json in temp_dir, 1=forces deletion of keys+abs
force=1

# number of keyphrases and summary sentences
#wk,sk=6,6
#wk,sk=10,9
wk,sk=10,8 #best

# if true abstracts are not trimmed out from documents
with_full_text = False

# sizes of silver abs and keys will match sizes in gold
match_sizes = False

# sets max number of documents to be processed, all if None or 0
max_docs = 100

# resource directories, for production and testing at small scale
prod_mode=True

if prod_mode :
  data_dir='dataset/Krapivin2009/'
  out_abs_dir  = "out/abs/"
  out_keys_dir = "out/keys/"
  temp_dir = 'temp_docs/'
  show_errors=True
else :
  if CNN_DM:
    #data_dir = 'dataset/cnn_dm_small/'
    data_dir = 'dataset/cnn_big/'
  else:
    data_dir='dataset/small/'

  out_abs_dir = "test/abs/"
  out_keys_dir = "test/keys/"
  temp_dir = 'test_docs/'
  show_errors = False
  
doc_dir=data_dir+'docsutf8/'
keys_dir=data_dir+'keys/'
abs_dir=data_dir+'abs/'
all_doc_files = sorted(glob.glob(doc_dir+"*.txt"))

if max_docs :
  doc_files=list(islice(all_doc_files,max_docs))
else :
  doc_files=all_doc_files


# clean output directories
def clean_all() :
  if not force : return
  clean_path(out_abs_dir)
  clean_path(out_keys_dir)
  if force>1 : clean_path(temp_dir)

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
def disect_doc(doc_file) :
  title=[]
  abstract=[]
  body=[]
  mode=None
  with open(doc_file) as f:
    for line in f:
      if line.startswith('--T')   : mode='TITLE'
      elif line.startswith('--A') : mode ='ABS'
      elif line.startswith('--B') : mode = 'BODY'
      elif line.startswith('--R'): mode = 'DONE'
      else :
        if   mode=='TITLE': title.append(line.strip()+' ')
        elif mode=='ABS'  : abstract.append(line.strip()+' ')
        elif mode=='BODY' : body.append(line.strip()+' ')
        elif mode=='DONE' : break
  return {'TITLE':title,'ABSTRACT':abstract,'BODY':body}

# process string text give word count,sentence count and filter
def runWithText(text,wk,sk,filter) :
  gm=customGraphMaker()
  gm.digest(text)
  keys= gm.bestWords(wk)
  sents=[s for (_,s) in gm.bestSentences(sk)]
  #keys_text=interleave_with('\n','\n',keys)
  #sents_text=interleave_with('\n','\n',sents)
  #return (keys_text,sents_text)
  nk=gm.nxgraph.number_of_nodes()
  vk=gm.nxgraph.number_of_edges()
  return (keys,sents,nk,vk)

def runWithTextAlt(fname,wk,sk,filter) :
  params = talk_params()
  params.top_sum=sk
  params.top_keys=wk
  talker=Talker(from_file=fname,params=params)
  ranked_sents=talker.get_summary()
  keys=talker.get_keys()
  def clean_sents():
    for r, s, ws in ranked_sents:
      yield ws

  #print('!!!KEYS',keys)
  #print('!!!SENT',list(clean_sents()))
  keys=nice_keys(keys)
  return (keys,clean_sents(),talker.g.number_of_nodes(),talker.g.number_of_edges())


def runWithPyTR(text,wk,sk,filter) :

  talker=Talker(from_file=fname)
  ranked_sents,keys=talker.extract_content(sk,wk)

  def clean_sents():
    for r, s, ws in ranked_sents:
      yield ws

  #print('!!!KEYS',keys)
  #print('!!!SENT',list(clean_sents()))
  keys=nice_keys(keys)
  return (keys,clean_sents(),talker.g.number_of_nodes(),talker.g.number_of_edges())



#  extract the gold standard abstracts from dataset  
def fill_out_abs() :
   for doc_file in doc_files :
     d=disect_doc(doc_file)
     abstract=d['ABSTRACT']
     text=''.join(abstract)
     abs_file=abs_dir+dr.path2fname(doc_file)
     print('abstract extraced to: ',abs_file)
     string2file(abs_file,text)

     
# turns a sequence/generator into a file, one line per item yield     
def seq2file(fname,seq) :
  xs=map(str,seq)
  ys=interleave_with('\n','\n',xs)
  text=''.join(ys)
  string2file(fname,text)

# turns a file into a (string) generator yielding each of its lines
def file2seq(fname) :
   with open(fname,'r') as f :
     for l in f : yield l.strip()

# turns a string into given file
def string2file(fname,text) :
  with open(fname,'w') as f :  
    f.write(text)

# turns content of file into a string
def file2string(fname) :
  try :
    with open(fname,'r') as f :
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

def process_file(i,path_file,full,wk,sk) :
  doc_file = dr.path2fname(path_file)
  kf = out_keys_dir + doc_file
  af = out_abs_dir + doc_file

  gold_kf = keys_dir + doc_file.replace('.txt','.key')
  gold_af = abs_dir + doc_file

  if match_sizes:
    gold_k=file2string(gold_kf).count('\n')
    if gold_k>1: wk=gold_k+0 #max(wk,gold_k)
    gold_a=file2string(gold_af).count('.')
    if gold_a > 1: sk = gold_a+0 # min(sk,gold_a)
    #print('!!!', wk, sk)

  if not force and exists_file(kf) and exists_file(af) :
    print('SKIPPING ALREADY PROCESSED:',doc_file)
    return

  if CNN_DM :
    text = file2string(path_file)
  else :
    d = disect_doc(path_file)
    title = d['TITLE']
    abstract = d['ABSTRACT']
    body = d['BODY']
    text_no_abs = ''.join(title + [' '] + body)

    if full:
      text = ''.join(title + [' '] + abstract + [' '] + body)
    else:
      text = ''.join(title + [' '] + body)

  if SYSTEM == "TEXTRANK":
    (keys,exabs) = keys_and_abs(text,wk,sk)
    print(i, ':', doc_file)

  else :
    if SYSTEM == "DOCTALK" :
      temp_file = temp_dir + doc_file
      string2file(temp_file, text)
      (keys, xss, nk, ek) = runWithTextAlt(temp_file, wk, sk, dr.isWord)
    elif SYSTEM == "TEXTCRAFT" :
      (keys, xss, nk, ek) = runWithText(text, wk, sk, dr.isWord)

    print(i,':',doc_file, 'nodes:', nk, 'edges:', ek)  # ,title)
    exabs = map(lambda x: interleave(' ', x), xss)

  seq2file(kf, keys)
  seq2file(af, exabs)


# extracts keys and abstacts from resource directory  
def extract_keys_and_abs(full,wk,sk,show_errors=show_errors) :
  clean_all()
  for i,path_file in enumerate(doc_files) :
    if show_errors:
      process_file(i,path_file, full, wk, sk)
    else:
      try :
        process_file(i,path_file, full, wk, sk)
      except :
        print('*** FAILING on:',path_file,'ERROR:',sys.exc_info()[0])

# apply Python base rouge to abstracts from given directory
def eval_with_rouge(i) :
  f=[]
  p=[]
  r=[]  
  for doc_file in doc_files : 
    fname=dr.path2fname(doc_file)
    ref_name=abs_dir+fname
    abs_name=out_abs_dir+fname
    #if trace_mode : print(fname)
    gold=file2string(ref_name)   
    silver=file2string(abs_name)
    if not gold:
      print('gold file missing:', ref_name)
      continue
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
    
        p.append(px)
        r.append(rx)
        f.append(fx)
        
      elif k>i : break
      k+=1
    if trace_mode : print('  ABS ROUGE MOV. AVG',i,fname,avg(p),avg(r),avg(f))
  rouge_name=(1,2,'l','w')  
  print ("ABS ROUGE",rouge_name[i],':',avg(p),avg(r),avg(f))


# apply Python base rouge to abstracts from given directory
def keys_with_rouge(i):
  f = []
  p = []
  r = []
  for doc_file in doc_files:
    fname = dr.path2fname(doc_file)
    ref_name = keys_dir + fname
    ref_name=ref_name.replace('.txt','.key')
    abs_name = out_keys_dir + fname
    # if trace_mode : print(fname)
    gold = file2string(ref_name)
    silver = file2string(abs_name)
    if not gold:
      print('gold file missing:', ref_name)
      continue
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

        p.append(px)
        r.append(rx)
        f.append(fx)

      elif k > i:
        break
      k += 1
    if trace_mode: print('  ABS ROUGE MOV. AVG', i, fname, avg(p), avg(r), avg(f))
  rouge_name = (1, 2, 'l', 'w')
  print("KEYS ROUGE", rouge_name[i], ':', avg(p), avg(r), avg(f))


# our own
def eval_abs() :
  f=[]
  p=[]
  r=[]  
  for doc_file in doc_files : 
    fname=dr.path2fname(doc_file)
    ref_name=abs_dir+fname
    abs_name=out_abs_dir+fname
    #if trace_mode : print(fname)
    gold=file2string(ref_name)
    silver=file2string(abs_name)
    if not gold:
      print('gold file missing:', ref_name)
      continue
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
      p.append(px)
      r.append(rx)
      f.append(fx)
    if trace_mode : print('  ABS MOV. AVG',fname,avg(p),avg(r),avg(f))
  print ("ABS SCORES  :",avg(p),avg(r),avg(f))

  
# 0.22434732994628803 0.24271988542882067 0.22280040709372084
def eval_keys() :
  f=[]
  p=[]
  r=[]  
  for doc_file in doc_files : 
    fname=dr.path2fname(doc_file)
    ref_name=keys_dir+fname
    keys_name=out_keys_dir+fname
    #if trace_mode : print(fname)
    gold=file2string(txt2key(ref_name))   
    silver=file2string(keys_name)
    if not gold:
      print('gold file missing:', ref_name)
      continue
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
    p.append(px)
    r.append(rx)
    f.append(fx)
    #if trace_mode : print('  KEYS . AVG:',fname,avg(p),avg(r),avg(f))
  print('KEYS SCORES :',avg(p),avg(r),avg(f))
  
  
def txt2key(fname) :
  return fname.replace('.txt','.key')
    
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
    print(
          'wk',wk,'sk',sk,'\n'
          'with_full_text = ',with_full_text,'\n',
          'prod_mode = ' ,prod_mode,'\n',
          'max_docs = ',max_docs,'\n',
          'match_sizes = ',match_sizes,'\n',
          #'noun_defs = ',p.noun_defs,'\n',
          #'all_recs =',p.all_recs,'\n'
          )

  print("STARTING")
  showParams()
  random.seed(42)
  extract_keys_and_abs(with_full_text, wk, sk)
  print("EXTRACTED KEYS AND ABSTRACTS")

  print('')
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
  pass
  #go()

