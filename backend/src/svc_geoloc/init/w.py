import csv
with open('world-in-italian.csv','rt') as f:
    res = {l[1].upper(): l[3] for l in csv.reader(f)}
    
print (res)