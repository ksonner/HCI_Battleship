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

@app.route("/game_play")
def game_play():
    return render_template("game_play.html")

@app.route("/waiting")
def waiting():
    return render_template("waiting.html")

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
        "players": ["host"],
        
        # ship location
        "host_ships": [],
        "guest_ships": [],
        
        # are both players ready
        "host_ready": False,
        "guest_ready": False,
        
        # shots fired
        "host_shots": [],
        "guest_shots": [],
        
        # game state
        "winner": None,
        "game_over": False,
        
        "turn": "host"
    }
    return jsonify({"room_code": room_code, "role": "host"})

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
    
@app.route("/save_ships", methods=["POST"])
def save_ships():
    
    data = request.json
    
    room_code = data["room_code"]    
    player = data["player"]
    ships = data["ships"]
    
    if room_code not in games:
        return jsonify({
            "success": False,
            "message": "Game not found"
        })
        
    if player == "host":
        games[room_code]["host_ships"] = ships
        
    elif player == "guest":
        games[room_code]["guest_ships"] = ships
        
    return jsonify({
        "success": True,
        "message": "Ships saved successfully"
    })
    
@app.route("/get_ships/<room_code>/<player>") 
def get_ships(room_code, player):
    if room_code not in games:
        return jsonify({"success": False})
    if player == "host":
        return jsonify({
            "success": True,
            "your_ships": games[room_code]["host_ships"],
            "opponent_ships": games[room_code]["guest_ships"]
        })   
    else:
        return jsonify({
            "success": True,
            "your_ships": games[room_code]["guest_ships"],
            "opponent_ships": games[room_code]["host_ships"]
        })    
    
@app.route("/game_status/<room_code>")
def game_status(room_code):
    if room_code not in games:
        return jsonify({"ready": False})
    
    player_count = len(games[room_code]["players"])
    
    return jsonify({
        "ready": player_count >= 2,
        "players": player_count
    })    
    
@app.route("/player_ready", methods=["POST"])
def player_Ready():
    data = request.json
    room_code = data["room_code"]
    player = data["player"]
    
    print("READY BUTTON PRESSED")
    print("player:", player)
    print("Room:", room_code)
    
    if player == "host":
        games[room_code]["host_ready"] = True
    else:
        games[room_code]["guest_ready"] = True
    return jsonify({"success": True})

@app.route("/ready_status/<room_code>")
def ready_status(room_code):
    if room_code not in games:
        return jsonify({"ready": False})
    
    game = games[room_code]
    
    return jsonify ({
        "ready":(
            game["host_ready"] and
            game["guest_ready"]
        ),
        "host_ready": game["host_ready"],
        "guest_ready": game["guest_ready"]
    })
    
def all_ships_sunk(ships, shots):
    letters = "ABCDEFGHIJ"
    
    for ship in ships:
        start = ship["startCell"]
        length = int(ship['length']) 
        direction = ship["direction"]
        
        col = letters.index(start[0])       
        row = int(start[1:])
        
        for i in range(length):
            if direction == "horizontal":
                cell = letters[col + i] + str(row)
            else:
                cell = letters[col] + str(row + i)
            if cell not in shots:
                return False    
    return True        
           
    
# fire shot route    
@app.route("/fire_shot", methods=["POST"])
def fire_shot():
    
    data = request.json
    
    room_code = data["room_code"]
    player = data["player"]
    target = data["target"]
    
    game = games[room_code]
    
    if game["turn"] != player:
        return jsonify({
            "success": False,
            "message": "Not your turn"
        })
    
    target = target.replace("opponent-", "")
    
    if player == "host":
        game["host_shots"].append(target)
    else:
        game["guest_shots"].append(target)
    
    hit = False
    
    if player == "host":
        enemy_ships = game["guest_ships"]
    else:
        enemy_ships = game["host_ships"]
         
    for ship in enemy_ships:
        start = ship["startCell"]
        length = int(ship["length"])
        direction = ship["direction"]
        
        letters = "ABCDEFGHIJ"
        
        col = letters.index(start[0])       
        row = int(start[1:])
        
        for i in range(length):
            if direction == "horizontal":
                current = letters[col + i] + str(row)
            else:
                current = letters[col] + str(row + i)
                
            if current == target:
                hit = True
                break
        if hit: 
            break
        
        # only switch turns on a miss 
    if not hit:
        if player == "host":
            game["turn"] = "guest"
        else:
            game["turn"] = "host"
     
    # check if victory after a successfull hit        
    if player == "host":
        
        # host shoots guest ships
        if all_ships_sunk(
            game["guest_ships"],
            game["host_shots"]
        ):
            game["game_over"] = True
            game["winner"] = "host"
    else:
        
        # guest shoots host ships 
        if all_ships_sunk(
            game["host_ships"],
            game["guest_shots"]
        ):
            game["game_over"] = True
            game["winner"] = "guest"                
                
    return jsonify({
        "success": True,
        "hit": hit,
        "target": target,
        "next_turn": game["turn"],
        "game_over": game["game_over"],
        "winner": game["winner"]
    })                    
    
@app.route("/turn_status/<room_code>")   
def turn_status(room_code):
    if room_code not in games:
        return jsonify({"success": False})
    
    return jsonify({
        "success": True,
        "turn": games[room_code]["turn"]
    }) 
    
@app.route("/winner_status/<room_code>")
def winner_status(room_code):
    if room_code not in games:
        return jsonify({
            "success": False
        })    
    game = games[room_code] 
    
    return jsonify({
        "success": True,
        "game_over": game["game_over"],
        "winner": game["winner"]
    })   
    
# retrieve opponents shots 
@app.route("/get_shots/<room_code>/<player>")
def get_shots(room_code, player):
    if room_code not in games:
        return jsonify({"success": False})
    game = games[room_code]
    
    if player == "host":
        shots_against_me = game["guest_shots"]
    else:
        shots_against_me = game["host_shots"]
        
    return jsonify({
        "success": True,
        "shots": shots_against_me
    })    
        
                 


# ---------------    
# start flask app
# ---------------

# 0.0.0.0 allows other devices on the same network to access the app     
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)

