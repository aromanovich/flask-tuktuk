#!env python
from flask.ext.script import Manager

from flask.ext.tuktuk.commands import TukTukCommand

from app import app


manager = Manager(app)
manager.add_command('tuktuk', TukTukCommand)


if __name__ == '__main__':
    manager.run()