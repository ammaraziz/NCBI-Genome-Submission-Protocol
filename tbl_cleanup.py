#!/usr/bin/env python

# This script will modify a .tbl file generated         
# from Prokka v1.13 to (attempt) meet NCBI standards.   
# What it corrects:                                     
#	~ score and dbxref lines are removed                
# 	~ product identifier is heavily modified:           
#		~ line is modified to remove square brackets([])
#		~ "locus_tag" changed to "old_locus_tag"         
#		~ more but I can't remember.

import sys
inFile = sys.argv[1]
outFile = sys.argv[2]

# read in tbl file
with open(inFile) as f:
    content = f.readlines()

# search if output of product is any of these
want = 'gene|locus_tag|protein_id|product'

print("working on " + str(inFile))
with open(outFile, 'w') as w:
    for l in content:
        if "product\t[" in l:
            m = l.replace("][", "] [").replace("[", "").replace("=", "\t").split("]")
            m = [x.lstrip(" ") for x in m]
            m = [e for e in m if e not in ("gbkey\tCDS", "\n", "")]
            for item in m:
                if bool(re.search(want, item)):
                    if "product" in item:
                        w.write(item.replace("gene\t", "") + '\n')
                    elif "locus_tag" in item:
                        w.write('\t\t\t' + 'old_' + item + '\n')
                    else:
                        m[m.index(item)] = '\t\t\t' + item
                        w.write('\t\t\t' + item + '\n')
        elif "score" in l:
            pass
        elif "dbxref" in l:
            pass
        else:
            w.write(l)
print("Done! May the gods bless this annotation")