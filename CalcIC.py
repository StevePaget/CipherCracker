# Calculate Index of Coincidence

def getIC(text):
    text = "".join([c.upper() for c in text if c.isalpha()])
    counts = [0 for _ in range(26)]
    totcount=0
    for letter in text:
        counts[ord(letter)-65] += 1
        totcount += 1
    ictotal = sum([counts[i]*(counts[i]-1) for i in range(26)])
    ic = ictotal / (totcount*(totcount-1))
    return ic

def getComparativeIC(text):
    # compares each letter frequency to that of English
    flist = [8.497,	1.492, 	2.202, 	4.253, 	11.162, 2.228, 	2.015, 	6.094, 	7.546, 	0.153, 	1.292, 	4.025, 	2.406,
         	6.749, 	7.507, 	1.929, 	0.095, 	7.587, 	6.327, 	9.356, 	2.758, 	0.978, 	2.560, 	0.150, 	1.994, 	0.077]
    nlist = [0 for x in range(26)]
    lettercount=0
    for c in text.upper():
        cnum = ord(c)-65
        if 0 <= cnum <=25:
            lettercount +=1
            nlist[cnum] +=1
    nlist = [n/lettercount*100 for n in nlist]
    score = sum([nlist[i] * flist[i] for i in range(26)])
    return score





