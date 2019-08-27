# In order to segment the jumble.py code so that the server could effectively
# communicate to, and recieve information from, the client I had to turn jumble
# into an object. This was so the object could be instantianted from the server,
# thus making its methods accessible from the server. The object seperates the 
# jumble.py file into two methods. The first method produces a prompt and jumbled
# word that can be sent from the server to the client. The second method recieves
# a word and then checks whether it is the correct answer.

import random
F = open('wordlist.txt')            # opens file filled with list of words
words = F.readlines()               # reads the words in the file into 'words' variable
F.close()                           # closes the file
class jumble:
    def __init__(self):             # when the jumble object is initialized it sets
        self.old_word = ''          #   the old_word class variable as an empty string.
    
    def give_word(self):            # function to give the client a jumble problem
        jumbled_word = ''           # initializes the jumbled word as an empty string
        word = words[random.randrange(len(words))]          # sets the local variable word as a random word 
        while len(word) > 5 or len(word) == 0:              # this while loop ensures the randomness of the chosen word
            word = words[random.randrange(0, len(words))]   
        word = word.rstrip()                                # formats the chosen word
        self.old_word = word                                # saves it to the class variable old_word so it can be accessed by other methods
        word = list(word)                                   # converts the word to a list so it can be jumbled.
        while word:                                         # the while loop formats jumbles the words letters into 'jumbled_word' string 
            jumbled_word = jumbled_word + word.pop(random.randrange(len(word))) + ' '
        return jumbled_word

    def get_word(self, match_word):                         # function to check the correctness of the users answer
            new_word = match_word + '\n'                    # formats the users answer
            if new_word in words and set(match_word) == set(self.old_word): # checks formatted user answer against objects answer
                    ans = 'You win.'            # sets server response if client is right
            else:
                ans = 'The answer is ' + self.old_word  # sets server response if client is wrong
            return ans                          # returns server response
