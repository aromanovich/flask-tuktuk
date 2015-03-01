# coding: utf-8
from __future__ import unicode_literals, print_function

import os
import pkgutil

import jsl
from flask import current_app
from flask.ext.script import Manager

from .helpers import pycharm


TukTukCommand = Manager()


@TukTukCommand.command
def build_helpers():
    if 'TUKTUK_HELPERS_MODULE' not in current_app.config:
        raise Exception('Config variable TUKTUK_HELPERS_MODULE is not set.')
    helpers_module = current_app.config['TUKTUK_HELPERS_MODULE']
    package = pkgutil.get_loader(helpers_module)
    if package is None:
        raise Exception('Module "{0}" does not exist. '
                        'Please create it before running the command.'.format(helpers_module))
    lines = pycharm.generate_module(jsl.registry.iter_documents())
    with open(package.filename, 'w') as f:
        f.write('\n'.join(lines))
    filename = os.path.relpath(package.filename, os.getcwd())
    print('Helpers module has been created. See {0} for the source code.'.format(filename))