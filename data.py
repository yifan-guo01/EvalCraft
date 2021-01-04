import glob
import sys
import os

#cn_dm_dir = "dataset/cnn_dm_small/"
cn_dm_dir = "dataset/cnn_big/"
out_abs_dir  = "cnn_dm/abs/"
out_keys_dir = "cnn_dm/keys/"

data_files = sorted(glob.glob(cn_dm_dir+"orig/*.story"))

def generate() :
  for df in data_files:
    dfname=justFname(df)
    kf=cn_dm_dir+"keys/"+dfname+".key"
    af=cn_dm_dir+"abs/"+dfname+".txt"
    tf=cn_dm_dir+"docsutf8/"+dfname+".txt"
    print('------',tf)
    with open(df,'r') as f:
      with open(kf,'w') as k:
        with open(af, 'w') as a:
          with open(tf, 'w') as t:
            flag = False
            for i, l in enumerate(f.readlines()):
              l = l.replace("\n", " ")
              l = l.replace("`", " ")
              l = l.replace("' ", " ")
              if len(l) < 3: continue
              if l == '@highlight ':
                #print(i,l)
                flag = True
              else:
                if flag:
                  k.write(l+"\n")
                  l = l + "."
                  a.write(l+"\n")
                  #print(i, l)
                  flag = False
                else :
                  #print(i,l)
                  t.write(l+"\n")



def path2fname(path):
    return path.split('/')[-1]


def trimSuf(path):
  return ''.join(path.split('.')[:-1])


def justFname(path):
  return trimSuf(path2fname(path))



if __name__ == '__main__' :
  pass
  generate()
