from gevent.monkey import patch_all
patch_all()

import os, sys

CUR_DIR = os.path.dirname(os.path.realpath(__file__))

sys.path.insert(0, CUR_DIR)
os.environ['DJANGO_SETTINGS_MODULE'] = 'cherrypick.settings'

from gevent.pywsgi import WSGIServer
import django.core.handlers.wsgi

if __name__ == '__main__':
    print 'Serving on 8088...'
    application = django.core.handlers.wsgi.WSGIHandler()
    WSGIServer(('', 8000), application).serve_forever()
