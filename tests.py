import glob
import os
from doctalk.params import talk_params
from doctalk.talk import *
from doctalk.think import *
from doctalk.vis import *
from doctalk.api import *
from doctalk.pypro import NatTalker
from doctalk.seek import *

import pprint

doc_dir="examples/"
doc_files = sorted(glob.glob(doc_dir+"*.txt"))
quest_files = sorted(glob.glob(doc_dir+"*_quest.txt"))

def quest2doc(qf) :
  return qf.replace('_quest.txt','.txt')

#clean files at given directory path
#example:  clean_path("../examples")   clean_path("../examples1")
def clean_path(path) :
  print(path);
  os.makedirs(path,exist_ok=True)
  files = glob.glob(path+"/*")
  print("get ", len(files), " files")
  for f in files:
    os.remove(f)

#example clean("True") or clean()
def clean(force=False)  :
  D=doc_dir
  if force :
    files = glob.glob(D + "/*.json")
    print(*files)
    for f in files:
       print(f)
       os.remove(f)
  files = glob.glob(D + "/*_cloud.pdf")
  for f in files:
    os.remove(f)
  files = glob.glob(D + "/*.gv.pdf")
  for f in files:
    os.remove(f)
  files = glob.glob(D + "/*.gv")
  for f in files:
    os.remove(f)
  files = glob.glob(D + "/*.pro")
  for f in files:
    os.remove(f)

# tests to run

def nlp_test() :
  to_json('examples/test.txt', 'examples/temp.json')
  show_extract('examples/test.txt')

def mtest() :
  fname = 'examples/geo.txt'
  t=Talker(from_file=fname)
  db=t.db
  for m in materialize(db) :
    lemmas,words,tags,ners,rels,svos,deps,comps = m
    #pprint.pprint(rels)
    #pprint.pprint(svos)
    pprint.pprint(comps)
    print('')

def otest() :
  fname = 'examples/test.txt'
  #rs=t.to_word_orbit('field')
  #rs = t.to_sent_orbit(333)
  #plot_rank_orbit(rs)
  t = Talker(from_file=fname)
  g=t.to_dep_tree()
  gshow(g,attr='rel',file_name='deptree.gv')

def qtest() :
  d = {"quiet" : False}
  fname = 'examples/test.txt'
  t = Talker(from_file=fname,params=talk_params(from_dict=d))
  t.show_all()

def jtest() :
  d = '{"quiet" : false}'
  fname = 'examples/test.txt'
  t = Talker(from_file=fname,params=talk_params(from_json=d))
  t.show_all()

def do(qf) :
    df=qf.replace("_quest.txt","")
    run_with(df,query=True)

def qftest() :
  do('examples/const_quest.txt')

def go()  :
  D=doc_dir
  files = sorted(glob.glob(D + "/*_quest.txt"))
  for qf in files:
    df=qf.replace("_quest.txt","")
    run_with(df,query=True)

def ftest() :
  fname='examples/geo'  #################
  run_with(fname,query=False)


def nrun(fname):
  docfile=fname+".txt"
  questfile=fname+"_quest.txt"

  natscript = '''

  rel 'is_like'.
  rel 'as_in'.
  rel 'kind_of'.

  tc_search A Rel B Res : rel Rel, tc A Rel B (s (s 0)) _ Res.

  tc A Rel C (s N1) N1 Res : ~ A Rel B Id, tc1 B Rel C N1 N2 Id Res.

  tc1 B _Rel B N N Id Id.
  tc1 B Rel C N1 N2 _Id Res : tc B Rel C N1 N2 Res.

  similar A B Id:
    ~ A R B Id,
    ~ T R A Id1,
    ~ T R B Id1.
  '''

  N = NatTalker(from_file=docfile,
                natscript=natscript)
  with ropen(questfile) as f:
    for q in f.readlines():
      N.natrun(q)
  # N.natrun("What deposits can be found in the Permian basin?")

  '''
  goals=[
    #'similar deposit B Id?',
    'tc_search permian Rel B Where ?'
  ]

  for goal in goals:
    print('GOAL:',goal)
    print('')
    ids=set()
    for answer in N.natrun(goal):
      print('ANSWER', answer)
      continue
      _,s,v,o,I=answer
      ids.add(I.val)
    return
    for id in ids :
      print(id,nice(N.get_sentence(id)))
    print('')
   '''

def pdf_test() :
  d = '{"quiet" : true}'
  fname = 'pdfs/cloudmis.pdf'
  #t = Talker(from_pdf=fname,params=talk_params(from_json=d))
  #t.show_all()
  fname = 'pdfs/cloudmis.txt'
  t = Talker(from_file=fname, params=talk_params(from_json=d))
  t.show_all()

def ptest() :
  nrun('examples/wolfram')

def chat_test() :
  chat_about('examples/bfr')


def tftest():
  fname='examples/hindenburg'  #################
  reason_with(fname,query=True)

def t1() :
    fname = 'examples/bfr'
    reason_with(fname, query=True)


def t0():
  fname = 'examples/bfr'
  run_with(fname, query=True)

def t2():
  fname = 'examples/hindenburg'
  reason_with(fname, query=True)


def t3():
  fname = 'examples/const'
  reason_with(fname, query=True)

def t4a():
  fname = 'examples/logrank'
  run_with(fname, query=True)

def t4():
  fname = 'examples/logrank'
  reason_with(fname, query=True)

def t5():
  fname = 'examples/heaven'
  reason_with(fname, query=True)

def t6():
  fname = 'examples/einstein'
  reason_with(fname, query=True)

def t7():
  fname = 'examples/geo'
  reason_with(fname, query=True)

def t8():
  fname = 'examples/hindenburg'
  reason_with(fname, query=True)

def t9():
  fname = 'examples/kafka'
  reason_with(fname, query=True)

def t10():
  fname = 'examples/test'
  reason_with(fname, query=True)

def t11():
  fname = 'examples/texas'
  reason_with(fname, query=True)

def t12():
  fname='examples/wasteland'  #################
  reason_with(fname,query=True)

def t13():
  fname='examples/heli'
  reason_with(fname,query=True)

def t14():
  fname='examples/covid'
  reason_with(fname,query=True)

def t15():
  fname='examples/wolfram'
  run_with(fname,query=True)

def t15a():
  fname='examples/wolfram'
  reason_with(fname,query=True)

def t16():
  fname='examples/toxi'
  run_with(fname,query=True)

def t16a():
  fname='examples/toxi'
  reason_with(fname,query=True)


def t17():
  fname = 'examples/peirce'
  run_with(fname, query=True)


def t17a():
  fname = 'examples/peirce'
  reason_with(fname, query=True)

def t17b():
  fname = 'examples/peirce'
  nrun(fname)

def t18():
  fname = 'examples/ec2'
  run_with(fname, query=True)


def t18a():
  fname = 'examples/ec2'
  reason_with(fname, query=True)

def t18b():
  fname = 'examples/ec2'
  nrun(fname)

def t19():
  fname = 'examples/relativity'
  run_with(fname, query=True)

def t20():
  fname = 'examples/alice'
  run_with(fname, query=True)

def t21():
  fname = 'examples/cybok'
  run_with(fname, query=True)

def s1() :
  fname = 'examples/bfr.txt'
  s=Seeker(from_file=fname)
  s.qa()

def s2() :
  fname = 'examples/tesla.txt'
  s=Seeker(from_file=fname)
  s.qa()

def s3() :
  fname = 'examples/const.txt'
  s=Seeker(from_file=fname)
  s.qa()

def tgo()  :
  D=doc_dir
  files = sorted(glob.glob(D + "/*_quest.txt"))
  for qf in files:
    df=qf.replace("_quest.txt","")
    reason_with(df,query=True)



import json
def crunch() :
  with ropen('doctalk/in.txt') as f:
    with  wopen('doctalk/lemmas.json') as g :
      d=dict()
      for l in f.readlines() :
        ws = l.split()
        if len(ws) == 3 :
          _,fr,w=ws
          if len(w)>1 and  w.replace('-','x').isalpha():
            d[w]=float(fr)
              #print(ws[2],ws[1],file=g)
          else:
            print(ws)
        else:
          print(ws)
      json.dump(d,g)

def api_test() :
  '''
  to be used on the server side to expose this as a web or Alexa service
  '''
  params=new_params(from_json='{"top_sum":3,"top_keys":6,"top_answers":3}')
  jsonish='''["
    The cat sits on the mat. 
    The mat sits on the floor.
    The floor sits on planet Earth.
    The Earth does not sit.
    The Earth just wanders.
  "]
  '''
  from_json=jsonish.replace('\n',' ')

  talker=new_talker(from_json=from_json,params=params)
  wss=json.loads(talker.summary_sentences())
  ks=json.loads(talker.keyphrases())

  print('SUMMARY')
  for ws in wss:
    print(" ".join(ws))

  print('KEYPHRASES')
  for k in ks:
    print(k)
  print('')
  q='Where is the mat?'
  print(q)
  r=answer_question(talker,q)
  wss=json.loads(r)

  for ws in wss :
    print(' '.join(ws))

def tt1():
  fname = 'examples/bfr.txt'
  t=Talker(from_file=fname)
  #print(1,list(t.raw_dep_edge(0)))
  #print(2,t.dep_tree(0))
  #print(3,t.dep_term(0,quote=False))
  #print(4,t.dep_tree(1))
  #print(5, t.dep_tree(2))
  #print(6,t.dep_term(2, quote=False))
  #t.to_term_file()
  t.to_json_file()

def tt2():
  dir_to_term_files('examples/',target='json')
  dir_to_term_files('examples/', target='pro')

if __name__== "__main__" :
  #nlp_test()
  #go()
  #mtest()
  #qftest()
  #simtest()
  #canned_test()
  #ftest()
  #ptest()
  #ttest2()
  #t12()
  #tftest()
  #otest()
  #t0()
  #otest()
  #api_test()
  #clean_text_file('examples/peirce.txt')
  #clean_text_file('examples/cybok.txt')
  #tt2()
  pass




