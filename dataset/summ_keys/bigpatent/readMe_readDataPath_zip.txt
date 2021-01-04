This directory contains :
1. Readme
2. readData.py  <-- code to read data
3. Tar files for training, validation and test data

Each tar contains 9 folders one for each of the cpc code. Each cpc folder
contains multiple gzip-compressed JSON lines. 

Follow the following steps to run the readData.py file:

Requirement : Python 2.7 and packages: gzip, json

1. Uncompress all the tar file like this : tar -xvzf test.tar.gz
2. Run this to read one of the files from cpc code 'd' in test split:
python readData.py --cpc_code d --split_type test --input_path .
