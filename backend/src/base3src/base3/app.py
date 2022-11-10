import json
import tornado
# import base3.decorators
from base3.decorators import route
import tornado.web


# import base3.decorators

class NotFoundHandler(tornado.web.RequestHandler):
    def prepare(self):
        self.set_status(404)
        self.write(json.dumps({'code': 'NOTFOUND', 'message': 'resource not found'}))

    def get(self):
        pass


import socketio


def make_app(print_routes=True, debug=True):
    r = []
    for i in route.handlers():
        uri, handler_class, static = i
        if static:
            r.append((r'{}'.format(uri), handler_class, static))
        else:
            r.append((r'{}'.format(uri), handler_class))

    from .sio_server import sio
    if sio:
        # print("Registering /socket.io/ handler")
        r.append((r"/socket.io/", socketio.get_tornado_handler(sio)))

    if print_routes:
        route.print_all_routes()

    app = tornado.web.Application(r, debug=debug, autoreload=True, default_handler_class=NotFoundHandler, cookie_secret='digitalcube')  # cookie_secret - use from settings
    return app


def run(port=8888, app_name='generic', print_routes=True, debug=True, pre_run_async_methods=[]):
    app = make_app(print_routes, debug)
    app.listen(port)

    loop = tornado.ioloop.IOLoop.current()
    for method in pre_run_async_methods:
        loop.run_sync(method)

    print(f'base server for the application {app_name} listening at port', port)
    loop.start()
