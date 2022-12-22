import sys
import math
import os

def calc_entropy(fname):

    file= open(fname,"r+b")
    count= dict()
    c= 0
    for line in file:
        for ch in line:
            c+=1
            if ch in count:
                count[ch]+=1
            else:
                count[ch]=1

    entropy= 0
    for num in count.values():
        p= num/c
        entropy-= p*math.log(p,2)

    file.close()
    return entropy



if __name__== "__main__":

    file_entropy= dict()
    for root, dirs, files in os.walk(".", topdown= True):
        for name in files:
            fname= os.path.join(root, name)
            entropy= calc_entropy(fname)
            file_entropy[fname]= entropy

    for row in file_entropy.items():    
        print(row)
    




