# Sound board app
import inspect
import os
import json
import sqlite3
from docopt import docopt
from flask import Flask
from flask import Response
from flask import request
from flask import send_from_directory
from .clips import Clip
from .clips import all_clips

class Soundboard(Flask):
    def __init__(self, db_path):
        super().__init__(__name__)
        # Register all of our routes
        self.route("/static/<path:path>")(self.serve_static)
        self.route("/")(self.index)
        # self.route("/signup")
        # self.route("/login")
        self.route("/api/clips", methods=['GET'])(self.clips_all)
        self.route("/api/clips", methods=['POST'])(self.clips_create)
        self.route("/api/clips/<clipid>", methods=['GET'])(self.clips_get)
        self.route("/api/clips/<clipid>", methods=['PATCH'])(self.clips_update)
        self.route("/api/clips/<clipid>", methods=['DELETE'])(self.clips_delete)
        self.route("/api/tags", methods=['GET'])(self.tags_all)
        self.route("/api/tags", methods=['POST'])(self.tags_create)
        self.route("/api/tags/<tagid>", methods=['GET'])(self.tags_get)
        self.route("/api/tags/<tagid>", methods=['PATCH'])(self.tags_update)
        self.route("/api/tags/<tagid>", methods=['DELETE'])(self.tags_delete)
        # Get our database stuff sorted out
        self.db_path = db_path
        self.db_conn = sqlite3.connect(self.db_path)
        self.prepare_db()

    def prepare_db(self):
        sql_clips = 'CREATE TABLE IF NOT EXISTS clips (id INTEGER PRIMARY KEY, name TEXT NOT NULL, url TEXT NOT NULL)'
        sql_tags = 'CREATE TABLE IF NOT EXISTS tags (id INTEGER PRIMARY KEY, name TEXT NOT NULL)'
        curs = self.db_conn.cursor()
        curs.execute(sql_clips)
        curs.execute(sql_tags)
        self.db_conn.commit()

    def serve_static(self, path):
        """ Route /static/*

        Serves static files from the 'static' folder within the python package
        """
        pkg_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        return send_from_directory(pkg_path + "/static", path)

    def index(self):
        """ Route /

        Gets the index page
        """
        return self.serve_static('index.html')

    # api clip endpoints
    def clips_all(self):
        clip_objects = all_clips(self.db_conn)
        clip_dicts = list(map(lambda x: x.as_dict(), clip_objects))
        return json_response(clip_dicts)

    def clips_create(self):
        # dictionary of args to provide to the procedure function
        data = json.loads(str(request.get_data().decode('utf-8')))
        clip = Clip(data['name'], data['url'])
        clip.save(self.db_conn)
        return json_response(clip.as_dict())

    def clips_get(self, clipid):
        clip = Clip.load(self.db_conn, clipid)
        return json_response(clip.as_dict())

    def clips_update(self, clipid):
        pass

    def clips_delete(self, clipid):
        clip = Clip.load(self.db_conn, clipid)
        clip.delete(self.db_conn)
        return ('', 204)

    # api tag endpoints
    def tags_all(self):
        pass

    def tags_create(self):
        pass

    def tags_get(self):
        pass

    def tags_update(self):
        pass

    def tags_delete(self):
        pass

def json_response(serializable):
    serialized = json.dumps(serializable)
    return Response(serialized, mimetype='application/json')

def main():
    """ soundboard

    Usage:
      soundboard [options]
    """
    app = Soundboard("db.sqlite3")
    app.run(host="127.0.0.1", port=8000)