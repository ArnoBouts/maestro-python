import comp
import json
import logging
import tempfile

log = logging.getLogger(__name__) 

def list(w, app):
    backups = []
    with tempfile.TemporaryFile() as out:
        res = comp.run(w, app, 'backup', ['list', '--json'], out)

        out.seek(0)
        content = out.read()
        if len(content) > 0:
            backups = json.loads(content)
            log.info(backups)

    return backups

def backup(w, app):
    comp.run(w, app, 'backup', ['create'])

def restore(w, app, archive):
    comp.run(w, app, 'backup', ['extract'], None, ['ARCHIVE=' + archive])
