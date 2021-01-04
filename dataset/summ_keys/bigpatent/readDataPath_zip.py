import json
import gzip
import os
import sys
import argparse
import codecs

def readData(input_path,split_type,cpc_code):
    file_names = os.listdir(os.path.join(input_path,split_type,cpc_code))
    # reading one of the gz files.
    file_name = file_names[0]
    print("Reading file "+ file_name + " from "+ split_type+" split for cpc code " + cpc_code)
    with gzip.open(os.path.join(input_path,split_type,cpc_code,file_name),'r') as fin:
        for row in fin:
            json_obj = json.loads(row)
            print("Fields present in each of the json object:")
            print(json_obj.keys())
            # uncomment to print the publication number, abstract and description
            print(json_obj["publication_number"])
            file_abs = "abs/" + json_obj["publication_number"] + ".txt"
            with codecs.open(file_abs, 'w',encoding='utf8') as f:
              f.write(json_obj["abstract"] + "\n")   
            f.close()
            f_content = "content/" + json_obj["publication_number"] + ".txt"
            with codecs.open(f_content, 'w',encoding='utf8') as f:
              f.write(json_obj["description"] + "\n")
            f.close()
 
            print(json_obj["abstract"])
            print("\n\n" + json_obj["description"])
            #break

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Read data')
    parser.add_argument('--cpc_code', type=str, help='can be a, b,c,d,e,f,g,h,y')
    parser.add_argument('--split_type', type=str, help='can be train, test, val')
    parser.add_argument('--input_path', type=str, help='path to data')

    args = parser.parse_args()
    split_type = args.split_type
    cpc_code = args.cpc_code
    input_path = args.input_path

    readData(input_path,split_type,cpc_code)

