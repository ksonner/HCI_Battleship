import pygame 
import sounddevice as sd 
from faster_whisper import WhisperModel
import numpy as np 
import socket # for peer-to-peer communication
from flask import Flask, render_template, request, jsonify 
import random
import string 

app = Flask(__name__)

games = {}

def create_room_code():
    return ''.join(
        random.choices(
            string.ascii_uppercase + string.digits, k=6
            )
        )

@app.route("/")
def home():
    return render_template('Battleship.html')

@app.route("/new_game", methods=["POST"])
def new_game():
    room_code = create_room_code()
    games[room_code] = {
        "players": [],
        "board": [],
        "turn": 1
    }
    return jsonify({"room_code": room_code})

@app.route("/join_game", methods=["POST"])
def join_game():
    
    data = request.json
    room_code = data["room_code"]
    
    if room_code not in games:
        return jsonify({"success": False, "message": "Game not found"})

    return jsonify({
        "success": True,
        "message": "Joined game successfully"
    })
    
if __name__ == "__main__":
    app.run(debug=True)

