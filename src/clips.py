import os.path
import functools
import youtube_dl
from pydub import AudioSegment

class Clip(object):
    def __init__(self, name, url, start, end):
        self.name = name
        self.url = url
        self.start = int(start)
        self.end = int(end)
        self._pkid = None

    @property
    def pkid(self):
        return self._pkid

    def is_saved(self):
        return self._pkid is not None

    def save(self, db_conn, save_directory):
        # Handle storage actions first
        if self.is_saved():
            # We want to update the database
            update(db_conn, self._pkid, self.name, self.url)
        else:
            # We want to create in the database
            row = create(db_conn, self.name, self.url, self.start, self.end)
            self._pkid = row[0]
        # Create the clip
        download_path = download_video(self.url)
        clip_path = "{}/{}.mp3".format(save_directory, self.pkid)
        create_clip(download_path, clip_path, self.start, self.end)

    def delete(self, db_conn):
        if self.is_saved() is False:
            raise ValueError("Object is not saved yet. Nothing to delete.")
        delete(db_conn, self._pkid)

    def as_dict(self):
        return {
            "name": self.name,
            "url": self.url,
            "pkid": self._pkid,
            "end": self.end,
            "start": self.start
        }

    @classmethod
    def load(cls, db_conn, pkid):
        clip_row = get(db_conn, pkid)
        return cls.from_row(clip_row)

    @classmethod
    def from_row(cls, row):
        pkid = row[0]
        name = row[1]
        url = row[2]
        start = row[3]
        end = row[4]
        clip = cls(name, url, start, end)
        clip.__dict__['_pkid'] = pkid
        return clip

def download_video(url):
    ydl_opts = {
        'outtmpl': "%(id)s.%(ext)s",
        'no_warnings': True,
        'quiet': True,
        'format':'bestaudio/best',
        'prefer_ffmpeg': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        }]
    }
    ydl = youtube_dl.YoutubeDL(ydl_opts)
    try:
        info_dict = ydl.extract_info(url)
    except youtube_dl.utils.DownloadError as e:
        if "Unsupported URL" in str(e):
            raise ValueError("Unsupported URL")
        else:
            raise e

    # ret_code = ydl.__dict__['_retcode']
    ret_code = 0
    filename = ydl.prepare_filename(info_dict)
    return filename.split(".")[0] + ".mp3"

def create_clip(source_path, out_path, start, end):
    milisecond = 1000
    formatted_start = milisecond * start
    formatted_end = milisecond * end
    sound = AudioSegment.from_mp3(source_path)

    clip = sound[formatted_start:formatted_end]
    clip.export(out_path, format="mp3")

########################################################################
# storage related functions

def all_clips(db_conn):
    clip_rows = all(db_conn)
    clips = list(map(lambda x: Clip.from_row(x), clip_rows))
    return clips

def all(db_conn):
    sql = 'SELECT * FROM clips'
    curs = db_conn.cursor()
    curs.execute(sql)
    clip_rows = curs.fetchall()
    return clip_rows

def create(db_conn, name, url, start, end):
    sql = 'INSERT INTO clips VALUES (null, ?, ?, ?, ?)'
    curs = db_conn.cursor()
    curs.execute(sql, (name, url, start, end))
    clipid = curs.lastrowid
    db_conn.commit()
    return get(db_conn, clipid)

def get(db_conn, clipid):
    sql = 'SELECT * FROM clips WHERE id=? LIMIT 1'
    curs = db_conn.cursor()
    curs.execute(sql, (clipid,))
    clip_row = curs.fetchone()
    return clip_row

def update(db_conn, clipid, name, url):
    sql = 'UPDATE clips name=?, url=? SET WHERE id=?'
    curs = db_conn.cursor()
    curs.execute(sql, (name, url, clipid))
    return get(db_conn, clipid)

def delete(db_conn, clipid):
    sql = 'DELETE FROM clips WHERE id=?'
    curs = db_conn.cursor()
    curs.execute(sql, (clipid,))
    db_conn.commit()
    return None
