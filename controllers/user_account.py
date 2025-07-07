from app import app
from flask import render_template, request, session, redirect, url_for, flash
from models.user_account_model import *
from utils import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user


@app.route('/user_account', methods=['get', 'post'])
def user_account():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))

    conn = get_db_connection()

    # "Change password" button pressed
    if request.form.get('change'):
        user_id = request.form.get("user_id")
        user_password = request.form.get("user_password")
        user_password_new = request.form.get("user_password_new")
        user_password_new_repeat = request.form.get("user_password_new_repeat")
        if not check_password_hash(current_user.password, user_password):
            flash("Введён неверный пароль", 'error')
            return redirect(url_for('user_account'))
        elif user_password_new != user_password_new_repeat:
            flash("Пароли не совпадают", 'error')
            return redirect(url_for('user_account'))
        elif user_password_new == "":
            flash("Пароль не может быть пустым", 'error')
            return redirect(url_for('user_account'))
        elif user_password_new == user_password:
            flash("Новый пароль совпадает со старым", 'error')
            return redirect(url_for('user_account'))
        else:
            update_password(conn, user_id, generate_password_hash(user_password_new, method="sha256"))
            flash("Пароль успешно изменён", 'success')
            return redirect(url_for('user_account'))


    html = render_template(
        'user_account.html',
        user=current_user,
        len=len,
        str=str
    )
    return html
