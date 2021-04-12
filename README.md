## Project Description

** The system uses dependency links for building Text Graphs, that with help of a centrality algorithm like *PageRank*, doctalk, StanzaGraphs, 
 1. support question answering 
 2. extract relevant keyphrases, summaries and relations from text documents
 A *SWI-Prolog* based module adds an interactive shell for talking about the document with a dialog agent that extracts for each query the most relevant sentences covering the document. Spoken dialog is also available if the OS supports it. Developed with *Python 3*, on OS X, but portable to Linux.**


## Dependencies:
  doctalk: https://github.com/Yifan-G/DocTalk
  StanzaGraphs: https://github.com/Yifan-G/StanzaGraphs
  copy doctalk or StanzaGraphs directory into EvalCraft directory

## dataset:
dataset/QA: support SQuAD and  NewsQA
dataset/summ_keys: bigpatent, cnn_big, Krapivin2009

Question Answering dataset: https://github.com/sebastianruder/NLP-progress/blob/master/english/question_answering.md
bigpatent for abstract: https://evasharma.github.io/bigpatent/



## Setup enviroment in linux:
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

install  EvalCraft dependent packages, in  EvalCraft diretory
  $ pip install -r requirements.txt

if doctalk is used:
    copy doctalk requirements.txt into doctalk directory
    cd to  doctalk directory
    $ pip install -r requirements.txt

 if StanzaGraphs is used, go to StanzaGraphs directory, run
    $ pip install -r requirements.txt
 
check packages version by command
    $ pip freeze 
run for every access
    $ . venv/bin/activate

## Run summ_keys
   There are three files: 
   eval_sumkeys-cnn_big.py: for cnn_big
   eval_sumkeys-Krapivin2009.py, for Krapivin2009.py
   eval_sumkeys-bigpatent.py, for bigpatent

For example:
```python3 -i eval_sumkeys-cnn_big.py```

then:

```go()``` 

then:
 
copy files from dataset/summ_keys/cnn_big/docsutf8 to dataset/summ_keys/cnn_big/temp_docs
keys and abs created at dataset/summ_keys/cnn_big/out, score csv are for each file


## Run Question Answering
```python3 -i eval_qa.py```

then run the function you want


