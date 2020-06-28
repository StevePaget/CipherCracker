from tkinter import *
import tkinter.font as tkFont
import tkinter.scrolledtext as scrolledtext
import random
import itertools
from ngram_score import ngram_score
import CalcIC
import multiprocessing as mp


class App:
    def __init__(self, master):
        self.titlefont = tkFont.Font(family="Arial", size=18, slant="italic")
        self.buttonfont = tkFont.Font(family="consolas", size=12)
        self.bigfont = tkFont.Font(family="consolas", size=24)
        self.master = master
        self.runningSubDecrypt = False
        self.ciphertextContents = ""
        self.activecolour = "#7261A3"
        self.inactivecolour = "#A67DB8"

        self.caesarbutton = Button(master, text="Caesar Shift",  fg= "white", font=self.buttonfont, command=self.showCaesar)
        self.rsubbutton = Button(master, text="Random Sub", fg= "white",font=self.buttonfont, command=self.showRsub)
        self.vigenerebutton = Button(master, text="Vigenere",  fg= "white",font=self.buttonfont, command=self.showVigenere)
        self.caesarbutton.grid(row=0, column=1, sticky="EW")
        self.rsubbutton.grid(row=0, column=2, sticky="EW")
        self.vigenerebutton.grid(row=0, column=3, sticky="EW")
        master.rowconfigure(1,weight=1)
        master.rowconfigure(2, minsize=200)

        # Main (left) frame stuff
        mainframe = Frame(master)
        mainframe.grid(row=0, column=0,rowspan=2, sticky=N)
        l1 = Label(mainframe, text="Ciphertext:", font=self.titlefont)
        l1.grid(row=0, column=0, sticky=W)
        self.entryBox = Text(mainframe, height=10, width=75,font="courier 18", bd=2, selectborderwidth=3)
        self.entryBox.grid(row=1, column=0, columnspan=3, sticky=EW)
        self.decryptedbox =  Text(mainframe, height=10,width=75, font="courier 18", bd=2)
        self.decryptedbox.grid(row=3, column=0, columnspan=3, sticky=W + E)
        self.reformatCiphertextButton = Button(mainframe, text="Reformat", font=self.buttonfont, command=self.reformatCiphertext)
        self.reformatCiphertextButton.grid(row=0, column=1, sticky=EW)
        self.clearSpacesButton = Button(mainframe, text="Trim", font=self.buttonfont, command=self.clearSpaces)
        self.clearSpacesButton.grid(row=0, column=2, sticky=EW)
        l2 = Label(mainframe, text="Plaintext:", font=self.titlefont)
        l2.grid(row=2, column=0, columnspan=3, sticky=W)
        mainframe.rowconfigure(4,minsize=30)
        self.contents = self.entryBox.get(1.0, END)
        self.entryBox.bindtags(('Text','.!frame.!text', '.', 'all'))
        
        self.entryBox.bind("<Key>", self.letterEntered)
        self.entryBox.bind("<Motion>", self.onMoveEntry)
        self.decryptedbox.bind("<Motion>", self.onMoveDecrypt)

        #Random Subtitution elements
        self.randomsubrightframe = Frame(master)
        self.randomsubrightframe.grid(row=1, column=1, sticky=NSEW, rowspan=2,columnspan=3)
        self.rsubCanvas = Canvas(self.randomsubrightframe,width=475, height=600)
        self.rsubCanvas.grid(row=1, column=0, columnspan=2,sticky="NSEW")
        self.letterFrequencies = Button(self.randomsubrightframe,font=self.buttonfont, text="Show Letter Frequencies", command= lambda x = self.rsubCanvas: self.showLetterFrequencies(x, self.ciphertextContents))
        self.letterFrequencies.grid(row=0, column=0,sticky="W")
        self.vowelTrowel = Button(self.randomsubrightframe, text="Show Vowel Trowel", font=self.buttonfont,command=self.showVowelTrowel)
        self.vowelTrowel.grid(row=0, column=1,sticky="E")
        self.randomsubbottomframe = Frame(master)
        self.randomsubbottomframe.grid(row=2, column=0, sticky=NSEW)
        self.swaptableLabel = Label(self.randomsubbottomframe, text="Enter your guesses of letter swaps here:", font=self.titlefont)
        self.swaptableLabel.grid(row=0, column=1, columnspan=26, sticky=EW)
        self.randomsubbottomframe.columnconfigure(0,minsize=20)
        self.topletters = []
        for x in range(26):
            self.topletters.append(
                Label(self.randomsubbottomframe, text=chr(65 + x), width=3, font=self.buttonfont).grid(row=6, column=x+1, sticky=W))
        self.bottomletters = []
        self.mappings = [StringVar() for x in range(26)]
        self.oldMappings = ["" for x in range(26)]
        for mapping in self.mappings:
            mapping.trace("w", self.checkentries)
        for x in range(26):
            self.bottomletters.append(
                Entry(self.randomsubbottomframe, width=3, font=self.buttonfont, justify=CENTER, textvariable=self.mappings[x]).grid(row=7,
                                                                                                                column=x+1,
                                                                                                                sticky=W))
        self.go = Button(self.randomsubbottomframe, text="Auto Decrypt", font=self.buttonfont, command=self.toggleAutoSubstitution)
        self.go.grid(row=8, column=1, columnspan=9)
        self.random = Button(self.randomsubbottomframe, text="Make Random Key", font=self.buttonfont, command=self.randomKey)
        self.random.grid(row=8, column=8, columnspan=9)
        self.clear = Button(self.randomsubbottomframe, text="Clear Key", font=self.buttonfont, command=self.clearKey)
        self.clear.grid(row=8, column=15, columnspan=9)

        # Caesar elements
        self.caesarrightframe = Frame(master)
        self.caesarrightframe.grid(row=1, column=1, sticky=NSEW, rowspan=2,columnspan=3)
        self.caesarbottomframe = Frame(master)
        self.caesarbottomframe.grid(row=2, column=0, sticky=NSEW)
        self.caesarCanvas = Canvas(self.caesarrightframe,width=475, height=600)
        self.caesarCanvas.grid(row=1, column=0, columnspan=2,sticky="NSEW")
        clb = Label(self.caesarbottomframe,text="Choose an offset:", font=self.bigfont)
        clb.grid(row=0, column=1)
        self.spinvalue = DoubleVar()
        self.spinvalue.set(1)
        self.caesarSpinner = Spinbox(self.caesarbottomframe, from_=0, to=25,  font=self.bigfont, width=7, command=self.spinchanged, wrap=True, textvariable=self.spinvalue)
        self.caesarSpinner.grid(row=1,column=1)
        self.caesarAutoButton = Button(self.caesarbottomframe,text="Auto Decrypt", font=self.buttonfont, command=self.findBestShift)
        self.caesarAutoButton.grid(row=3, column=1)
        self.caesarbottomframe.columnconfigure(0,weight=1)
        self.caesarbottomframe.columnconfigure(2,weight=1)
        self.caesarbottomframe.rowconfigure(2,minsize=20)
        self.caesarrightframe.rowconfigure(0,minsize=33)
        


        # Vigenere elements
        self.vigenererightframe = Frame(master)
        self.vigenererightframe.grid(row=1, column=1, sticky=NSEW, rowspan=2,columnspan=3)
        self.vigenerebottomframe = Frame(master)
        self.vigenerebottomframe.grid(row=2, column=0, sticky=NSEW)
        self.vigenereCanvas = Canvas(self.vigenererightframe,width=475, height=600)
        self.vigenereCanvas.grid(row=1, column=0, columnspan=2,sticky="NSEW")
        vlb = Label(self.vigenerebottomframe,text="Enter a key word:", font=self.bigfont)
        vlb.grid(row=0, column=1)
        self.vigkeyword = StringVar
        self.vigkey = Entry(self.vigenerebottomframe, textvariable=self.vigkeyword, font=self.bigfont)
        self.vigkey.bindtags(('Entry','.!frame7.!entry', '.', 'all'))
        self.vigAutoButton = Button(self.vigenerebottomframe,text="Auto Decrypt", font=self.buttonfont, command=self.vigAutoDecrypt)
        self.vigAutoButton.grid(row=3, column=1)
        self.vigkey.bind("<Key>", self.vigkeychanged)
        self.vigkey.grid(row=1, column=1)
        self.vigenerebottomframe.columnconfigure(0,weight=1)
        self.vigenerebottomframe.columnconfigure(2,weight=1)
        self.vigenereCanvas.bind("<Button-1>", self.vigCanvasClicked)
        self.frames = {"caesar": [self.caesarrightframe, self.caesarbottomframe], "random":[self.randomsubrightframe, self.randomsubbottomframe], "vigenere":[self.vigenerebottomframe, self.vigenererightframe]}
        self.modebuttons = {"caesar": self.caesarbutton, "random":self.rsubbutton, "vigenere":self.vigenerebutton}
        self.switchMode("caesar")

        # Set up a sample Caesar text
        sample = "gdqd hr zm dwzlokd ne z rdbqds ldrrzfd"
        self.entryBox.insert(1.0, sample)
        self.letterEntered(None)
        self.spinchanged()

        


    def switchMode(self, mode):
        self.currentmode = mode
        for button in self.modebuttons.values():
            button.config(bg=self.inactivecolour)
        self.modebuttons[mode].config(bg=self.activecolour)
        self.decryptedbox.delete(1.0, END)
        for thisframe in self.frames[mode]:
            thisframe.tkraise()

    def showCaesar(self):
        self.switchMode("caesar")
        self.spinchanged()
        if self.runningSubDecrypt:
            self.toggleAutoSubstitution() # turn it off

    def showRsub(self):
        self.switchMode("random")

    def showVigenere(self):
        self.switchMode("vigenere")
        self.vigenereCanvas.delete(ALL)
        self.vigkey.delete(ALL)

    def vigkeychanged(self,e):
        newkey = self.vigkey.get()
        if len(newkey)>0:
            plaintext = vigenereDecrypt(self.entryBox.get(1.0, END), newkey )
            self.decryptedbox.delete(1.0, END)
            self.decryptedbox.insert(1.0, plaintext)


    def toggleAutoSubstitution(self):
        if not self.runningSubDecrypt:
            self.rsubCanvas.delete(ALL)
            self.rsubCanvas.create_text(10, 10, text="Starting search for the substitution key...",
                                        anchor="nw", fill="blue", font=("Arial", 11))
            self.canvasLine = 1
            self.runningSubDecrypt = True
            self.ciphertextContents = self.entryBox.get(1.0, END)
            self.ciphertextContents = self.ciphertextContents.upper()
            self.ciphertextContents = self.ciphertextContents.replace("\n", "")
            self.PipeIn, self.PipeOut = mp.Pipe()
            self.p = mp.Process(target=autoDecryptRSubTask, args=(self.PipeIn, self.ciphertextContents))
            self.p.start()
            self.go.config(text="Stop")
            self.afterID = self.master.after(5000, self.rsubUpdate)
        else:
            self.master.after_cancel(self.afterID )
            self.rsubCanvas.delete(ALL)
            self.runningSubDecrypt = False
            self.p.terminate()
            self.go.config(text="Decrypt!")


    def rsubUpdate(self):
        if self.runningSubDecrypt:
            if self.PipeOut.poll():
                (maxkey) = self.PipeOut.recv()
                self.rsubCanvas.create_text(10, 30 + self.canvasLine*16, text=str(self.canvasLine) + ": Got a new solution. Press Stop when you're happy",
                                        anchor="nw", fill="blue", font=("Arial", 11))
                self.canvasLine += 1
                self.clearKey()
                for x in range(26):
                    self.mappings[x].set(maxkey[x])
                plaintext = substitute(self.ciphertextContents, maxkey)
                self.decryptedbox.delete(1.0, END)
                self.decryptedbox.insert(1.0, plaintext)
            self.afterID =  self.master.after(1000, self.rsubUpdate)


    def reformatCiphertext(self):
        # go through encrypted text and remove spaces & punctuation. Update ciphertext box
        self.clearSpaces()
        newCipherText = ""
        letterCount = 0
        for letter in self.ciphertextContents:
            letterNum = ord(letter) - 65
            if letterNum >= 0 and letterNum <= 25:
                newCipherText += letter
                letterCount += 1
                if letterCount % 5 == 0:
                    newCipherText += " "
        self.entryBox.delete(1.0, END)
        self.entryBox.insert(1.0, newCipherText)
        self.ciphertextContents = newCipherText
        if self.currentmode == "random":
            self.rsubDecrypt()
        elif self.currentmode == "caesar":
            self.spinchanged()
        

    def clearSpaces(self):
        if self.runningSubDecrypt:
            # still doing an auto decrypt, so cancel it
            self.toggleAutoSubstitution()
        # Same as reformat but no extra spaces added
        self.ciphertextContents = self.entryBox.get(1.0, END)
        self.ciphertextContents = self.ciphertextContents.replace(" ", "")
        self.ciphertextContents = self.ciphertextContents.replace("\n", "")
        self.ciphertextContents = self.ciphertextContents.upper()
        newCipherText = ""
        for letter in self.ciphertextContents:
            letterNum = ord(letter) - 65
            if letterNum >= 0 and letterNum <= 25:
                newCipherText += letter
        self.entryBox.delete(1.0, END)
        self.entryBox.insert(1.0, newCipherText)
        self.ciphertextContents = newCipherText
        if self.currentmode == "random":
            self.rsubDecrypt()
        elif self.currentmode == "caesar":
            self.spinchanged()

    def onMoveDecrypt(self, a):
        self.entryBox.tag_delete("hl")
        self.decryptedbox.tag_delete("hl")
        self.entryBox.tag_config("all", background="white")
        self.decryptedbox.tag_config("all", background="white")
        pos=self.decryptedbox.index(CURRENT)
        self.decryptedbox.tag_add("hl", CURRENT, "%s+2c" % CURRENT)
        self.decryptedbox.tag_configure("hl", background="light green")
        hlRange = self.decryptedbox.tag_ranges("hl")
        self.entryBox.tag_add("hl", hlRange[0], hlRange[1])
        self.entryBox.tag_configure("hl", background="light green")
        self.entryBox.see(pos)

    def onMoveEntry(self, a):
        self.entryBox.tag_delete("hl")
        self.decryptedbox.tag_delete("hl")
        self.entryBox.tag_config("all", background="white")
        self.decryptedbox.tag_config("all", background="white")
        pos=self.entryBox.index(CURRENT)
        self.entryBox.tag_add("hl", CURRENT, "%s+2c" % CURRENT)
        self.entryBox.tag_configure("hl", background="light blue")
        hlRange = self.entryBox.tag_ranges("hl")
        self.decryptedbox.tag_add("hl", hlRange[0], hlRange[1])
        self.decryptedbox.tag_configure("hl", background="light blue")
        self.decryptedbox.see(pos)

    def showLetterFrequencies(self,canvas, text):
        if len(text) == 0:
            return
        standardFrequencies = [8.17, 1.49, 2.78, 4.25, 12.70, 2.23, 2.02, 6.1, 6.97, 0.15, 0.77, 4.03, 2.41, 6.75, 7.51,
                               1.92, 0.1, 5.99, 6.34, 9.05, 2.76, 0.98, 2.36, 0.15, 1.97, 0.07]
        canvas.delete(ALL)
        # get letter frequencies first
        letterFrequencies = []
        for letter in range(26):
            letterFrequencies.append(text.count(chr(letter + 65)))
        maxFrequency = max(letterFrequencies)
        numLetters = sum(letterFrequencies)
        topy = 200
        bottomy = 500
        if numLetters == 0:
            return
        for letter in range(26):
            x = 10 + (letter * 18)
            height = letterFrequencies[letter] / maxFrequency * 180
            canvas.create_text(x, topy, text=chr(letter + 65), anchor="n", font=("Arial", 12, "bold"))
            canvas.create_text(x, bottomy, text=chr(letter + 65), anchor="n", font=("Arial", 12, "bold"))
            canvas.create_rectangle(x - 4, topy - height, x + 4, topy, fill="blue")
            canvas.create_text(x, topy + 20, text=str(int(letterFrequencies[letter] / numLetters * 100)),
                                            fill="blue", anchor="n", font=("Arial", 9))
            height = standardFrequencies[letter] / 13 * 180
            canvas.create_rectangle(x - 4, bottomy - height, x + 4, bottomy, fill="red")
            canvas.create_text(x, bottomy + 20, text=str(int(standardFrequencies[letter])), anchor="n",
                                            fill="red", font=("Arial", 9))
        canvas.create_text(10, topy + 40, text="Frequencies in ciphertext (%)", anchor="nw", fill="blue",
                                        font=("Arial", 9))
        canvas.create_text(400, bottomy + 40, text="Target Frequencies in Normal English (%)", anchor="ne", fill="red",
                                        font=("Arial", 9))

    def showVowelTrowel(self):
        # calc most sociable letters
        letterArray = [[chr(x), set([])] for x in range(65, 91)]
        # print(letterArray)
        for pos in range(len(self.ciphertextContents)):
            letterNum = ord(self.ciphertextContents[pos].upper())
            if letterNum >= 65 and letterNum <= 90:
                if pos > 0:
                    prev = ord(self.ciphertextContents[pos - 1].upper())
                    if prev >= 65 and prev <= 90:
                        letterArray[letterNum - 65][1].add(prev)
                if pos < len(self.ciphertextContents) - 1:
                    next = ord(self.ciphertextContents[pos + 1].upper())
                    if next >= 65 and next <= 90:
                        letterArray[letterNum - 65][1].add(next)

        # now sort
        for _ in range(25):
            for j in range(25):
                if len(letterArray[j][1]) > len(letterArray[j + 1][1]):
                    letterArray[j], letterArray[j + 1] = letterArray[j + 1], letterArray[j]

        # now display
        self.rsubCanvas.delete(ALL)
        self.rsubCanvas.create_text(10, 10, text="The following are the most 'sociable' letters in the ciphertext.",
                                        anchor="nw", fill="blue", font=("Arial", 11))
        self.rsubCanvas.create_text(10, 30, text="(They appear alongside most other letters)",
                                        anchor="nw", fill="blue", font=("Arial", 11))
        self.rsubCanvas.create_text(10, 50, text="This means they are probably vowels.",
                                        anchor="nw", fill="blue", font=("Arial", 11))
        y = 80
        for letter in range(1, 10):
            char = letterArray[-letter][0]
            freq = len(letterArray[-letter][1])
            self.rsubCanvas.create_text(50, y + (letter * 30), text=char + " : " + str(freq),
                                            anchor="nw", fill="blue", font=("Courier", 12, "bold"))

    def checkentries(self, a, c, b):
        # turn all uppercase:
        for mapNo in range(len(self.mappings)):
            thisletter = self.mappings[mapNo].get()
            if thisletter.islower():
                self.mappings[mapNo].set(thisletter.upper())
            # get rid of non -letters
        for mapNo in range(len(self.mappings)):
            thisletter = self.mappings[mapNo].get()
            if not thisletter.isalpha() and thisletter != "":
                self.mappings[mapNo].set("")

        # cut down to one letter
        for mapNo in range(len(self.mappings)):
            thisletter = self.mappings[mapNo].get()
            if len(thisletter) > 1:
                self.mappings[mapNo].set(thisletter[0])
        # cut out repetitions
        newmappings = [mapping.get() for mapping in self.mappings]
        oldmappings = [mapping for mapping in self.oldMappings]
        for mapNo in range(len(self.mappings)):
            thisletter = self.mappings[mapNo].get()
            if newmappings.count(thisletter) > 1 and oldmappings[mapNo] != thisletter:
                self.mappings[mapNo].set("")

        self.oldMappings = [mapping.get() for mapping in self.mappings]
        self.rsubDecrypt()
        return True

    def letterEntered(self, event,last=None):
        # the top text box has been changed, so update the decrypted box
        self.ciphertextContents = self.entryBox.get(1.0, END)
        self.ciphertextContents = self.ciphertextContents.upper()
        self.ciphertextContents = self.ciphertextContents.replace("\n", "")
        if self.currentmode == "random":
            self.rsubDecrypt()
            self.showLetterFrequencies(self.rsubCanvas, self.ciphertextContents)
        elif self.currentmode == "caesar":
            self.spinchanged()
    

    def rsubDecrypt(self):
        plaintext = ""
        key = [None for x in range(26)]
        for letterNum in range(26):
            key[letterNum] = self.mappings[letterNum].get()
        plaintext = substitute(self.ciphertextContents, key)
        self.decryptedbox.delete(1.0, END)
        self.decryptedbox.insert(1.0, plaintext)


    def randomKey(self):
        self.clearKey()
        letters = [chr(x) for x in range(65, 91)]
        random.shuffle(letters)
        for x in range(26):
            self.mappings[x].set(letters[x])
        self.rsubDecrypt()

    def clearKey(self):
        # clear old mappings
        for x in range(26):
            self.mappings[x].set("")
        self.rsubDecrypt()

    def spinchanged(self):
        plaintext = shift(self.ciphertextContents,int(self.spinvalue.get()))
        #print(plaintext, self.ciphertextContents)
        self.decryptedbox.delete(1.0, END)
        self.decryptedbox.insert(1.0, plaintext)
        self.showLetterFrequencies(self.caesarCanvas, self.decryptedbox.get(1.0, END))

    def findBestShift(self):
        text=self.ciphertextContents
        #fitness = ngram_score('english_quadgrams.txt')  # load our quadgram statistics
        maxscore = CalcIC.getComparativeIC(text)
        self.shiftAnimation(1,text,maxscore, 0, text)
           

    def shiftAnimation(self,shiftNum, text, maxscore, bestkey, plaintext):
        # shift by amount
        candidate = shift(text, shiftNum)
        self.decryptedbox.delete(1.0, END)
        self.decryptedbox.insert(1.0, candidate)
        self.spinvalue.set(shiftNum)
        self.showLetterFrequencies(self.caesarCanvas, self.decryptedbox.get(1.0, END))
        # check score of text
        score = CalcIC.getComparativeIC(candidate)
        if score > maxscore:
            maxscore=score
            bestkey = shiftNum
            plaintext = candidate
        if shiftNum==26:
            self.decryptedbox.delete(1.0, END)
            self.decryptedbox.insert(1.0, plaintext)
            self.spinvalue.set(bestkey)
            self.showLetterFrequencies(self.caesarCanvas, self.decryptedbox.get(1.0, END))
        else:
            self.master.after(100, lambda s=shiftNum+1: self.shiftAnimation(s, text,maxscore, bestkey, plaintext))


    def vigAutoDecrypt(self):
        self.vigenereCanvas.delete(ALL)
        self.viganswers = autoVigenereDecrypt(self.entryBox.get(1.0,END))
        self.vigenereCanvas.create_text(10, 10, text="Click one of the options below",
                                        anchor="nw", fill="red", font=("Arial", 11))
        ypos = 40
        for candidate in self.viganswers:
            self.vigenereCanvas.create_text(10, ypos, text="Key Length "+ str(candidate[0]),
                                        anchor="nw", fill="blue", font=("Arial", 11))
            self.vigenereCanvas.create_text(10, ypos+20, text="Likely key word: "+ candidate[2],
                                        anchor="nw", fill="blue", font=("Arial", 11))
            self.vigenereCanvas.create_text(10, ypos+40, text="gives plaintext:",
                                        anchor="nw", fill="blue", font=("Arial", 11))
            self.vigenereCanvas.create_text(10, ypos+60, text=candidate[3],
                                        anchor="nw", fill="blue", font=("Arial", 11))
            ypos+=95

    def vigCanvasClicked(self,e):
        itemclicked = (e.y-40)//95
        if 0 <= itemclicked and self.viganswers:
            self.vigkey.delete(0, END)
            self.vigkey.insert(0, self.viganswers[itemclicked][2])
            self.vigkeychanged(None)




def bestShiftIC(text):
    maxscore = CalcIC.getComparativeIC(text)
    bestkey=0
    plaintext=text
    for shiftNum in range(26):
        candidate = shift(text, shiftNum)
        score = CalcIC.getComparativeIC(candidate)
        if score > maxscore:
            maxscore=score
            bestkey = shiftNum
            plaintext = candidate
    return bestkey, plaintext

def vigenereDecrypt(text, key):
    key = key.upper()
    text = text.upper()
    plaintext=""
    keypos = 0
    for pos in range(len(text)):
        cipherletterval = ord(text[pos])-65
        if 0 <= cipherletterval <= 25:
            plaintext += chr((cipherletterval - ord(key[keypos%len(key)])-65)%26+65)
            keypos+=1
        else:
            plaintext += text[pos]
    return plaintext

# def autoVigenereDecrypt(text):
#     strippedtext = "".join(c.upper() for c in text if c.isalpha())
#     print("Stripped:", strippedtext)
#     # find length
#     lengthscores = []
#     for length in range(25):
#         print("Length", length)
#         plaintextColumns = []
#         for column in range(length):
#             # find best shift
#             thiscolumn = "".join([strippedtext[i] for i in range(column,len(strippedtext),length)])
#             shift, plaintextColumn = bestShiftIC(thiscolumn)
#             plaintextColumns.append(plaintextColumn)
#         print(plaintextColumns)
#         plaintext = [val for tup in zip(*plaintextColumns) for val in tup]
#         print("".join(plaintext))

def autoVigenereDecrypt(text):
    strippedtext = "".join(c.upper() for c in text if c.isalpha())
    # find length
    answers = []
    for length in range(1,15):
        #print("Length", length)
        totalIC = 0
        plaintextColumns = []
        keycandidate=""
        for column in range(length):
            thiscolumn = "".join([strippedtext[i] for i in range(column,len(strippedtext),length)])
            totalIC += CalcIC.getIC(thiscolumn)
            shift, plaintextColumn = bestShiftIC(thiscolumn)
            keycandidate += chr((26-shift)%26+65)
            plaintextColumns.append(plaintextColumn)
        plaintext = "".join([val if val else "" for pair in itertools.zip_longest(*plaintextColumns) for val in pair])
        answers.append((length, totalIC/length, keycandidate, plaintext))
    answers.sort(reverse=True,key=lambda i:i[1])
    return answers

        
        


        
    


def autoDecryptRSubTask(PipeIn, ciphertextContents):
        fitness = ngram_score('english_quadgrams.txt')  # load our quadgram statistics
        maxkey = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        maxscore = -99e9
        parentscore, parentkey = maxscore, maxkey[:]
        i = 0
        while i < 1000:
            i = i + 1
            random.shuffle(parentkey)
            deciphered = substitute(ciphertextContents, parentkey)
            parentscore = fitness.score(deciphered)
            count = 0
            while count < 1000:
                a = random.randint(0, 25)
                b = random.randint(0, 25)
                child = parentkey[:]
                # swap two characters in the child
                child[a], child[b] = child[b], child[a]
                deciphered = substitute(ciphertextContents, child)
                score = fitness.score(deciphered)
                # if the child was better, replace the parent with it
                if score > parentscore:
                    parentscore = score
                    parentkey = child[:]
                    count = 0
                count = count + 1
            # keep track of best score seen so far
            if parentscore > maxscore:
                maxscore, maxkey = parentscore, parentkey[:]
                # print ('\nbest score so far:',maxscore,'on iteration',i)
                PipeIn.send((maxkey))
                # print ('    best key: '+''.join(maxkey))
                # print ('    plaintext: '+ss)



def substitute(ciphertext, key):
    plaintext = ""
    for letter in ciphertext:
        letterNum = ord(letter) - 65
        if letterNum == 32 - 65:
            plaintext += " "
        elif letterNum >= 0 and letterNum <= 25:
            if key[letterNum] == "":
                plaintext += "*"
            else:
                plaintext += key[letterNum]
    return plaintext

def shift(text, shiftnum):
    return "".join([chr(65+(ord(c)-65+shiftnum)%26) if c.isalpha() else c for c in text])

if __name__ == "__main__":
    mp.freeze_support()
    root = Tk()
    root.title("Triple Cipher Cracker")
    root.geometry("1550x850+100+100")
    root.resizable(width=False, height=False)
    app = App(root)
    root.mainloop()
    if app.runningSubDecrypt:
        app.p.terminate()
    print("Quit")

