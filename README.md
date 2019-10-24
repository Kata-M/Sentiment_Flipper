# Sentiment_Flipper
Turning hate speech into love; a NLP project which turns negative sentences into positive ones by utilising a rule based system. This system looks into negative adjectives, their antonyms, negations, and swearwords. The program uses NLP concepts like tokenisation, part-of-speech tagging, sentiment analysis, text generation, and bigram probabilities. 


## To run the code

Install spacy:
https://spacy.io/usage?fbclid=IwAR2iyBKr4Nr_yvYf-2-2RMq9N9jsdNWo8b8zYyy5hIUZmKuSOclX8LRdwsY

Download English language module for spacy: 
python -m spacy download en

Install nltk:
pip3 install nltk

Install mysql:
pip3 install mysql-connector-python

Write:
*python3 sentiment_flipper.py* in the terminal in correct project directory


## Understanding the code

1. The program reads the sentences from the *input.txt* file
2. Each sentence is run through Google Perspective API and a toxicity score is assigned for it. Results are printed to *before.txt*
3. Tokenize the input which is read from *input.txt*
4. PoS tag the text (Using spacy’s automatic PoS tagging) 
5. Loop through the tokens and identify the adjectives
6. Check if the adjective is negative (compare to our dataset of negative adjectives), if yes, find an antonym and replace the adjective with its antonym
7. In this step many different antonyms were found by wordnet. The best fitting antonym from the list of antonyms was chosen with the help of bigram frequencies from a database provided by the University of Twente. The most frequently appearing adjective together with the subsequent word was always chosen. 
8. If antonym is not found, leave the word as it is and move on
9. Check if the token == “not”, if yes, remove the word (removes negations)
10. Check if the token is a swear word, if yes, remove the word
11. Put tokens back to text strings
12. Print the strings to output.txt file
13. Run the output.txt file through Google Perspective: get the toxicity score for each sentence and write the output sentences together with their toxicity scores to a new text file “after.txt” 
14. Count the average toxicity before and after the sentiment flipper and print them out. The results are written to files "before.txt" and "after.txt" together with the modified sentences. 




