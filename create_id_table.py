import pickle
import sys
import csv
import time
from extract_features import Block

with open(sys.argv[1], "rb") as inf:
    dramen = pickle.load(inf)


out = []
for i, (_, drama) in enumerate(dramen):
    id = (i+1)*10000
    for j, rede in enumerate(drama):
        out.append([id+j, '"' + rede.text.strip() + '"'])


# creating a timestamp
ts = time.strftime("%Y%m%d-%H%M")
ofName = f"ID_list_{ts}.csv"
# write the list of lists as a csv
with open(ofName, "w", newline="") as of:
    writer = csv.writer(of, delimiter=",", quotechar='"')
    writer.writerows(out)