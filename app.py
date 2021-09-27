from typing import final
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
from flask import Flask , render_template , request
from heapq import nlargest

app= Flask(__name__)

# Summarization
punctuation+="/n"

stopwords= STOP_WORDS
nlp = spacy.load('en_core_web_sm')

def text_cleaning(doc):
    clean_doc=""
    for word in doc:
        if word.text.lower() not in stopwords:
            if word.text.lower() not in punctuation:
                clean_doc += word.text.lower() + " "
    return clean_doc


def summary(doc):
    # word frequencies
    word_frequencies={}
    for word in doc:
        if word.text.lower() not in stopwords:
            if word.text.lower() not in punctuation:
                if word.text.lower() not in word_frequencies.keys():
                    word_frequencies[word.text.lower()]=1
                else:
                    word_frequencies[word.text.lower()] +=1
    
    # total frequencies
    total=0
    for word in word_frequencies.keys():
        total+= word_frequencies[word]

    total_freq={}
    for word in word_frequencies.keys():
        total_freq[word] = word_frequencies[word]/total
    

    # sentence_scores
    sentence_scores={}
    sentence_tokens = [sent for sent in doc.sents]
    for sent in sentence_tokens:
        for word in sent:
            if word.text.lower() in total_freq.keys():
                if sent not in sentence_scores.keys():
                    sentence_scores[sent]= total_freq[word.text.lower()]
                else:
                    sentence_scores[sent]+= total_freq[word.text.lower()]

    # extractinc summary
    select_length = int(len(sentence_tokens)*0.5)
    summary = nlargest(select_length,sentence_scores,key=sentence_scores.get)

    final_summary= ""
    for sent in sentence_tokens:
        if sent in summary:
            final_summary +=" "+ str(sent) 
    
    return final_summary
@app.route("/",methods=["GET","POST"])
def index():
    final_text=""
    if request.method=="POST":
        text= request.form.get("text")
        doc= nlp(text)
        tokens= [token for token in doc]
        final_text=summary(doc)
        
        
    # return render_template("index.html")
    return render_template("index.html",final_text=final_text)

if __name__ == "__main__":
    app.run(debug=True)