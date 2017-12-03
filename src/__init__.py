# Sound board app
import inspect
import os
import json
import sqlite3
import yaml
from docopt import docopt
from flask import Flask
from flask import Response
from flask import request
from flask import send_from_directory
from flask import send_file
from .clips import Clip
from .clips import all_clips

class Soundboard(Flask):
    def __init__(self, soundboard_config):
        super().__init__(__name__)
        self.sb_config = soundboard_config
        # Register all of our routes
        self.route("/")(self.index)
        self.route("/static/<path:path>")(self.serve_static)
        self.route("/audio/<int:clipid>.mp3")(self.serve_clip_audio)
        # self.route("/signup")
        # self.route("/login")
        self.route("/api/clips", methods=['GET'])(self.clips_all)
        self.route("/api/clips", methods=['POST'])(self.clips_create)
        self.route("/api/clips/<int:clipid>", methods=['GET'])(self.clips_get)
        self.route("/api/clips/<int:clipid>", methods=['PATCH'])(self.clips_update)
        self.route("/api/clips/<int:clipid>", methods=['DELETE'])(self.clips_delete)
        self.route("/api/tags", methods=['GET'])(self.tags_all)
        self.route("/api/tags", methods=['POST'])(self.tags_create)
        self.route("/api/tags/<int:tagid>", methods=['GET'])(self.tags_get)
        self.route("/api/tags/<int:tagid>", methods=['PATCH'])(self.tags_update)
        self.route("/api/tags/<int:tagid>", methods=['DELETE'])(self.tags_delete)
        # Get our database stuff sorted out
        if self.sb_config.data_dir[0] != "/":
            self.clip_path = os.path.join(os.getcwd(), self.sb_config.data_dir)
        else:
            self.clip_path = self.sb_config.data_dir
        self.db_conn = sqlite3.connect(self.sb_config.db_file)
        self.prepare_db()

    def prepare_db(self):
        sql_clips = 'CREATE TABLE IF NOT EXISTS clips (id INTEGER PRIMARY KEY, name TEXT NOT NULL, start INTEGER NOT NULL, end INTEGER NOT NULL, url TEXT NOT NULL)'
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

    def serve_clip_audio(self, clipid):
        clip = Clip.load(self.db_conn, clipid)
        file_path = "{}{}.mp3".format(self.clip_path, clip.pkid)
        file_name = "{}_{}.mp3".format(clip.name, clip.pkid)
        return send_file(file_path, mimetype='audio/mpeg', attachment_filename=file_name)

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
        # prepare values for creating the clip instance
        name = data.get('name', None)
        url = data.get('url', None)
        start = data.get('start', None)
        end = data.get('end', None)
        if None in [name, url, start, end]:
            return ('', 400)
        # instantiate and save object
        clip = Clip(name, url, start, end)
        try:
            clip.save(self.db_conn)
        except ValueError as e:
            return json_response({'error': True, 'field': 'url', 'message': str(e)}, 400)
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

class Configuration(object):
    defaults = {
        "config_file": "/etc/soundboard.yml",
        "host": "0.0.0.0",
        "port": "8000",
        "db_file": "/var/opt/soundboard/db.sqlite3",
        "data_dir": "/var/opt/soundboard/data"
    }
    def __init__(self, config_file=None):
        self.set_defaults()
        if config_file is not None:
            self.set_setting("config_file", config_file, "init")

    def _clean_setting(self, string):
        return string.replace('-', '_')

    def _valid_setting(self, string):
        return self._clean_setting(string) in self.defaults

    def set_setting(self, setting, value, source):
        if self._valid_setting(setting) is False:
            raise ValueError("Found invalid setting '{}'.".format(setting))
        setattr(self, self._clean_setting(setting), value)

    def set_defaults(self):
        self.set_from_dict(self.defaults, "defaults")

    def set_from_file(self):
        content = ""
        # Read the actual content
        # TODO: Handle error: FileNotFoundError
        with open(self.config_file) as rfile: # pylint: disable=no-member
            content = rfile.read()
        # Parse the config content
        file_configs = yaml.load(content)
        # Start assigning the values of the settings
        self.set_from_dict(file_configs, "file")

    def set_from_dict(self, config_dict, source="dict"):
        for setting in config_dict:
            self.set_setting(setting, config_dict[setting], source)

def json_response(serializable, status_code=200):
    serialized = json.dumps(serializable)
    return Response(serialized, status=status_code, mimetype='application/json')

def main():
    """ soundboard

    Usage:
      soundboard [options]

    Options:
      --config-file <config_file>
      --host <host>
      --port <port>
      --db-file <db_file>
      --data-dir <data_dir>
    """

    arguments = docopt(main.__doc__)
    # Cleans the dictionary of any key-value pair where the value is None. This
    # will also strip the leading "--" off any key that has a value != None
    arguments = {k[2:]: v for k, v in arguments.items() if v is not None}

    config_file = arguments.pop("config-file", Configuration.defaults['config_file'])
    config = Configuration(config_file=config_file)
    config.set_from_file()
    config.set_from_dict(arguments, "cli")

    app = Soundboard(config)
    app.run(host=config.host, port=config.port) # pylint: disable=no-member

