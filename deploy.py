import os
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ForceReply, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import logging
import string
import random
import ujson
from emoji import emojize
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from dotenv import load_dotenv

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
MODE = os.getenv("MODE")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

active_games = {}
user_game = {}
bot = telegram.Bot(BOT_TOKEN)

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

class User:
    def __init__(self, userObj, chatObj, gameid):
        self.userObj = userObj
        self.fname = userObj.first_name
        self.name = userObj.full_name
        self.chatid = chatObj.id
        self.id = userObj.id
        self.username = userObj.username
        self.gameid = gameid
        self.cards = []
        self.team = 0

class Game:
    def __init__(self, gameid):
        self.userlist = []
        self.gameid = gameid
        self.numPlayers = 0
        self.gameNo = 1
        self.roundNo = 0
        self.gameScores = {'1': 0, '2': 0}
        self.scores = {'1':0, '2':0}
        self.teams = {'1': None, '2': None}
        self.state = 'SETUP'
        self.playerIdx = -1
        self.availableCards = DECK
        self.trump = None
        self.lastRoundWinner = None
        self.currPlayer = None
        self.roundParams = {'First Player': None, 'Suit': None, 'Highest Card': None, 'Highest Player': None, 'Turn Count': 0, 'Current Player': None, 'Messages': None} 
        self.lastWinner = None

    def addUser(self, user):
        self.userlist.append(user)
        if(self.numPlayers == 0):
            self.host = user
            self.currPlayer = self.host
        self.numPlayers += 1

    def getUserList(self):
        msg = ''
        for x in self.userlist:
            msg += x.name + '\n'
        return msg

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
    print(update.message.from_user.name + ' started a new game.')
    if(len(active_games) > 2):
        update.message.reply_text('Server limit reached. Try again later.')
    else:
        gameid = ''.join(random.choices(string.ascii_uppercase, k=5))
        active_games[gameid] = Game(gameid)
        newuser = User(update.message.from_user, update.effective_chat, gameid)
        active_games[gameid].addUser(newuser)
        user_game[update.message.from_user.id] = gameid
        update.message.reply_text('New game created. Ask your friend to join using \"/join ' + gameid + '\"', reply_markup=ReplyKeyboardRemove())

def joingame(update, context):
    if((update.message.from_user.id in user_game) and (update.message.from_user.id != ADMIN_ID)):
        update.message.reply_text('Could not join. Already in a game.')
    else:
        gameid = "".join(context.args)
        if(gameid in active_games):
            if(active_games[gameid].numPlayers < 2):
                newuser = User(update.message.from_user, update.effective_chat, gameid)
                update.message.reply_text('Joined game successfully. Players in room: \n' + active_games[gameid].getUserList(), reply_markup=ReplyKeyboardRemove())
                for x in active_games[gameid].userlist:
                    update.message.bot.send_message(x.chatid, update.message.from_user.name + ' has joined the game')
                active_games[gameid].addUser(newuser)
                user_game[update.message.from_user.id] = gameid
            else:
                update.message.reply_text('Could not join game. Room is full.')
        else:
            update.message.reply_text('Game does not exist. You can create a game using /newgame.')

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('newgame', newgame))
    updater.dispatcher.add_handler(CommandHandler('join', joingame))
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
