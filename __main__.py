from twisted.internet import reactor, endpoints
from twisted.web.wsgi import WSGIResource
from twisted.python.threadpool import ThreadPool
from twisted.web import static, server
from twisted.application import service, strports
from twisted.web.server import Site
import privadome_frontend.backend.wsgi as a
import os, sys
import sqlite3

def main():
    wsgiThreadPool = ThreadPool()
    wsgiThreadPool.start()
    reactor.addSystemEventTrigger('after', 'shutdown', wsgiThreadPool.stop)
    wsgiAppAsResource = WSGIResource(reactor, wsgiThreadPool, a.application)

    BASE_DIR = module_path()
    print(BASE_DIR)
    if check_first_run(BASE_DIR):
        try:
            pass
            #initialize_installation()
        except Exception as ex:
            print(ex)
            raise ex

    root = static.File(os.path.join(BASE_DIR, "static"))
    index = static.File(os.path.join(BASE_DIR, "static/index.html"))
    root.putChild(b"api", wsgiAppAsResource)
    root.childNotFound = index
    reactor.listenTCP(8080, Site(root))
    reactor.run()

def initialize_installation():
    from privadome_frontend import manage
    manage.main(['manage.py', 'migrate'])
    print("----------- PLEASE CREATE YOUR DEFAULT USER -----------")
    manage.main(['manage.py', 'createsuperuser'])

def check_first_run(base_dir):
    try:
        conn = sqlite3.connect(os.path.join(base_dir, 'privadome_frontend.sqlite3'))
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*)
            FROM '{0}'
            WHERE id = 1
            """.format('django_migrations'))
        if cursor.fetchone()[0] == 1:
            conn.close()
            return False
        conn.close()
        return True
    except Exception as ex:
        print(ex)
        conn.close()
        return True

def module_path():
    if hasattr(sys, "frozen"):
        return os.path.dirname(sys.executable)
    return os.path.dirname(__file__)

if __name__ == '__main__':
    main()