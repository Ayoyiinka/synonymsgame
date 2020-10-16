from flask import Flask, request, session
import requests
from twilio.twiml.messaging_response import MessagingResponse
import pandas as pd
import random, os

app = Flask(__name__)

app.secret_key = os.environ['SECRET_KEY']
headers = {'x-rapidapi-host': os.environ['X-RAPIDAPI-HOST'], 'x-rapidapi-key': os.environ['X-RAPIDAPI-KEY']}

def get_word():
    rand = random.randint(4,10)
    url = "https://wordsapiv1.p.rapidapi.com/words/?letters=" + str(rand)
    res = requests.request("GET", url, headers=headers)
    results = res.json()['results']['data']
    words=[]
    for result in results:
        if result.isalpha():
            words.append(result)
    if len(words) > 0:
        return words[random.randint(0,len(words)-1)]
    return results[random.randint(0,len(results)-1)]

@app.route('/synonymsgame', methods=['POST'])
def bot():
    incoming_msg = request.values.get('Body', '').lower()
    resp = MessagingResponse()
    msg = resp.message()

    if session.get("Game Started?") != True or incoming_msg.strip().lower() == "new game":
        if incoming_msg.strip().lower() == "yes" or incoming_msg.strip().lower() == "new game":
            session["Game Started?"] = True
            session["num_corr_ques"] = 0
            random_word = get_word()
            session["random_word"] = random_word 
            msg.body("First word: " + random_word)
            return str(resp)
        else:
            msg.body("Start the game?(Yes/No)")
            return str(resp)
    else:
        in_ = incoming_msg.strip().lower()
        random_word = session["random_word"]
        url = "https://wordsapiv1.p.rapidapi.com/words/" + random_word + "/synonyms"
        response = requests.request("GET", url, headers=headers)
        json = response.json()
        synonyms = json['synonyms']
        if len(synonyms) <= 0:
            session.pop("random_word")
            session["random_word"] = get_word()
            msg.body("No synonyms for " + random_word + ", next word: " + session["random_word"])
            return str(resp)

        if in_ in synonyms:
            session["num_corr_ques"] += 1
            session.pop("random_word")
            random_word = get_word()
            session["random_word"] = random_word
            msg.body("Correct!, next word: " + random_word)

        else:
            session.pop("Game Started?")
            msg.body("Game over! " + "You got " + str(session["num_corr_ques"]) + " questions correctly" + \
                    "\n\nSynonyms for " + random_word + " are <" + ", ".join(synonyms) + ">" + \
                    "\n\nType <new game> to start a new game")

        return str(resp)

if __name__ == "__main__":
    app.run()
