from flask import Flask, request, send_file
from werkzeug.wsgi import SharedDataMiddleware
from gevent import monkey; monkey.patch_all()

from socketio import socketio_manage
from socketio.server import SocketIOServer
from socketio.namespace import BaseNamespace
from socketio.mixins import BroadcastMixin, RoomsMixin

import os
import json


positions = {}

class DefaultNamespace(BaseNamespace, RoomsMixin, BroadcastMixin):
    def __init__(self, *args, **kwargs):
        super(DefaultNamespace, self).__init__(*args, **kwargs)

    def emit(self, event, args):
        self.socket.send_packet(dict(type="event", name=event,
            args=args, endpoint=self.ns_name))

    def on_localized(self, coords):
        self.emit('init_neighbors', positions)
        id = self.socket.sessid
        positions[id] = coords
        self.broadcast_event_not_me('neighbor_localized', [id, coords])

app = Flask(__name__)

@app.route("/socket.io/<path:path>")
def run_socketio(path):
    socketio_manage(request.environ, {'/default': DefaultNamespace})
    return ''

if __name__ == '__main__':
    print 'Listening on http://localhost:8080'
    app.debug = True
    server = SocketIOServer(
        ('0.0.0.0', 8080),
        SharedDataMiddleware(app, {}),
        namespace="socket.io",
        policy_server=False)
    server.serve_forever()
