#!/usr/bin/env python

import sys
from webengine import WSGIWebEngine
from settings import APP_CONFIG

if 'lib' not in sys.path:
    sys.path[0:0] = ['lib']

app = WSGIWebEngine(config=APP_CONFIG, debug=True)