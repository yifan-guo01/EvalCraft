## Project Description

** The system uses doctalk to build Text Graphs, extract relevant keyphrases, summaries from text documents
Developed with Python 3.6, on Linux centos 7
doctalk downloads stanza_corenlp and nltk_data automatically , please make sure the server can access internet.


## The Directories 
 - EvalCraft           # call doctalk and get ROUGE Score
 - EvalCraft/doctalk/  # Keyphrase Extraction and Summarization
 - EvalCraft/StanzaGraphs/  # Keyphrase Extraction and Summarization 
 - EvalCraft/dataset/  # data and doctalk's output saved in different datasets


## Setup Enviroment in Linux:
- python 3.6 or newer, pip3, java 9.x or newer, SWI-Prolog 8.x or newer, graphviz
- also, having git installed is recommended for easy updates
The steps are as below with root:
$ yum install epel-release 
$ yum install python3-pip
$ python3 -m pip install --upgrade pip setuptools wheel
$ pip3 install virtualenv
$ virtualenv -p python3.6 venv
$ . venv/bin/activate

install java
    $ yum -y install java

install  EvalCraft dependent packages, under EvalCraft diretory
  $ pip install -r requirements.txt
install StanzaGraphs dependent packages, under StanzaGraphs diretory
  $ pip install -r requirements.txt

run for every access
    $ . venv/bin/activate


## Dataset:
EvalCraft/dataset/
  - Inspec  # Keyphrase Extraction
  - Krapivin_Full    # Keyphrase Extraction and Summarization
  - Krapivin_NoAbstract  # remove abstract from article
  - NUS_Full   # Keyphrase Extraction and Summarization
  - NUS_NoAbstract  # remove abstract from article
  - SemEval_Full    # Keyphrase Extraction and Summarization
  - SemEval_NoAbstract   # remove abstract from article
  - PubMed    # for Summarization
  - arXiv     # for Summarization

each dataset has the subdirectories:
  - abs   # abstract
  - docsutf8   # original article
  - keys    # key words
  - temp_docs # stanza_corenlp parser json files
  - out    # save doctalk Keyphrase Extraction and Summarization
    - keys # for Keyphrase Extraction
    - abs # Summarization

each dataset includes about 20 articles as sample, you can put all articles into docsutf8 to do full test


## Run eval_sumkeys Python Files to Get Keyphrase Extraction and Summarization
   There are several files that the names start from eval_sumkeys-, each file for one dataset.
   - eval_sumkeys-Inspec.py  
   - eval_sumkeys-Krapivin_Full.py 
   - eval_sumkeys-Krapivin_NoAbstract.py
   - eval_sumkeys-NUS_Full.py 
   - eval_sumkeys-NUS_NoAbstract.py
   - eval_sumkeys-SemEval_Full.py   
   - eval_sumkeys-SemEval_NoAbstract.py  
   - eval_sumkeys-PubMed.py 
   - eval_sumkeys-arXiv.py

    Configuration:
    in eval_sumkeys-* file, such as eval_sumkeys-Krapivin_Full.py
      - # 2 forces deletion of json in temp_docs, 1=forces deletion of keys+abs in out
        force=0
      - # number of keyphrases and summary sentences
        wk,sk=10,8  # wk for number of keyphrases, sk for number of summary sentences
      - # sets max number of documents to be processed, all if None or 0
        max_docs = 0


  How to run, for example:
  ```python eval_sumkeys-PubMed.py ```


Then 
copy files from dataset/PubMed/docsutf8 to dataset/PubMed/temp_docs, save stanza_corenlp parser json files into dataset/PubMed/temp_docs
keys and abs created at dataset/PubMed/out

then print final ROUGE score, such as

      EXTRACTED KEYS AND ABSTRACTS
                      Precision,          Recall,           F-Measure
      KEYS ROUGE 1 : 0.29827969008116073 0.4364484126984127 0.34144388195074693
      ABS ROUGE 1 : 0.49158123673586773    0.5043105876111166    0.48753007181944447
      ABS ROUGE 2 : 0.2825046451122882    0.29587238206313704    0.28307249204689017
      ABS ROUGE l : 0.5404513073395705    0.5515895825486291    0.537938640371076
      ABS ROUGE w : 0.27062101520754644    0.1830950391544452    0.21442998206315905
      DONE
      SYSTEM : DOCTALK
      wk 10 sk 8
      with_full_text =  False
      max_docs =  0
      force =  1






