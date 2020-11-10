from flask import Flask, session, request
import requests
from twilio.twiml.messaging_response import MessagingResponse
import random, os

app = Flask(__name__)

app.secret_key = os.environ['SECRET_KEY']
headers = {'x-rapidapi-host': os.environ['X-RAPIDAPI-HOST'], 'x-rapidapi-key': os.environ['X-RAPIDAPI-KEY']}

def get_word():
    url = "https://wordsapiv1.p.rapidapi.com/words/?hasDetails=synonyms"
    page = str(random.randint(1,200))
    querystring = {"page":page}
    res = requests.request("GET", url, headers=headers, params=querystring)
    results = res.json()['results']['data']
    random_word = results[random.randint(1, len(results))]
    url_ = "https://wordsapiv1.p.rapidapi.com/words/" + random_word + "/synonyms"
    response = requests.request("GET", url_, headers=headers)
    json = response.json()
    synonyms = json['synonyms']
    return random_word, synonyms

@app.route('/synonymsgame', methods=['POST'])
def bot():
    incoming_msg = request.values.get('Body', '').lower()
    resp = MessagingResponse()
    msg = resp.message()

    if session.get("Game Started?") != True or incoming_msg.strip().lower() == "new game":
        if incoming_msg.strip().lower() == "yes" or incoming_msg.strip().lower() == "new game":
            session["Game Started?"] = True
            session["num_corr_ques"] = 0
            random_word, synonyms = get_word()
            session["random_word"] = random_word
            session["synonyms"] = synonyms
            msg.body("First word: " + random_word)
            return str(resp)
        else:
            msg.body("Start the game?(Yes/No)")
            return str(resp)
    else:
        in_ = incoming_msg.strip().lower()
        random_word = session["random_word"]
        synonyms = session["synonyms"]

        if in_ in synonyms:
            session["num_corr_ques"] += 1
            session.pop("random_word")
            session.pop("synonyms")
            random_word, synonyms = get_word()
            session["random_word"] = random_word
            session["synonyms"] = synonyms
            msg.body("Correct!, next word: " + random_word)

        else:
            session.pop("Game Started?")
            session.pop("random_word")
            session.pop("synonyms")
            msg.body("Game over! " + "You got " + str(session["num_corr_ques"]) + " questions correctly" + \
                    "\n\nSynonyms for " + random_word + " are <" + ", ".join(synonyms) + ">" + \
                    "\n\nType <new game> to start a new game")

        return str(resp)

if __name__ == "__main__":
    app.run()