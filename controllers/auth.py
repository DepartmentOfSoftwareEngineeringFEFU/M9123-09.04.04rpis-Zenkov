from app import app
from flask import render_template, request, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models.auth_model import *
from utils import get_db_connection
from flask_login import login_user, logout_user, current_user
import secrets
import random

PASS_LEN_MAX = 8
PASS_LEN_MIN = 12

@app.route('/register_post', methods=['post'])
def register_post():
    conn = get_db_connection()

    user_login = request.form.get('user_login')
    user_name = request.form.get('user_name')
    user_is_editor = request.form.get('user_is_editor')
    user_password_unsafe = secrets.token_urlsafe(int(random.random() * (PASS_LEN_MAX - PASS_LEN_MIN) + PASS_LEN_MIN))
    if user_login is None or user_login == "":
        flash('Логин не может быть пустым', 'error')
        return redirect(url_for('control_panel'))
    if user_name is None or user_name == "":
        flash('ФИО не может быть пустым', 'error')
        return redirect(url_for('control_panel'))

    user = get_user(conn, user_login)
    if user:
        flash('Пользователь с таким логином уже существует', 'error')
        return redirect(url_for('control_panel'))

    user_password = generate_password_hash(user_password_unsafe, method='sha256')

    add_user(conn, user_login, user_name, user_password, user_is_editor)

    flash('Пользователь успешно добавлен.', 'success')
    flash('Пароль: ' + user_password_unsafe, 'warning')
    flash('Вам будет необходимо сообщить пароль пользователю.', 'warning')
    return redirect(url_for('control_panel'))


@app.route('/login', methods=['get'])
def login():
    if not current_user.is_authenticated:
        return render_template('login.html', user=current_user, len=len, str=str)
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    logout_user()
    session['org_id'] = None
    session['role_id'] = None
    session['role_type'] = None
    session['student_id'] = None
    return redirect(url_for('index'))


@app.route('/login_post', methods=['post'])
def login_post():
    conn = get_db_connection()

    user_login = request.form.get('login')
    user_password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = get_user(conn, user_login)
    if not user or not check_password_hash(user.password, user_password):
        flash('Введён неверный логин или пароль', 'error')
        return redirect(url_for('login'))

    login_user(user, remember=remember)
    session['student_id'] = ''
    return redirect(url_for('index'))

