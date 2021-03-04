import os
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ForceReply, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import logging
import string
import random
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from dotenv import load_dotenv
import json
from random import randint, choice
import os, sys

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
MODE = os.getenv("MODE")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

active_games = {}
user_game = {}
bot = telegram.Bot(BOT_TOKEN)

dictionary = {}

proper_dictionary = {}

if (MODE == "dev"):
    def run(updater):
        updater.start_polling()
        updater.idle()
elif (MODE == "deploy"):
    def run(updater):
        PORT = int(os.getenv("PORT", "8443"))
        updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=BOT_TOKEN)
        updater.bot.set_webhook("https://court-piece-bot.herokuapp.com/" + BOT_TOKEN)
        updater.idle()
else:
    logger.error("No mode specified")
    sys.exit(1)

def check(word, guess):
    word = word.upper().strip()
    guess = guess.upper().strip()
    word = list(word)
    guess = list(guess)
    bulls = 0
    cows = 0
    index = 0
    while index<len(word):
        if word[index]==guess[index]:
            bulls+=1
            del word[index]
            del guess[index]
        else:
            index+=1
    index = 0
    while index<len(word):
        index2 = 0
        found = False
        while index2<len(guess):
            if word[index]==guess[index2]:
                cows+=1
                del word[index]
                del guess[index2]
                found = True
                break
            else:
                index2+=1
        if not found:
            index+=1
    return [bulls, cows]

def get_random_word():
    alpha = chr(ord('A') + randint(0, 25))
    word = choice(proper_dictionary[alpha])
    return word

def get_dictionary():
    dictionary_path = 'words.json'
    if getattr(sys, 'frozen', False):
        dictionary_path = os.path.join(sys._MEIPASS, 'words.json')
    global dictionary
    with open(dictionary_path) as f:
        dictionary = json.loads(f.read())

def get_proper_dictionary():
    dictionary_path = 'properwords.json'
    if getattr(sys, 'frozen', False):
        dictionary_path = os.path.join(sys._MEIPASS, 'properwords.json')
    global proper_dictionary
    with open(dictionary_path) as f:
        proper_dictionary = json.loads(f.read())

class User:
    def __init__(self, userObj, chatObj, gameid):
        self.userObj = userObj
        self.fname = userObj.first_name
        self.name = userObj.full_name
        self.chatid = chatObj.id
        self.id = userObj.id
        self.username = userObj.username
        self.gameid = gameid
        self.in_game = False
        self.attempts = 0
        self.word = ''
    
    def get_gameinfo(self, update, context):
        update.message.reply_text(f'Current Attempts: {self.attempts}', quote=True)

    def endgame(self, update, context):
        update.message.reply_text(f'You ended the game with {self.attempts} attempts!', quote=True)
        update.message.reply_text(f'Word: {self.word}')
        self.in_game = False
        self.attempts = 0
        self.word = ''

    def start_game(self):
        self.in_game = True
        self.word = get_random_word()
        print('Random Word:', self.word)
        bot.send_message(self.id, 'Guess Word')

    def respond(self, update, context):
        if self.in_game:
            guess = update.message.text.strip().upper()
            if len(guess)!=4 or guess not in dictionary[guess[0]]:
                print(f'{update.message.from_user.name} guessed {guess} | INVALID')
                update.message.reply_text('Invalid Guess. Try Again.', quote=True)
            else:
                bulls, cows = check(self.word, guess)
                self.attempts+=1
                if bulls==4:
                    print(f'{update.message.from_user.name} guessed {guess} in {self.attempts} attempts!')
                    update.message.reply_text(f'You guessed the word in {self.attempts} attempts!', quote=True)
                    self.in_game = False
                    self.attempts = 0
                    self.word = ''
                else:
                    # update.message.reply_text(f'{bulls} Bulls and {cows} Cows')
                    print(f'{update.message.from_user.name} guessed {guess} | {bulls} Bulls and {cows} Cows')
                    update.message.reply_text(f'{bulls} Bulls and {cows} Cows', quote=True)
        else:
            update.message.reply_text('Invalid command. You\'re not in a game.')


def reset(update, context):
    if(update.message.from_user.id == ADMIN_ID):
        active_games.clear()
        user_game.clear()
        update.message.reply_text('Game list cleared.')
    else:
        update.message.reply_text('Unauthorized.')

def about(update, context):
    update.message.reply_text('Court Piece Bot made by Yashvardhan Jain.\nContact @IamYVJ for reporting bugs, feedback and suggestions.')

def helper(update, context):
    update.message.reply_text("Use /newgame to create a game.\nUse /join <gameid> to join a game.\nUse /gameinfo to get details of current game. \nUse /endgame to end current game\nUse /about to get info about bot.")

def start(update, context):
    update.message.reply_text("Welcome to Bulls and Cows. Use /help to get a list of available commands.")

def newgame(update, context):
    if(update.message.from_user.id not in user_game) or user_game[update.message.from_user.id].in_game==False:
        print(update.message.from_user.name + ' started a new game.')
        if(len(active_games) > 2):
            update.message.reply_text('Server limit reached. Try again later.')
        else:
            gameid = ''.join(random.choices(string.ascii_uppercase, k=5))
            newuser = User(update.message.from_user, update.effective_chat, gameid)
            user_game[update.message.from_user.id] = newuser
            newuser.start_game()
    else:
        update.message.reply_text('You\'re already in a game.', quote=True)

def respond(update, context):
    if(update.message.from_user.id in user_game):
        user = user_game[update.message.from_user.id]
        user.respond(update, context)
    else:
        update.message.reply_text('Invalid option. Please create or join a game. Use /help to see a list of commands.', quote=True)

def gameinfo(update, context):
    if(update.message.from_user.id in user_game) and (user_game[update.message.from_user.id].in_game==True):
        user = user_game[update.message.from_user.id]
        user.get_gameinfo(update, context)
    else:
        update.message.reply_text('No active game.', quote=True)

def endgame(update, context):
    if(update.message.from_user.id in user_game) and (user_game[update.message.from_user.id].in_game==True):
        user = user_game[update.message.from_user.id]
        user.endgame(update, context)
    else:
        update.message.reply_text('No active game.', quote=True)

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    get_dictionary()
    get_proper_dictionary()
    updater = Updater(BOT_TOKEN, use_context=True)
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('newgame', newgame))
    updater.dispatcher.add_handler(CommandHandler('help', helper))
    updater.dispatcher.add_handler(CommandHandler('reset', reset))
    updater.dispatcher.add_handler(CommandHandler('gameinfo', gameinfo))
    updater.dispatcher.add_handler(CommandHandler('endgame', endgame))
    updater.dispatcher.add_handler(CommandHandler('about', about))
    updater.dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), respond))
    updater.dispatcher.add_error_handler(error)

    run(updater)

if __name__ == '__main__':
    main()
