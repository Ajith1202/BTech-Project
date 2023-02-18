import sys
import math
import os
from tabulate import tabulate
import pandas


def calc_stat(fname):

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
    
    if c==0:
        return ["null", "null"]
    Ei= c/256
    X= 0
    k=0
    for num in count.values():
        k+=1
        X+= (num- Ei)**2

    X= X+ (256-k)* (Ei**2)
    chisqr= X/Ei

    file.close()
    return [entropy,chisqr]


def beautify_print(chisq, file_entropy):

    added= dict()
    for file in chisq:
        added[file]= False
    rows= []
    normal= []
    encrypted= []
    for file in chisq:
        if not added[file]:
            if file[-4:]== ".gpg":
                unencr=  file[:-4]
                if unencr in chisq:
                    normal.append(unencr)
                    encrypted.append(file)
                    added[file]= True
                    added[unencr]= True
            else:
                temp= file+ ".gpg"
                if temp in chisq:
                    normal.append(file)
                    encrypted.append(temp)
                    added[file]= True
                    added[temp]= True
    for rfile in chisq:
        if not added[file]:
            if rfile[-4:]== ".gpg":
                encrypted.append(rfile)
                added[rfile]= True
            else:
                normal.append(rfile)
                added[rfile]= True
    i=0
    j=0
    while i < len(normal) or j< len(encrypted):
        if i < len(normal) and j<len(encrypted):
            rows.append([normal[i], chisq[normal[i]], file_entropy[normal[i]], encrypted[j],chisq[encrypted[j]], file_entropy[encrypted[j]]])
            i+=1
            j+=1
        elif i<len(normal):
            rows.append([normal[i], chisq[normal[i]],file_entropy[normal[i]], "","",""])
            i+=1
        elif j<len(encrypted):
            rows.append(["","","", encrypted[j], chisq[encrypted[j]], file_entropy[encrypted[j]]])
            j+=1
    headers=["Normal files", "<--Chi-square", "<--Entropy", "Encrypted files", "<--Chi-square", "<--Entropy"]
    print (tabulate(rows, headers, tablefmt="grid", numalign= "center"))

    # print('---------------------------------------------------------------------------------------------------------------------------')
    # print()
    # headers= ["Normal files", "<--Chi-square", "Encrypted files", "<--Chi-square"]
    # print(pandas.DataFrame(rows, headers))


    



if __name__== "__main__":

    file_entropy= dict()
    chisq= dict()

    max_enc = float('-inf')
    min_non_enc = float('inf')
    count_enc = count_non_enc = 0
    avg_enc = avg_non_enc = 0
    median_enc, median_non_enc = [], []
    wrong_enc = wrong_non_enc = 0

    for root, dirs, files in os.walk(".", topdown= True):
        for name in files:
            
            if name[-10:] == "entropy.py":
                continue

            fname= os.path.join(root, name)
            stat= calc_stat(fname)

            file_entropy[fname]= stat[0]
            chisq[fname]= stat[1]

            if name[-4:] == ".gpg":
                if stat[1] > 293.25:
                    wrong_enc += 1
                count_enc += 1
                avg_enc += stat[1]
                max_enc = max(max_enc, stat[1])
                median_enc.append(stat[1])
            else:
                if stat[1] < 293.25:
                    wrong_non_enc += 1
                count_non_enc += 1
                avg_non_enc += stat[1]
                min_non_enc = min(min_non_enc, stat[1])
                median_non_enc.append(stat[1])
            # print(fname," --", " Entr= ", stat[0], "    Chisq= ", stat[1])
    
    median_enc.sort()
    median_non_enc.sort()

    print(count_enc, count_non_enc)
    count_enc = len(median_enc)
    count_non_enc = len(median_non_enc)

    if count_enc % 2 == 0:
        print(count_enc // 2)
        m1 = median_enc[count_enc // 2]
        m2 = median_enc[count_enc // 2 - 1]
        
        m = (m1 + m2) / 2
    else:
        m = median_enc[count_enc // 2]


    print(f"Median chi square for Encrypted: {str(m)}")

    if count_non_enc % 2 == 0:
        m1 = median_non_enc[count_non_enc // 2]
        m2 = median_non_enc[count_non_enc // 2 - 1]
        
        m = (m1 + m2) / 2
    else:
        m = median_non_enc[count_non_enc // 2]
    
    print(f"Median chi square for Non-Encrypted: {str(m)}")
    
    print("--------------------------------------------------------------------")

    print(f"Average chi square for Encrypted: {str(avg_enc / count_enc)}")
    print(f"Average chi square for Non-Encrypted: {str(avg_non_enc / count_non_enc)}")

    print("--------------------------------------------------------------------")

    print(f"Max chi square for Encrypted: {str(max_enc)}")
    print(f"Min chi square for Non-Encrypted: {str(min_non_enc)}")

    print("--------------------------------------------------------------------")

    print(f"Total Number of analysed files: {str(count_enc + count_non_enc)}")

    print("--------------------------------------------------------------------")

    print(f"Percentage of wrongly detected Encrypted files: {str(wrong_enc / count_enc * 100) + '%'}")
    print(f"Percentage of wrongly detected Non-Encrypted files: {str(wrong_non_enc / count_non_enc * 100) + '%'}")

    print("--------------------------------------------------------------------")

    print(f"Percentage of wrongly detected files: {str((wrong_enc + wrong_non_enc) / (count_enc + count_non_enc) * 100) + '%'}")
    #beautify_print(chisq, file_entropy)
    
