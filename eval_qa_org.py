import sys
import os
import json
import argparse
from doctalk.talk import Talker, nice_keys, exists_file, jload, jsave
from doctalk.params import talk_params, ropen, wopen
from doctalk.think import reason_with_File, reason_with_Text


def saveSQuAD_QuestionContent(version):
  datadir = "dataset/QA/SQuAD/" + version + "/"
  os.makedirs(datadir + 'dev',exist_ok=True)
  if version == "1.1":
    dataset= jload( datadir + "dev-v1.1.json")
  else : #version ="2.0"
    dataset= jload( datadir + "dev-v2.0.json")
  #data is []
  #print('data[0]:', dataset['data'][0])
  for article in dataset['data']:
      context = ''
      for paragraph in article['paragraphs']:
         context += paragraph['context']
      for i, paragraph in enumerate(article['paragraphs']):
         fname = datadir + "dev/" + article['title']  + "_" + str(i) + ".txt"
         #context = paragraph['context']
         with wopen(fname) as fcontext :
            fcontext.write(context + "\n")
         fcontext.close()          
         questions = paragraph['qas']
         fqname = datadir + "dev/" + article['title']  + "_" + str(i) + "_quest.txt" 
         with wopen(fqname) as fquest:
           for question in questions:
             q=question['question']
             fquest.write(q + "\n")
           fquest.close()

def createSQuADQuestionIDMap(version):
  datadir = "dataset/QA/SQuAD/"  + version + "/"
  if version == "1.1":
    dataset= jload( datadir + "dev-v1.1.json")
  else : #version ="2.0"
    dataset= jload( datadir + "dev-v2.0.json")
  #data is []
  #print('data[0]:', dataset['data'][0])
  qidMap = dict()
  for article in dataset['data']:
      for i, paragraph in enumerate(article['paragraphs']):    
         questions = paragraph['qas']
         for question in questions:
             qid = question['id']
             q=question['question']
             qidMap[qid] = article['title']  + "_" + str(i) + "_" + q
  output = json.dumps(qidMap)
  fname = datadir + "qidMap.json"
  with wopen(fname) as f:
    f.write(output + "\n")
  f.close()

# example: answerSQuADByName('dataset/QA/SQuAD/1.1/dev/1973_oil_crisis_0')
def answerSQuADByName(filename):
  talkansOrg, talkansYifan, thinkans, bertans = reason_with_pytalk_FromFile(filename)
  print('talkansOrg:', talkansOrg)
  print('talkansYifan:', talkansYifan)
  print('thinkans:', thinkans )
  print('bertans:', bertans )

 

def answerSQuADFromFile(version):
  datadir = "dataset/QA/SQuAD/" + version + "/"
  if version == "1.1":
    dataset= jload( datadir + "dev-v1.1.json")
  else : #version ="2.0"
    dataset= jload( datadir + "dev-v2.0.json")
  #data is []
  qidTalkAnswerOrgMap = dict()
  qidTalkAnswerYifanMap = dict()
  qidThinkAnswerMap = dict()
  qidBertAnswerMap = dict()

  for count, article in enumerate(dataset['data']):
    for i, paragraph in enumerate(article['paragraphs']):
      fname = datadir +"dev/" + article['title']  + "_" + str(i)
      talkansOrg, talkansYifan, thinkans, bertans = reason_with_pytalk_FromFile(fname)
      #print('answerSQuAD, talkansOrg:', talkansOrg)
      #print('answerSQuAD, talkansYifan:', talkansYifan)
      #print('answerSQuAD, thinkans:', thinkans)
      #print('answerSQuAD, bertans:', bertans)

      qids = []
      for qa in paragraph['qas']:
        qid = qa['id']
        qids.append(qid)
      print('qids length:', len(qids), ', detail:', qids)
      for j, qid in enumerate(qids):
        qidTalkAnswerOrgMap[qid] = talkansOrg[j]
        qidTalkAnswerYifanMap[qid] = talkansYifan[j]
        qidThinkAnswerMap[qid] = thinkans[j]
        qidBertAnswerMap[qid] = bertans[j]
      #if i == 0: break
    if count ==5: break
  #print('\nqidTalkAnswerOrgMap:', qidTalkAnswerOrgMap)
  #print('\nqidTalkAnswerYifanMap:', qidTalkAnswerYifanMap)
  #print('\nqidThinkAnswerMap:', qidThinkAnswerMap)
  #print('\nqidBertAnswerMap:', qidBertAnswerMap)  
  outputTalkOrig = json.dumps(qidTalkAnswerOrgMap)
  with wopen(datadir + 'predictions_talkOrigin.json' ) as ftalkOrigin:
    ftalkOrigin.write(outputTalkOrig + "\n")
  ftalkOrigin.close()

  outputTalkYifan = json.dumps(qidTalkAnswerYifanMap)
  with wopen(datadir + 'predictions_talkYifan.json' ) as ftalkYifan:
    ftalkYifan.write(outputTalkYifan + "\n")
  ftalkYifan.close()
  
  outputThink = json.dumps(qidThinkAnswerMap)
  with wopen(datadir + 'predictions_think.json' ) as fthink:
    fthink.write(outputThink + "\n")
  fthink.close() 

  outputBert = json.dumps(qidBertAnswerMap)
  with wopen(datadir + 'predictions_bert.json' ) as fbert:
    fbert.write(outputBert + "\n")
  fbert.close() 


def reason_with_pytalk_FromFile(fname) :  
  params = talk_params()
  params.with_answerer=True
  params.answers_by_rank = True
  params.to_prolog = 1 
  talkansOrg, talkansYifan, thinkans, bertans = reason_with_File(fname, params)
  return talkansOrg, talkansYifan, thinkans, bertans




def answerSQuADFromText(version):
  datadir = "dataset/QA/SQuAD/" + version + "/"
  if version == "1.1":
    dataset= jload( datadir + "dev-v1.1.json")
  else : #version ="2.0"
    dataset= jload( datadir + "dev-v2.0.json")
  #data is []
  qidTalkAnswerOrgMap =dict() 
  qidTalkAnswerYifanMap =dict() 
  qidThinkAnswerMap =dict() 
  qidBertAnswerMap =dict() 
  for count, article in enumerate(dataset['data']):
    for i, paragraph in enumerate(article['paragraphs']):
      context = paragraph['context']
      print('\n\n^^^^^^^^^^^^^^^^^^^^^^^^^^\n')
      print(article['title'], ' paragraph[', i, ']')
      print('context:\n',context )
      print('\n^^^^^^^^^^^^^^^^^^^^^^^^^^\n\n')

      qlist = []
      questions = paragraph['qas']
      for question in questions:
        q=question['question']
        qlist.append(q)
      talkansOrg, talkansYifan, thinkans, bertans = reason_with_pytalk_FromText(context, qlist)
      print('answerSQuAD, talkansOrg:', talkansOrg )
      print('answerSQuAD, talkansYifan:', talkansYifan )
      print('answerSQuAD, thinkans:', thinkans )
      print('answerSQuAD, bertans:', bertans )
      qids = []
      for qa in paragraph['qas']:
        qid = qa['id']
        qids.append(qid)
      print('qids length:', len(qids), ', detail:', qids)
      for j, qid in enumerate(qids):
        qidTalkAnswerOrgMap[qid] = talkansOrg[j]
        qidTalkAnswerYifanMap[qid] = talkansYifan[j]
        qidThinkAnswerMap[qid] = thinkans[j]
        qidBertAnswerMap[qid] = bertans[j]
      if i == 0: break
    if count==0: break
  #print('\nqidTalkAnswerOrgMap:', qidTalkAnswerOrgMap)
  #print('\nqidTalkAnswerYifanMap:', qidTalkAnswerYifanMap)
  #print('\nqidThinkAnswerMap:', qidThinkAnswerMap)
  #print('\nqidBertAnswerMap:', qidBertAnswerMap)  
  
  outputTalkOrig = json.dumps(qidTalkAnswerOrgMap)
  with wopen(datadir + 'predictions_talkOrigin.json' ) as ftalkOrigin:
    ftalkOrigin.write(outputTalkOrig + "\n")
  ftalkOrigin.close()

  outputTalkYifan = json.dumps(qidTalkAnswerYifanMap)
  with wopen(datadir + 'predictions_talkYifan.json' ) as ftalkYifan:
    ftalkYifan.write(outputTalkYifan + "\n")
  ftalkYifan.close()
  
  outputThink = json.dumps(qidThinkAnswerMap)
  with wopen(datadir + 'predictions_think.json' ) as fthink:
    fthink.write(outputThink + "\n")
  fthink.close() 

  outputBert = json.dumps(qidBertAnswerMap)
  with wopen(datadir + 'predictions_bert.json' ) as fbert:
    fbert.write(outputBert + "\n")
  fbert.close() 


def reason_with_pytalk_FromText(text, qlist) :  
  params = talk_params()
  params.with_answerer=True
  params.answers_by_rank = True
  params.to_prolog = 1 
  talkansOrg, talkansYifan, thinkans, bertans = reason_with_Text(text, qlist, params)
  return talkansOrg, talkansYifan, thinkans, bertans


def saveHotpotQA_QuestionContent():
  dataset= jload('dataset/QA/HotpotQA/hotpot_dev_distractor_v1.json')
  #data is []
  print('dataset length:', len(dataset))
  for i, article in enumerate(dataset):    
    quest_id = article["_id"]
    #print('quest_id:', quest_id)
    question = article["question"]
    #print('question ', i, ':', question)
    fqname = "dataset/QA/HotpotQA/dev/" + quest_id + "_quest.txt" 
    with wopen(fqname) as fquest:
        fquest.write(question + "\n")
    fquest.close()
    
    answer = article["answer"]
    fqname = "dataset/QA/HotpotQA/answer/" + quest_id + ".txt" 
    with wopen(fqname) as fanswer:
      fanswer.write(answer + "\n")
    fanswer.close()

    text = ''
    paralist = article["context"]
    #print('paralist type:', type(paralist))
    for para in paralist:
      #title = para[0]
      #print('\n\ntitle:', title)
      text += '\n'
      sentences = para[1]
      #print('sentences:', sentences)
      for sent in sentences:
        text += sent
    
    fname = "dataset/QA/HotpotQA/dev/" + quest_id + ".txt"
    with wopen(fname) as fcontext :
      fcontext.write(text + '\n')
    fcontext.close()

    if i > 10 : break  


def answerHotpotQA():
  dataset= jload('dataset/QA/HotpotQA/hotpot_dev_distractor_v1.json')
  #data is []
  qidTalkAnswerMap =dict()
  qidThinkAnswerMap =dict() 
  qidDiffAnswerMap =dict()  
  for i, article in enumerate(dataset):    
    quest_id = article["_id"]
    fname = "dataset/QA/HotpotQA/dev/" + quest_id
    talkans, thinkans = reason_with_pytalk_FromFile(fname)
    print('answerHotpotQA:', talkans, ',', thinkans )
    if not talkans[0]: talkans[0] = ''
    qidTalkAnswerMap[quest_id] = talkans[0]
    if not thinkans[0]: thinkans[0] = ''
    qidThinkAnswerMap[quest_id] = thinkans[0]
    if talkans != thinkans:
      diff = 'talk:' + talkans[0] + '; think:' + thinkans[0]
      qidDiffAnswerMap[quest_id] = diff
    if i > 10 : break
  print('\nqidTalkAnswerMap:', qidTalkAnswerMap)
  print('\nqidThinkAnswerMap:', qidThinkAnswerMap)
  print('\nqidDiffAnswerMap', qidDiffAnswerMap)

  answerTalkMap = dict()
  answerTalkMap["answer"] = qidTalkAnswerMap      
  outputTalk = json.dumps(answerTalkMap)
  fname = "dataset/HotpotQA/pred_talk.json"
  with wopen(fname) as ftalk:
    ftalk.write(outputTalk + "\n")
  ftalk.close()

  answerThinkMap = dict()
  answerThinkMap["answer"] = qidThinkAnswerMap 
  outputThink = json.dumps(answerThinkMap)
  fname = "dataset/QA/HotpotQA/pred_think.json"
  with wopen(fname) as fthink:
    fthink.write(outputThink + "\n")
  fthink.close()
  outputDiff = json.dumps(qidDiffAnswerMap)
  fname = "dataset/QA/HotpotQA/pred_diff.json"
  with wopen(fname) as fdiff:
    fdiff.write(outputDiff + "\n")
  fdiff.close()

def saveCoQA_QuestionContent():
  dataset= jload('dataset/QA/CoQA/coqa-dev-v1.0.json')  
  print('data length:', len(dataset['data']))  
  for article in dataset['data']:
    quest_id = article["id"]
    fname = "dataset/QA/CoQA/dev/" + quest_id + ".txt"
    conext = article['story']
    with wopen(fname) as fcontext :
      fcontext.write(conext + "\n")
    fcontext.close()          
    questions = article['questions']
    fqname = "dataset/QA/CoQA/dev/" + quest_id + "_quest.txt" 
    with wopen(fqname) as fquest:
      for question in questions:
        q=question['input_text']
        fquest.write(q + "\n")
      fquest.close()
      questions = article['questions']
    answers = article['answers']
    faname = "dataset/QA/CoQA/answer/" + quest_id + ".txt" 
    with wopen(faname) as fanswer:
      for answer in answers:
        span_text=answer['span_text']
        input_text = answer['input_text']
        fanswer.write(span_text + "\n" + input_text + "\n")
      fanswer.close()


def answerCoQA():
  dataset= jload('dataset/QA/CoQA/coqa-dev-v1.0.json')
  #data is []
  qidTalkAnswerMap =dict()
  qidThinkAnswerMap =dict() 
  qidDiffAnswerMap =dict()  
  for i, article in enumerate(dataset['data']):    
    quest_id = article["id"]
    fname = "dataset/QA/CoQA/dev/" + quest_id
    talkans, thinkans = reason_with_pytalk_FromFile(fname)
    print('answerCoQA:', talkans, ',', thinkans )
    '''
    if not talkans[0]: talkans[0] = ''
    qidTalkAnswerMap[quest_id] = talkans[0]
    if not thinkans[0]: thinkans[0] = ''
    qidThinkAnswerMap[quest_id] = thinkans[0]
    if talkans != thinkans:
      diff = 'talk:' + talkans[0] + '; think:' + thinkans[0]
      qidDiffAnswerMap[quest_id] = diff
    '''
    if i > 1 : break
    '''
  print('\nqidTalkAnswerMap:', qidTalkAnswerMap)
  print('\nqidThinkAnswerMap:', qidThinkAnswerMap)
  print('\nqidDiffAnswerMap', qidDiffAnswerMap)

  answerTalkMap = dict()
  answerTalkMap["answer"] = qidTalkAnswerMap      
  outputTalk = json.dumps(answerTalkMap)
  fname = "dataset/QA/HotpotQA/pred_talk.json"
  with wopen(fname) as ftalk:
    ftalk.write(outputTalk + "\n")
  ftalk.close()

  answerThinkMap = dict()
  answerThinkMap["answer"] = qidThinkAnswerMap 
  outputThink = json.dumps(answerThinkMap)
  fname = "dataset/QA/HotpotQA/pred_think.json"
  with wopen(fname) as fthink:
    fthink.write(outputThink + "\n")
  fthink.close()
  outputDiff = json.dumps(qidDiffAnswerMap)
  fname = "dataset/QA/HotpotQA/pred_diff.json"
  with wopen(fname) as fdiff:
    fdiff.write(outputDiff + "\n")
  fdiff.close()
  '''


def saveNewQA_QuestionContent():
  dataset= jload('dataset/QA/NewsQA/combined-newsqa-data-v1.json')
  #data is []
  print('how many storys:', len(dataset['data']))

  for i, article in enumerate(dataset['data']):
    storyId = article["storyId"]
    storyId  =  storyId [len("./cnn/stories/"):]   
    keeplen= len(storyId) - len(".story")
    storyId = storyId[:keeplen]    
    
    fname = "dataset/QA/NewsQA/dev/" + storyId + ".txt"
    conext = article['text']
    with wopen(fname) as fcontext :
      fcontext.write(conext + "\n")
    fcontext.close()    
          
    questions = article['questions']
    qstring = ""
    astring = ""
    answerMap =dict()  
    
    for j, question in enumerate(questions):
      q=question['q']
      qstring += q + "\n"
      a=question['consensus']
      #print('a:', a)
      if 'badQuestion' in a.keys():
        #print("*****find bad question")
        answer = ""
      elif 'noAnswer' in a.keys():
        #print("******noAnswer")
        answer = ""
      else:
        start = a['s']
        end = a['e']
        #print('start:end, ', start, end )
        answer = conext[a['s']:a['e']]
      #print('answer:', answer)
      answerMap[storyId + "_" + str(j)] = answer
      

    fqname = "dataset/QA/NewsQA/dev/" + storyId + "_quest.txt" 
    with wopen(fqname) as fquest:
      fquest.write(qstring + "\n")
    fquest.close()
    
    faname = "dataset/QA/NewsQA/answer/" + storyId + ".txt"
    outputAnswer = json.dumps(answerMap)
    with wopen(faname) as fanswer:
      fanswer.write( outputAnswer + "\n" )
    fanswer.close()

def answerNewsQA():
  dataset= jload('dataset/QA/NewsQA/combined-newsqa-data-v1.json')
  #data is []
 
  for i, article in enumerate(dataset['data']):
    storyId = article["storyId"]
    storyId  =  storyId [len("./cnn/stories/"):]
    keeplen= len(storyId) - len(".story")
    storyId = storyId[:keeplen]
    fname = "dataset/QA/NewsQA/dev/" + storyId
    talkansOrg, talkansYifan, thinkans, bertans = reason_with_pytalk_FromFile(fname)
    print('answerNewsQA, talkansOrg:', talkansOrg)
    print('answerNewsQA, talkansYifan:', talkansYifan)
    print('answerNewsQA, thinkans:', thinkans)
    print('answerNewsQA, bertans:', bertans)

    
    questions = article['questions']
    answerTalkOriginMap =dict()  
    answerTalkYifanMap =dict()  
    answerThinkMap =dict()
    answerBertMap =dict()
  
    #answerDiffMap =dict()
    for j, question in enumerate(questions):
      q=question['q']
      aTalkOrign=talkansOrg[j]
      aTalkYifan=talkansYifan[j]     
      aThink = thinkans[j]
      aBert = bertans[j]
      answerTalkOriginMap[storyId + "_" + str(j)] = aTalkOrign
      answerTalkYifanMap[storyId + "_" + str(j)] = aTalkYifan 
      answerThinkMap[storyId + "_" + str(j)] = aThink
      answerBertMap[storyId + "_" + str(j)] = aBert
      '''
      if aTalk != aThink:
        answerDiffMap[storyId + "_" + str(j)] = "talk:" + aTalk + ", think:" + aThink
      ''' 
    
    fname = "dataset/QA/NewsQA/output/talk_origin/" + storyId + ".txt"
    outputTalkOriginAnswer = json.dumps(answerTalkOriginMap)
    with wopen(fname) as ftalkOrign:
      ftalkOrign.write(outputTalkOriginAnswer + "\n")
    ftalkOrign.close()

    fname = "dataset/QA/NewsQA/output/talk_yifan/" + storyId + ".txt"
    outputTalkYifanAnswer = json.dumps(answerTalkYifanMap)
    with wopen(fname) as ftalkYifan:
      ftalkYifan.write(outputTalkYifanAnswer + "\n")
    ftalkYifan.close()

  
    outputThinkAnswer = json.dumps(answerThinkMap)
    fname = "dataset/QA/NewsQA/output/think/" + storyId + ".txt"
    with wopen(fname) as fthink:
      fthink.write(outputThinkAnswer + "\n")
    fthink.close()

    outputBertAnswer = json.dumps(answerBertMap)
    fname = "dataset/QA/NewsQA/output/bert/" + storyId + ".txt"
    with wopen(fname) as fbert:
      fbert.write(outputBertAnswer + "\n")
    fbert.close() 

    '''
    outputDiffMap = json.dumps(answerDiffMap)
    fname = "dataset/QA/NewsQA/output/diff/" + storyId + ".txt"
    with wopen(fname) as fdiff:
      fdiff.write(outputDiffMap + "\n")
    fdiff.close()
    '''
    if i==0:break


def reason_with_pytalk_FromFile(fname) :  
  params = talk_params()
  params.with_answerer=True
  params.answers_by_rank = True
  params.to_prolog = 1 
  talkOriginAns, talkYifanAns, thinkans, bertans = reason_with_File(fname, params)
  return talkOriginAns, talkYifanAns, thinkans, bertans

  

if __name__ == "__main__":


     
    #saveSQuAD_QuestionContent("1.1" )
    answerSQuADFromFile("1.1")
     
    #answerSQuADFromText("1.1")

    #answerNewsQA()
    print('DONE')

'''    
 
if __name__ == '__main__' :
  pass
'''


