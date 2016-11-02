from app import app
from .mwtools import *
import telebot
from flask import request

bot_api_key = app.config["TELEGRAM_API_KEY"]

@app.route("/" + bot_api_key, methods=["POST"])
def index():
    telegram_inb = request.get_json()
