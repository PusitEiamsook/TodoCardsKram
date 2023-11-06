# This is the script app.py, which is the entry point for the flask app
# This file contains the logic for routes, sessions, handling requests
# This file does not contain the logic for handling database queries & business logic
# Author: Panisara S 6422781326, Nachat K 6422770774

from flask import Flask, request, jsonify, session
from flask_cors import CORS
import mysql.connector

import cards, user, decks

# connects to mysql
# sets this up as a global variable
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="TodoCards"
)

# sets up some flask stuff (oh, and CORS too)
app = Flask(__name__)
app.secret_key = "some really useless key lol"
CORS(app, origins=["http://localhost:5173", "http://127.0.0.1:5173"], supports_credentials=True)
app.config['SESSION_COOKIE_SAMESITE'] = "None"
app.config['SESSION_COOKIE_SECURE'] = True

# a preliminary check for login status, only excluded for non-priviledged requests
@app.before_request
def check_login():
    # only apply to previledged requests
    if request.endpoint not in ['login', 'logout', 'ping', 'signup']:
        # simply check for username status (if it's set)
        if "username" not in session:
            return jsonify("not logged in")

# a debugging route that responds with "pong"
@app.route("/ping")
def ping():
    response = jsonify({"message": "pong"})
    return response

# authenticates a user and sets a session variable "userid"
@app.route("/login", methods=["POST"])
def login():
    jsonbody = request.get_json()
    username = jsonbody.get("username")
    password = jsonbody.get("password")

    # login function returns either true or false
    status = user.login(mydb, username, password)
    if status: 
        session["username"] = username
    elif "username" in session:
        session.pop("username")

    return jsonify(status)

# removes login info from session cookie
@app.route("/logout", methods=["POST"])
def logout():
    if "username" in session:
        session.pop('username', default=None)
    return ""

@app.route("/signup", methods=["POST"])
def signup():
    jsonbody = request.get_json()
    username = jsonbody.get("username")
    password = jsonbody.get("password")

    status = user.signup(mydb, username, password)
    if status: 
        session["username"] = username
    elif "username" in session:
        session.pop("username")

    return jsonify(status)

# retrieve a list of decks
@app.route("/get-decks-list", methods=["GET"])
def get_decks_list():
    username = session.get("username")
    result = decks.get_decks_list(mydb, username)
    return jsonify(result)


# retrieve a list of cards using deckId. 
@app.route("/get-cards-list", methods=["GET"])
def get_cards_list():
    deck_id = request.args.get("deckId")
    username = session.get("username")
    result = cards.get_cards_list(mydb, deck_id, username)
    return jsonify(result)

# retrieve a list of subcards using cardId. 
@app.route("/get-subcards-list", methods=["GET"])
def get_subcards_list():
    card_id = request.args.get("deckId")
    username = session.get("username")
    result = cards.get_subcards_list(mydb, card_id, username)
    return jsonify(result)

@app.route("/finish-card", methods=["POST"])
def finish_card():
    jsonbody = request.get_json()
    card_id = jsonbody.get("cardId")
    username = session.get("username")
    result = cards.finish_card(mydb, card_id, username)
    return jsonify(result)

@app.route("/finish-subcard", methods=["POST"])
def finish_subcard():
    jsonbody = request.get_json()
    subcard_id = jsonbody.get("subcardId")
    username = session.get("username")
    result = cards.finish_subcard(mydb, subcard_id, username)
    return jsonify(result)

@app.route("/edit-deck", methods=["POST"])
def edit_deck():
    jsonbody = request.get_json()
    deck_info = jsonbody.get("deckInfo")
    username = session.get("username")
    status = decks.edit_deck(mydb, deck_info, username)
    return jsonify(status)

@app.route("/edit-card", methods=["POST"])
def edit_card():
    jsonbody = request.get_json()
    card_info = jsonbody.get("cardInfo")
    username = session.get("username")
    status = cards.edit_card(mydb, card_info, username)
    return jsonify(status)

@app.route("/edit-subcard", methods=["POST"])
def edit_subcard():
    jsonbody = request.get_json()
    subcard_info = jsonbody.get("subcardInfo")
    username = session.get("username")
    status = cards.edit_subcard(mydb, subcard_info, username)
    return jsonify(status)

@app.route("/get-sharecode", methods=["GET"])
def get_sharecode():
    deck_id = request.args.get("deckId")
    username = session.get("username")
    result = decks.get_sharecode(mydb, deck_id, username)
    return jsonify(result)

# Handles sharing
@app.route("/recieve-sharecode", methods=["GET"])
def recieve_sharecode():
    sharecode = request.args.get("sharecode")
    username = session.get("username")
    result = decks.recieve_sharecode(mydb, sharecode, username)
    return jsonify(result)

# the entry point of the code
if __name__ == "__main__":
    # runs app, default to 127.0.0.1 port 5000
    app.run(debug=True)