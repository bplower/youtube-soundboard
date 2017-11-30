import functools

class Clip(object):
    def __init__(self, name, url):
        self.name = name
        self.url = url
        self._pkid = None

    def is_saved(self):
        return self._pkid is not None

    def save(self, db_conn):
        if self.is_saved():
            # We want to update the database
            update(db_conn, self._pkid, self.name, self.url)
        else:
            # We want to create in the database
            row = create(db_conn, self.name, self.url)
            self._pkid = row[0]

    def delete(self, db_conn):
        if self.is_saved() is False:
            raise ValueError("Object is not saved yet. Nothing to delete.")
        delete(db_conn, self._pkid)

    def as_dict(self):
        return { "name": self.name, "url": self.url, "pkid": self._pkid }

    @classmethod
    def load(cls, db_conn, pkid):
        clip_row = get(db_conn, pkid)
        return cls.from_row(clip_row)

    @classmethod
    def from_row(cls, row):
        pkid = row[0]
        name = row[1]
        url = row[2]
        clip = cls(name, url)
        clip.__dict__['_pkid'] = pkid
        return clip

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

def create(db_conn, name, url):
    sql = 'INSERT INTO clips VALUES (null, ?, ?)'
    curs = db_conn.cursor()
    curs.execute(sql, (name, url))
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
