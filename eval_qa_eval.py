import sys
import os
import json
import argparse
from doctalk.talk import Talker, nice_keys, exists_file, jload, jsave
from doctalk.params import talk_params, ropen, wopen
from doctalk.think import reason_with_File, reason_with_Text

def mergeNewsQA_SQuAD(version):
  import glob
  squad_datadir = "dataset/QA/SQuAD/" + version + "/dev/"
  print('squad_datadir:', squad_datadir)
  squad_files = sorted(glob.glob(squad_datadir+"*.txt"))
  newsqa_datadir = "dataset/QA/NewsQA/dev/"
  print('newsqa_datadir:', newsqa_datadir)
  newsqa_files = sorted(glob.glob(newsqa_datadir+"*.txt"))
  print('squad_files, type:', type(squad_files), ', len:', len(squad_files))
  print('newsqa_files, type:' , type(newsqa_files), ', len:', len(newsqa_files))

  for i, squad_file in enumerate(squad_files) : 
    with ropen(squad_file) as fs: squad_text = fs.read()
    fs.close()
    with ropen(newsqa_files[2*i]) as fn1: newsqa1_text = fn1.read()
    fn1.close()
    with ropen(newsqa_files[2*i + 1]) as fn2: newsqa2_text = fn2.read()
    fn2.close()
    
    print('squad_file:', squad_file)
    print('newsqa1_file:', newsqa_files[2*i])
    print('newsqa2_file:', newsqa_files[2*i + 1])

    content = squad_text + newsqa1_text  + newsqa2_text
    squad_merged_datadir = "dataset/QA/SQuAD/" + version + "/dev_merged/" 
    merge_file = squad_file.replace('dev', 'dev_merged' )
    print('merge_file name:', merge_file)
    with wopen(merge_file) as fm:
      fm.write(content)
    #if i==10: break



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



def saveSQuAD_QuestionContent_Paragraphs(version):
  datadir = "dataset/QA/SQuAD/" + version + "/"
  os.makedirs(datadir + 'dev_Warsaw',exist_ok=True)
  if version == "1.1":
    dataset= jload( datadir + "dev-v1.1.json")
  else : #version ="2.0"
    dataset= jload( datadir + "dev-v2.0.json")
  #data is []
  #print('data[0]:', dataset['data'][0])
  for count, article in enumerate(dataset['data']):
      if count < 1: continue
      context = ''
      qidMap = dict()
      questionsArray = []
      for i, paragraph in enumerate(article['paragraphs']):
         dir = datadir + 'dev_Warsaw/' + str(i)
         os.makedirs(dir, exist_ok=True)
         print( article['title'] )
         fname = dir + "/" +  article['title']  + ".txt"
         print('fname:', fname)

         context += paragraph['context']
         with wopen(fname) as fcontext :
            fcontext.write(context + "\n")
         fcontext.close()
         
         questions = paragraph['qas']
         for question in questions:
             qid = question['id']
             q=question['question']
             questionsArray.append(q)
             qidMap[qid] = article['title']  + "_" + str(i) + "_" + q
          
         output = json.dumps(qidMap)
         fqidname =  dir + "/" +  article['title'] + '_quest_id.json'
         print('fqidname:', fqidname)
         with wopen(fqidname) as f:
           f.write(output + "\n")
         f.close()
         
         fqname = dir + "/" +  article['title']  + "_quest.txt" 
         print('fqname:', fqname)
         qtext = '\n'.join(questionsArray)
         with wopen(fqname) as fquest:
           fquest.write(qtext + "\n")
         fquest.close()
      if count == 1: break



#answerSQuADFromFile_Paragraphs('dataset/QA/SQuAD/1.1/dev_Warsaw/')
 
def answerSQuADFromFile_Paragraphs(path):
  with os.scandir(path) as it:
    for entry in it:
        if not entry.name.startswith('.') and entry.is_dir():
            print(entry.name)            
            number = int(entry.name) 
            if number < 28: continue
            answerSQuADParagraphsFromFile('dataset/QA/SQuAD/1.1/dev_Warsaw/', entry.name,'Warsaw')
            
  

#answerSQuADParagraphsFromFile('dataset/QA/SQuAD/1.1/dev_Warsaw/', '0','Warsaw')

def answerSQuADParagraphsFromFile(dir, number, fname):
  
  datadir = dir + number + "/"
  fname = datadir + fname
  fqidname = fname + '_quest_id.json'
  qids = jload( fqidname)
  print('qids, len:', len(qids), 'content:\n', qids)
  talkansOrg, talkansYifan, thinkans, bertans = reason_with_pytalk_FromFile(fname)
  print('answer, len:', len(talkansOrg))
  print('\n talkansOrg:', talkansOrg)
  print('\n talkansYifan:', talkansYifan)
  print('\n thinkans:', thinkans)
  print('\n bertans:', bertans)
  qidTalkAnswerOrgMap = dict()
  qidTalkAnswerYifanMap = dict()
  qidThinkAnswerMap = dict()
  qidBertAnswerMap = dict()
  
  for j, qid in enumerate(qids):
      qidTalkAnswerOrgMap[qid] = talkansOrg[j]
      qidTalkAnswerYifanMap[qid] = talkansYifan[j]
      qidThinkAnswerMap[qid] = thinkans[j]
      qidBertAnswerMap[qid] = bertans[j]
  print('\nqidTalkAnswerOrgMap:', qidTalkAnswerOrgMap)
  print('\nqidTalkAnswerYifanMap:', qidTalkAnswerYifanMap)
  print('\nqidThinkAnswerMap:', qidThinkAnswerMap)
  print('\nqidBertAnswerMap:', qidBertAnswerMap)  
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
  
  with ropen(fname + '.txt') as f: 
    text = f.read()
  f.close()
  
  words = text.split( )
  total = len(words)
  print('\n total words number:', total )
  with wopen(datadir + 'wordsnumber.txt' ) as f:
    f.write('total words number: ' + str(total) + "\n")
  f.close() 



#put EvalCrafts/dataset/QA/SQuAD/1.1/evaluate-v1.1.py to EvalCrafts/evaluate.py
def evaluateSQuADParagraphs (): #dev_Warsaw
  datadir = "dataset/QA/SQuAD/1.1/"
  dataset= jload( datadir + "dev-v1.1.json")
  content = ''
  import evaluate as ev
  for count, article in enumerate(dataset['data']):
      if count < 1: continue

      content = 'article, paragraphs number, total words, talk_origin F1, talk_origin_exact_match,'
      content += 'talk_yifan_F1, talk_yifan_exact_match, think_F1, think_exact_match, bert_F1, bert_exact_match' + '\n'

      for i, paragraph in enumerate(article['paragraphs']):
        dir = datadir + 'dev_Warsaw/' + str(i) + "/"
        with ropen(dir + 'Warsaw.txt') as f: text = f.read()
        f.close()

        words = text.split( )
        total = len(words)
        print('\n total words number:', total )

	
        predictions = jload( dir + 'predictions_talkOrigin.json')
        score =ev.evaluate(dataset['data'], predictions, i)
        em_talkOrigin = round(score['exact_match'], 2)
        f1_talkOrigin = round(score['f1'], 2)

        predictions = jload( dir + 'predictions_talkYifan.json')
        score =ev.evaluate(dataset['data'], predictions, i)
        em_talkYifan = round(score['exact_match'], 2)
        f1_talkYifan = round(score['f1'], 2)

        predictions = jload( dir + 'predictions_think.json')
        score =ev.evaluate(dataset['data'], predictions, i)
        em_think = round(score['exact_match'], 2)
        f1_think = round(score['f1'], 2)


        predictions = jload( dir + 'predictions_bert.json')
        score =ev.evaluate(dataset['data'], predictions, i)
        em_bert = round(score['exact_match'], 2)
        f1_bert = round(score['f1'], 2)

        content += 'Warsaw' + ',' + str(i) + ',' + str(total) + ','
        content += str(f1_talkOrigin) + ',' + str(em_talkOrigin) + ','
        content += str(f1_talkYifan) + ',' + str(em_talkYifan) + ','
        content += str(f1_think) + ',' + str(em_think) + ','
        content += str(f1_bert) + ',' + str(em_bert) + '\n' 
        
        if i == 32: break
      if count == 1: 
        break

  toFile = datadir + 'dev_Warsaw/' + "score.csv"
  print('save score to file:', toFile)
  with wopen(toFile) as fscore:
    fscore.write(content + "\n")
  fscore.close()



def saveSQuAD_QuestionContentOnArticle(version, number):
  datadir = "dataset/QA/SQuAD/" + version + "/"
  os.makedirs(datadir + 'dev',exist_ok=True)
  if version == "1.1":
    dataset= jload( datadir + "dev-v1.1.json")
  else : #version ="2.0"
    dataset= jload( datadir + "dev-v2.0.json")
  #data is []
  #print('data[0]:', dataset['data'][0])
  contextlist = []
  questionlist = []
  for count, article in enumerate(dataset['data']):
      if count%number == 0:
        if len(contextlist) >0:
          print('\narticle file name:', fname)
          print('question file name:', fqname)
          print('contextlist, len:', len(contextlist))
          print('questionlist, len:', len(questionlist))
          with wopen(fname) as fcontext :
            context = '\n'.join(contextlist)
            words = context.split()
            totalwordsNum = len(words) 
            print('total words number:', totalwordsNum)
            fcontext.write(context)
          fcontext.close()
          with wopen(fqname) as fquest:
             qcontext = '\n'.join(questionlist)
             fquest.write(qcontext)
          fquest.close()           
        fname = datadir + "dev/" + article['title'] + ".txt"
        fqname = datadir + "dev/" + article['title']  + "_quest.txt"        
        contextlist = []
        questionlist = []            
      
      for i, paragraph in enumerate(article['paragraphs']):
         contextlist.append(paragraph['context'])
         questions = paragraph['qas']
         for question in questions:
           q=question['question']
           questionlist.append(q)




def answerSQuADFromFileOnArticle(version, number):
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
  qids = []
  talkansOrg = []
  talkansYifan = []
  thinkans = []
  bertans = []
  for count, article in enumerate(dataset['data']):

      if count%number == 0: 
        print('qids length:', len(qids))
        if len(qids) > 0:
          for j, qid in enumerate(qids):
            qidTalkAnswerOrgMap[qid] = talkansOrg[j]
            qidTalkAnswerYifanMap[qid] = talkansYifan[j]
            qidThinkAnswerMap[qid] = thinkans[j]
            qidBertAnswerMap[qid] = bertans[j]
          print('\nqidTalkAnswerOrgMap:', qidTalkAnswerOrgMap)
          print('\nqidTalkAnswerYifanMap:', qidTalkAnswerYifanMap)
          print('\nqidThinkAnswerMap:', qidThinkAnswerMap)
          print('\nqidBertAnswerMap:', qidBertAnswerMap)  
          outputTalkOrig = json.dumps(qidTalkAnswerOrgMap)
          with wopen(datadir + 'predictions_talkOrigin' + shortFname + '.json' ) as ftalkOrigin:
            ftalkOrigin.write(outputTalkOrig + "\n")
          ftalkOrigin.close()

          outputTalkYifan = json.dumps(qidTalkAnswerYifanMap)
          with wopen(datadir + 'predictions_talkYifan_' + shortFname + '.json' ) as ftalkYifan:
            ftalkYifan.write(outputTalkYifan + "\n")
          ftalkYifan.close()
  
          outputThink = json.dumps(qidThinkAnswerMap)
          with wopen(datadir + 'predictions_think_' + shortFname + '.json' ) as fthink:
            fthink.write(outputThink + "\n")
          fthink.close() 

          outputBert = json.dumps(qidBertAnswerMap)
          with wopen(datadir + 'predictions_bert_' + shortFname + '.json' ) as fbert:
            fbert.write(outputBert + "\n")
          fbert.close()
        
        #clearup
        qids = [] 
        qidTalkAnswerOrgMap = dict()
        qidTalkAnswerYifanMap = dict()
        qidThinkAnswerMap = dict()
        qidBertAnswerMap = dict()
        talkansOrg = []
        talkansYifan = []
        thinkans = []
        bertans = []
        shortFname = article['title']
        fname = datadir + "dev/" + article['title']
        print('read file:', fname)
        talkansOrg, talkansYifan, thinkans, bertans = reason_with_pytalk_FromFile(fname)
        print('answerSQuAD, talkansOrg:', talkansOrg)
        print('answerSQuAD, talkansYifan:', talkansYifan)
        print('answerSQuAD, thinkans:', thinkans)
        print('answerSQuAD, bertans:', bertans)

      for i, paragraph in enumerate(article['paragraphs']):
        for qa in paragraph['qas']:
          qid = qa['id']
          qids.append(qid)


        


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

  
'''
if __name__ == "__main__":


     
   #saveSQuAD_QuestionContent("1.1" )
    #answerSQuADFromFile("1.1")
     
    #answerSQuADFromText("1.1")

    answerNewsQA()
    print('DONE')
'''
    
 
if __name__ == '__main__' :
  pass



