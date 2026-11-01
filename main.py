# import pygame 
# import sounddevice as sd 
# from faster_whisper import WhisperModel
# import numpy as np 
import socket # for peer-to-peer communication
from flask import Flask, render_template, request, jsonify 
import random
import string 

# creating the flask app
app = Flask(__name__)

# dictionary to store all active game rooms
games = {}

# creates a random 6-char room code 
def create_room_code():
    return ''.join(
        random.choices(
            string.ascii_uppercase + string.digits, k=6
            )
        )

# -----------
# page routes 
# -----------

# home screen route
@app.route("/")
def home():
    return render_template('home_screen.html')

 
# join game page route
# displays the page where a player can enter a room
@app.route("/join")
def join_page():
    return render_template('join_game.html')

# create game page route
# displays the page that generates and show a room code 
@app.route("/start")
def start_game():
    return render_template('create_game.html')

@app.route("/battleship")
def battleship():
    return render_template('battleship.html')

# ----------
# API routes
# ----------

# creates a new game room
@app.route("/new_game", methods=["POST"])
def new_game():
    # creates a unique room code
    room_code = create_room_code()
    
    # create a new game entry
    games[room_code] = {
        "players": [],
        "board": [],
        "turn": 1
    }
    return jsonify({"room_code": room_code})

# allows a player to join an existing game room
@app.route("/join_game", methods=["POST"])
def join_game():
    
    # get JSON data sent from join_game.html
    data = request.json
    
    # extract room code entered by player 
    room_code = data["room_code"]
    
    # check if room exists
    if room_code not in games:
        return jsonify({
            "success": False, 
            "message": "Game not found"})
        
    # prevent more than 2 players in a room
    if len(games[room_code]["players"]) >= 2:
        return jsonify({
            "success": False,
            "message": "Game is full"
        })    
        
    games[room_code]["players"].append("guest")    

    # if room exists allow player to join 
    return jsonify({
        "success": True,
        "message": "Joined game successfully"
    })
    
@app.route("/game_status/<room_code")
def game_status(room_code):
    if room_code not in games:
        return jsonify({"ready": False})
    
    player_count = len(games[room_code]["players"])
    
    return jsonify({
        "ready": player_count >= 2,
        "players": player_count
    })    
    
# ---------------    
# start flask app
# ---------------

# 0.0.0.0 allows other devices on the same network to access the app     
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)

