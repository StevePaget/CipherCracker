# CipherCracker.py


This program holds a series of tools to aid with decryption of text using some simple ciphers.
At present, the following ciphers are implemented:

## Caesar Cipher

The program lets you choose a shift value and moves each letter by that amount.
 
 An autodecrypt function tries every possible shift and displays the most likely plaintext.

 (The algorithm uses an Index of Coincidence to find the most likely key)


 ## Random Substitution

 Each letter will be swapped for a different one, based on a table of swaps.
 eg. Every letter E will be swapped for a P

 The program will let you enter your own swap table, or choose a random one

 It also performs frequency analysis to assist in manual decryption.
 
 See https://www.youtube.com/watch?v=LhS8N6oJdno&t=2s for details.

 An autodecrypt function searches for the most likely table of substitutions.

 (The algorithm uses a hill-climbing algorithm using quadgrams.
 See http://practicalcryptography.com/cryptanalysis/text-characterisation/quadgrams/
 )

 ## Vigenere Cipher
 
 A keyword is used, and each letter of the ciphertext is shifted by an amount determined by a differen tletter of the keyword.

 The program lets you enter a keyword, and performs the decryption.

 An autodecrypt function first finds the most likely key lengths, then for each key length it searches for  keywords (or strings) that result in likely plaintext.

 (The algorithm uses Index of Coincidence as explained here: http://www.practicalcryptography.com/cryptanalysis/stochastic-searching/cryptanalysis-vigenere-cipher/ )


 # To-do
 At the moment, the tool is focused on decryption, rather than encyption. Making sample texts to play with is a bit of a fudge, and is especially tricky for Vigenere.

 I plan to add a switch from decrypt to encrypt, as well as include some sample texts.
