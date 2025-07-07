# импорт объекта для создания приложения 
from flask import Flask, session
import sys
import os
from flask_login import LoginManager
from models.auth_model import get_user_by_id
from utils import get_db_connection


app = Flask(__name__)

app.secret_key = 'td@sj%$#FDk4w7e38orG#4^%E$W#Q@'
app.path = os.path.dirname(__file__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
ALLOWED_EXTENSIONS = {'jpg', 'png', 'jpeg', 'mp4', 'webm', 'vtt'}
ALLOWED_AUDIO_EXTENSIONS = {'wav', 'mp3', 'ogg', 'mov', 'webm'}
VTT_PATTERN = r'<(?!/?(?:b|u|i|c|ruby|rt|v|lang)\b)[^>]*>'
app.config['UPLOAD_FOLDER'] = os.path.join(app.path, 'static')
app.config['MAX_CONTENT_LENGTH'] = 100 * 1000 * 1000  # 100 Mb

# TEMPORARY CONST FOR NEW DB COMPATIBILITY
# WHILE GUIDEBOOK ADDING FUNCTIONALITY HASN'T BEEN ADDED YET
DEFAULT_BOOK_ID = 1

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

path = os.path.join(app.path, 'templates')
if not os.path.exists(path):
    os.mkdir(path)
path = os.path.join(app.path, 'static')
if not os.path.exists(path):
    os.mkdir(path)


@login_manager.user_loader
def load_user(user_id):
    return get_user_by_id(get_db_connection(), user_id)

import controllers.index
import controllers.constructor
import controllers.edit_entry
import controllers.auth
import controllers.control_panel
import controllers.user_account
import controllers.save_answer
import controllers.receive
import controllers.moderation
import controllers.dictionary
import controllers.edit_dictionary
import controllers.edit_word
import controllers.chat
