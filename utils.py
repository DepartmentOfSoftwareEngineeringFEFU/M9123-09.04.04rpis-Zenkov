import sqlite3 
import glob
import os
from pathlib import Path
from bs4 import BeautifulSoup
from langcodes import tag_is_valid, Language
PATH = os.path.dirname(__file__)


def clamp(value, min_limit, max_limit):
    return max(min_limit, min(value, max_limit))


def insert_video_tracks(video_tag):
    src = PATH + video_tag['src']
    filename = Path(src).stem
    pattern = f'{filename}*.vtt'
    glob_pattern = os.path.splitext(src)[0].replace(filename, pattern)
    subtitleFiles = glob.glob(glob_pattern)
    soup = BeautifulSoup('', 'html.parser')
    for subtitleFile in subtitleFiles:
        language = Path(subtitleFile).stem[-2:]
        if tag_is_valid(language):
            local_path = subtitleFile.replace(PATH, "").replace('\\', '/')
            track_tag = soup.new_tag("track", attrs={'src': local_path, 'default': '', 'kind': 'subtitles', 'srclang': language, 'label': Language.get(language).display_name(language)})
            video_tag.append(track_tag)
    return video_tag


def prepare_videos(html_data):
    prepared_html = html_data
    soup = BeautifulSoup(html_data, 'html.parser')
    for video_frame in soup.find_all('iframe', {"class": "ql-video"}):
        video_src = video_frame['src']
        parent = video_frame.parent
        # remove iframe with all subtags
        player_tag = soup.new_tag('div', attrs={'class': 'videoplayer'})
        video_tag = soup.new_tag('video', attrs={'src': video_src, 'controls': '', 'onloadstart': 'PrepareVideos()'})
        video_tag = insert_video_tracks(video_tag)
        player_tag.append(video_tag)
        subtitles_tag = soup.new_tag('div', attrs={'class': 'subtitles'})
        player_tag.append(subtitles_tag)
        video_frame.insert_after(player_tag)
        video_frame.extract()
    return str(soup)


def get_prepared_html(html_data):
    prepared_html = prepare_videos(html_data)
    return prepared_html
    
 
def get_db_connection():
    return sqlite3.connect('main.sqlite')
