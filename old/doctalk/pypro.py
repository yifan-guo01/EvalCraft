from natlog.natlog import natlog,Int
from natlog.db import db

from .params import *
from .talk import *


class NatTalker(Talker) :
  def __init__(self,natscript=None,**kwargs):
    super().__init__(**kwargs)
    self.engine=natlog(text=natscript)
    self.engine.db=self.to_nat_db()

  def to_nat_db(self):
    nd=db()
    for svo, occs in self.svos.items():
      s, v, o = svo
      for id in sorted(occs) :
        c=(s,v,o,id) # should be Int
        nd.add_db_clause(c)
    return nd

  def query_with_goal(self,natgoal):
      for answer in distinct(self.engine.solve(natgoal)):
        yield answer

  def ask(self,q):
    answers,answerer=self.answer_quest(q)

    ids=dict()
    shareds=set()
    for answer in answers:
       id, sent,rank,shared=answer
       ids[id]=rank
       shareds.update(shared)

    inferred=dict()
    targets=set()
    for shared in shareds :
       for res in self.query_with_goal("tc_search "+shared+" Rel What Where?") :
         _,_shared,rel,what,where=res
         if isinstance(what,tuple) and what[0]==what[1] : continue
         id=where.val
         if id in ids:
            targets.add(what)
            inferred[id]=ids[id]
            #ids[id]=ids[id]*2

    #sorted_ids=rank_sort(ids)
    sorted_ids=sorted(ids.items())
    inferred=rank_sort(inferred)
    yield sorted_ids,sorted(inferred), shareds,targets

  def natrun(self, q):
     print('QUESTION:',q)
     for x in self.ask(q):
        ids, inferred, shareds, targets = x
        print('')
        print('IDS',ids)
        print('')
        print('INFS',inferred)
        print('')
        print('CONCEPTS IN ANSWERS:',shareds)
        print('')
        print('MINED CONCEPTS: ',targets)
        print('')
     print('ANSWERS:')
     top_ids=list(take(self.params.top_answers, ids))
     for i, r in top_ids:
       print(i, r, end=': ')
       self.say(nice(self.get_sentence(i)))
     print('')
     print('NEW INFERRED ANSWERS:')
     top_ids={i for i,_ in top_ids}
     for k, ir in enumerate(inferred):
       i,r=ir
       if i in top_ids : continue
       if k>self.params.top_answers : break
       print(i, r, end=': ')
       self.say(nice(self.get_sentence(i)))
     print('-----------------------\n')
