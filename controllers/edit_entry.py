import codecs
import os
import shutil
import json
import re
from flask import render_template, request, session, redirect, url_for, flash
from flask_login import current_user
from werkzeug.utils import secure_filename
from app import app, ALLOWED_EXTENSIONS, ALLOWED_AUDIO_EXTENSIONS, VTT_PATTERN
from utils import get_db_connection
from controllers.constructor import create_directory, create_file
from models.edit_entry_model import *
from models.constructor_model import delete_path, get_book, is_author
from models.guidebook_model import get_all_students

DEFAULT_TEXT_SIZE = 10
DEFAULT_TEXT_MAXLENGTH = 10
DEFAULT_TXAR_ROWS = 8
DEFAULT_NUMB_MIN = 1
DEFAULT_NUMB_MAX = 99
DEFAULT_DIAG_REPLIES = 4
DEFAULT_MAX_POINTS = 1
DEFAULT_CHECK = 'False'
DEFAULT_HEADER_ALIGN = 'left'
DEFAULT_HEADER_SIZE = 'normal'
DEFAULT_IN_CONTENTS = 'False'


def delete_entry_answers(book_id, entry_id):
    root_dir = f'static/guidebooks/{book_id}/answers'
    for foldername, subfolders, filenames in os.walk(root_dir):
        subfolder_path = os.path.join(foldername, str(entry_id))
        if os.path.exists(subfolder_path):
            try:
                shutil.rmtree(subfolder_path)
                print(f"Deleted subfolder: {subfolder_path}")
            except Exception as e:
                print(f"Error deleting {subfolder_path}: {e}")


def is_json(path):
    if os.path.exists(path):
        f = codecs.open(path, 'r')
        first_char = f.read(1)
        f.close()
        if first_char == '{':
            return True
    return False


def save_task_data(book_id, entry_id, task_data):
    path = f'static/guidebooks/{book_id}/entries/{entry_id}/'
    filename = 'info.dat'
    create_directory(path)
    create_file(path, filename, '')
    full_path = os.path.join(app.path, f'{path}/{filename}')
    if not is_json(full_path) and os.path.exists(full_path):
        os.remove(full_path)
        create_file(path, filename, '')
    f = open(os.path.join(app.path, f'{path}/{filename}'), 'w')
    json.dump(task_data, f)
    f.close()


def get_task_data(book_id, entry_id):
    task_data = None
    path = os.path.join(app.path, 'static/guidebooks/' + str(book_id) + '/entries/' + str(entry_id))
    if os.path.exists(path) and os.path.exists(path + '/info.dat'):
        if is_json(path + '/info.dat'):
            f = codecs.open(path + '/info.dat', 'r')
            task_data = json.load(f)
            f.close()
    return task_data


def get_text_data(book_id, entry_id, data_type):
    size = DEFAULT_TEXT_SIZE
    maxlength = DEFAULT_TEXT_MAXLENGTH
    task_data = get_task_data(book_id, entry_id)
    if task_data is not None and 'size' in task_data.keys():
        size = task_data['size']
    if task_data is not None and 'maxlength' in task_data.keys():
        maxlength = task_data['maxlength']
    if data_type == 'size':
        return size
    else:
        return maxlength


def get_txar_data(book_id, entry_id):
    rows = DEFAULT_TXAR_ROWS
    task_data = get_task_data(book_id, entry_id)
    if task_data is not None and 'rows' in task_data.keys():
        rows = task_data['rows']
    return rows


def get_numb_data(book_id, entry_id, data_type):
    numb_min = DEFAULT_NUMB_MIN
    numb_max = DEFAULT_NUMB_MAX
    task_data = get_task_data(book_id, entry_id)
    if task_data is not None and 'min' in task_data.keys():
        numb_min = task_data['min']
    if task_data is not None and 'max' in task_data.keys():
        numb_max = task_data['max']
    if data_type == 'min':
        return numb_min
    else:
        return numb_max


def is_file_allowed(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def is_audio_file_allowed(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_AUDIO_EXTENSIONS


def update_contents(book_id, entry_id, entry_contents):
    path = os.path.join(app.path, 'templates/guidebooks/' + str(book_id) + '/entries/' + str(entry_id))
    if os.path.exists(path) and os.path.exists(path + '/contents.html'):
        f = codecs.open(path + '/contents.html', 'w', 'utf-8-sig')
        f.write(entry_contents)
        f.close()


def get_all_images(book_id):
    files = []
    path = os.path.join(app.path, 'static/guidebooks/' + str(book_id) + '/files')
    if os.path.exists(path):
        for file in os.listdir(path):
            if file.endswith(".jpg") or file.endswith(".jpeg") or file.endswith(".png"):
                files.append(file)
    return files
    
    
def get_all_videos(book_id):
    files = []
    path = os.path.join(app.path, 'static/guidebooks/' + str(book_id) + '/files')
    if os.path.exists(path):
        for file in os.listdir(path):
            if file.endswith(".mp4") or file.endswith(".webm") or file.endswith(".mov"):
                files.append(file)
    return files


def get_all_audios(book_id):
    files = []
    path = os.path.join(app.path, 'static/guidebooks/' + str(book_id) + '/files')
    if os.path.exists(path):
        for file in os.listdir(path):
            if file.endswith(".wav") or file.endswith(".mp3") or file.endswith(".ogg"):
                files.append(file)
    return files


# clean VTT file from HTML tags except tags in VTT_PATTERN
def clean_file(path):
    name, extention = os.path.splitext(path)
    if extention == '.vtt':
        pattern = VTT_PATTERN
        with open(path, "r+") as file:
            content = file.read()
            clean_content = re.sub(pattern, '', content)
            file.seek(0)
            file.write(clean_content)


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        book_id = request.form.get("book_id")
        entry_id = request.form.get("entry_id")
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('Нет части, содержащей файл', 'error')
            return redirect(url_for('edit_entry') + '?b=' + str(book_id) + '&e=' + str(entry_id))
        file = request.files['file']
        filename = request.form.get("filename")

        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('Файл для загрузки не был выбран', 'error')
            return redirect(url_for('edit_entry') + '?b=' + str(book_id) + '&e=' + str(entry_id))
        if file and (is_file_allowed(file.filename) or is_audio_file_allowed(file.filename)):
            # setting filename for the uploaded file
            # if filename was specified
            if filename:
                filename_orig, file_extension = os.path.splitext(file.filename)
                filename = secure_filename(filename) + file_extension
            # if wasn't set the original filename
            else:
                filename = secure_filename(file.filename)
            path = os.path.join(app.path, 'static/guidebooks/' + str(book_id) + '/files')
            if os.path.exists(path):
                file_path = os.path.join(app.path, 'static/guidebooks/' + str(book_id) + '/files/' + filename)
                file.save(file_path)
                clean_file(file_path)
            flash('Файл был успешно загружен', 'success')
            return redirect(url_for('edit_entry') + '?b=' + str(book_id) + '&e=' + str(entry_id))
        else:
            flash('Расширение не поддерживается', 'error')
            return redirect(url_for('edit_entry') + '?b=' + str(book_id) + '&e=' + str(entry_id))
    return redirect(url_for('constructor'))


@app.route('/edit_entry', methods=['GET', 'POST'])
def edit_entry():

    if not current_user.is_authenticated or not current_user.is_editor:
        return redirect(url_for('index'))

    conn = get_db_connection()
    book_id = request.args.get('b')
    
    if book_id == None or len(get_book(conn, book_id)) < 1:
        book_id = None
        return render_template(
            'constructor.html',
            user=current_user,
            book_id=book_id,
            len=len,
            str=str
        )
    
    if not is_author(conn, current_user.id, book_id):
        flash('Нет доступа на редактирование пособия', 'error')
        book_id = None
        return render_template(
            'constructor.html',
            user=current_user,
            book_id=book_id,
            len=len,
            str=str
        )

    entry_id = None
    if request.values.get('e'):
        entry_id = request.values.get('e')
    else:
        return redirect(url_for('constructor') + '?b=' + str(book_id))

    # "Add rule" button pressed
    if request.form.get('add_rule'):
        entry_id = request.form.get("entry_id")
        entry_type = request.form.get("entry_type")
        entry_name = request.form.get("entry_name")
        update_entry(conn, entry_id, entry_name, entry_type)
        return redirect(url_for('edit_entry') + '?b=' + str(book_id) + '&e=' + str(entry_id))

    # "Add task" button pressed
    if request.form.get('add_task'):
        entry_id = request.form.get("entry_id")
        entry_type = request.form.get("entry_type")
        entry_name = request.form.get("entry_name")
        task_type = request.form.get("task_type")
        entry_type += '_' + task_type
        update_entry(conn, entry_id, entry_name, entry_type)
        match entry_type:
            case 'task_text':
                task_data = {'size': str(DEFAULT_TEXT_SIZE), 'maxlength': str(DEFAULT_TEXT_MAXLENGTH),
                             'check': DEFAULT_CHECK, 'points': str(DEFAULT_MAX_POINTS)}
                save_task_data(book_id, entry_id, task_data)
            case 'task_txar':
                task_data = {'rows': str(DEFAULT_TXAR_ROWS), 'check': DEFAULT_CHECK, 'points': str(DEFAULT_MAX_POINTS)}
                save_task_data(book_id, entry_id, task_data)
            case 'task_numb':
                task_data = {'min': str(DEFAULT_NUMB_MIN), 'max': str(DEFAULT_NUMB_MAX), 'check': DEFAULT_CHECK, 'points': str(DEFAULT_MAX_POINTS)}
                save_task_data(book_id, entry_id, task_data)
            case 'task_chbx' | 'task_radi' | 'task_ordr':
                task_data = {'check': DEFAULT_CHECK, 'points': str(DEFAULT_MAX_POINTS)}
                save_task_data(book_id, entry_id, task_data)
            case 'task_diag':
                task_data = {'replies': str(DEFAULT_DIAG_REPLIES), 'points': str(DEFAULT_MAX_POINTS)}
                save_task_data(book_id, entry_id, task_data)
            case 'task_audi':
                task_data = {'points': str(DEFAULT_MAX_POINTS)}
                save_task_data(book_id, entry_id, task_data)
        return redirect(url_for('edit_entry') + '?b=' + str(book_id) + '&e=' + str(entry_id))
        
    df_entry = get_entry(conn, entry_id)

    # "Save" button pressed
    if request.form.get('save'):
        entry_id = request.form.get("entry_id")
        entry_type = request.form.get("entry_type")
        entry_name = request.form.get("entry_name")
        entry_contents = request.form.get("entry_contents")
        match entry_type:
            case 'rule' | 'rule_nic':
                entry_type = "rule_nic"
                if request.form.get('entry_in_contents'):
                    entry_type = "rule"
                header_align = request.form.get('header_align')
                if header_align is None: header_align = DEFAULT_HEADER_ALIGN
                header_size = request.form.get('header_size')
                if header_size is None: header_size = DEFAULT_HEADER_SIZE
                in_contents_main = 'False'
                if request.form.get('in_contents_main'):
                    in_contents_main = 'True'
                task_data = {'header_align': str(header_align), 'header_size': str(header_size),
                             'in_contents_main': str(in_contents_main)}
                save_task_data(book_id, entry_id, task_data)
            case 'task_text':
                text_size = request.form.get('size')
                text_maxlength = request.form.get('maxlength')
                check = request.form.get('check')
                points = request.form.get('points')
                if points is None: points = DEFAULT_MAX_POINTS
                if text_size is None: text_size = DEFAULT_TEXT_SIZE
                if text_maxlength is None: text_maxlength = DEFAULT_TEXT_MAXLENGTH
                if check is None:
                    check = DEFAULT_CHECK
                else:
                    check = 'True'
                task_data = {'size': str(text_size), 'maxlength': str(text_maxlength), 'check': check, 'points': str(points)}
                save_task_data(book_id, entry_id, task_data)
            case 'task_txar':
                txar_rows = request.form.get('rows')
                check = request.form.get('check')
                points = request.form.get('points')
                if points is None: points = DEFAULT_MAX_POINTS
                if txar_rows is None: txar_rows = DEFAULT_TXAR_ROWS
                if check is None:
                    check = DEFAULT_CHECK
                else:
                    check = 'True'
                task_data = {'rows': str(txar_rows), 'check': check, 'points': str(points)}
                save_task_data(book_id, entry_id, task_data)
            case 'task_numb':
                numb_min = request.form.get('min')
                numb_max = request.form.get('max')
                check = request.form.get('check')
                points = request.form.get('points')
                if points is None: points = DEFAULT_MAX_POINTS
                if numb_min is None: numb_min = DEFAULT_NUMB_MIN
                if numb_max is None: numb_max = DEFAULT_NUMB_MAX
                if check is None:
                    check = DEFAULT_CHECK
                else:
                    check = 'True'
                task_data = {'min': str(numb_min), 'max': str(numb_max), 'check': check, 'points': str(points)}
                save_task_data(book_id, entry_id, task_data)
            case 'task_diag':
                diag_replies = request.form.get('replies')
                points = request.form.get('points')
                if points is None: points = DEFAULT_MAX_POINTS
                if diag_replies is None: diag_replies = DEFAULT_DIAG_REPLIES
                task_data = {'replies': str(diag_replies), 'points': str(points)}
                save_task_data(book_id, entry_id, task_data)
            case 'task_chbx' | 'task_radi' | 'task_ordr':
                check = request.form.get('check')
                points = request.form.get('points')
                if points is None: points = DEFAULT_MAX_POINTS
                if check is None:
                    check = DEFAULT_CHECK
                else:
                    check = 'True'
                task_data = {'check': check, 'points': str(points)}
                save_task_data(book_id, entry_id, task_data)
            case 'task_audi':
                points = request.form.get('points')
                if points is None: points = DEFAULT_MAX_POINTS
                task_data = {'points': str(points)}
                save_task_data(book_id, entry_id, task_data)

        delete_entry_answers(book_id, entry_id)
        update_entry(conn, entry_id, entry_name, entry_type)
        update_contents(book_id, entry_id, entry_contents)
        return redirect(url_for('edit_entry') + '?b=' + str(book_id) + '&e=' + str(entry_id))

    # "Delete file" button pressed
    if request.form.get('delete_image') or request.form.get('delete_video') or request.form.get('delete_audio'):
        filename = request.form.get("file")
        if filename is not None:
            os.remove(os.path.join(app.path, 'static/guidebooks/' + book_id + '/files/' + filename))
            flash('Файл успешно удалён', 'success')
            return redirect(url_for('edit_entry') + '?b=' + str(book_id) + '&e=' + str(entry_id))
        else:
            flash('Файл для удаления не был выбран', 'error')
            return redirect(url_for('edit_entry') + '?b=' + str(book_id) + '&e=' + str(entry_id))

    images = get_all_images(book_id)
    videos = get_all_videos(book_id)
    audios = get_all_audios(book_id)
    images.sort()
    videos.sort()
    audios.sort()

    text_size = DEFAULT_TEXT_SIZE
    text_maxlength = DEFAULT_TEXT_MAXLENGTH
    txar_rows = DEFAULT_TXAR_ROWS
    numb_min = DEFAULT_NUMB_MIN
    numb_max = DEFAULT_NUMB_MAX
    diag_replies = DEFAULT_DIAG_REPLIES
    check = DEFAULT_CHECK
    points = DEFAULT_MAX_POINTS
    header_size = DEFAULT_HEADER_SIZE
    header_align = DEFAULT_HEADER_ALIGN
    in_contents_main = DEFAULT_IN_CONTENTS
    df_entry_type = get_entry_type_name(conn, entry_id)
    entry_type = 'none'
    if len(df_entry_type) > 0:
        entry_type = df_entry_type.iloc[0]['entry_type_name']
    task_data = get_task_data(book_id, entry_id)
    match entry_type:
        case 'rule' | 'rule_nic':
            if task_data is not None and 'header_size' in task_data.keys():
                header_size = task_data['header_size']
            if task_data is not None and 'header_align' in task_data.keys():
                header_align = task_data['header_align']
            if task_data is not None and 'in_contents_main' in task_data.keys():
                in_contents_main = task_data['in_contents_main']
        case 'task_text':
            if task_data is not None and 'size' in task_data.keys():
                text_size = task_data['size']
            if task_data is not None and 'maxlength' in task_data.keys():
                text_maxlength = task_data['maxlength']
        case 'task_txar':
            if task_data is not None and 'rows' in task_data.keys():
                txar_rows = task_data['rows']
        case 'task_numb':
            if task_data is not None and 'min' in task_data.keys():
                numb_min = task_data['min']
            if task_data is not None and 'max' in task_data.keys():
                numb_max = task_data['max']
        case 'task_diag':
            if task_data is not None and 'replies' in task_data.keys():
                diag_replies = task_data['replies']
    if task_data is not None and 'check' in task_data.keys():
        check = task_data['check']
    if task_data is not None and 'points' in task_data.keys():
        points = task_data['points']

    html = render_template(
        'edit_entry.html',
        entries=df_entry,
        book_id=book_id,
        entry_id=entry_id,
        user=current_user,
        images=images,
        videos=videos,
        audios=audios,
        size=text_size,
        maxlength=text_maxlength,
        rows=txar_rows,
        min=numb_min,
        max=numb_max,
        replies=diag_replies,
        check=check,
        points=points,
        header_align=header_align,
        header_size=header_size,
        in_contents_main=in_contents_main,
        len=len,
        str=str
    )
    return html