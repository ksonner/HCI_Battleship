import pygame 
import sounddevice as sd 
from faster_whisper import WhisperModel
import numpy as np 
import socket # for peer-to-peer communication
from flask import Flask, render_template 

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('battleship.html')

if __name__ == "__main__":
    app.run(debug=True)

