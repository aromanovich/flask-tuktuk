#!/bin/bash
PYTHONPATH=.:$PYTHONPATH py.test -s --tb=short --showlocals \
                                 --cov-report term-missing --cov flask_tuktuk ./tests "$@"