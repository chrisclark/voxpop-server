from flask import Flask
from flask_socketio import SocketIO, join_room
from meeting import Meeting
import os
import redis

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET')
socketio = SocketIO(app, cors_allowed_origins='*')

rurl = os.environ.get('REDIS_URL')
r = redis.StrictRedis.from_url(rurl, decode_responses=True)

@socketio.on('toggle_user')
def handle_toggled(json):
    mtg_name, user, m = destructure(json)
    m.toggle_user(user)
    queue_update(m)

@socketio.on('user_connected')
def handle_connect(json):
    mtg_name, user, m = destructure(json)
    join_room(mtg_name)
    m.add_user(user)
    print(user + ' joined ' + mtg_name)
    queue_update(m)

@socketio.on('remove_user')
def handle_remove_user(json):
    mtg_name, user, m = destructure(json)
    m.remove_user(user)
    queue_update(m)

def destructure(json):
    mtg_name = json['mtg']
    user = json['user']
    m = Meeting(r, mtg_name)
    return mtg_name, user, m

def queue_update(m):
    socketio.emit('queue_update', {
        'users_list': m.users,
        'queue': m.queue
    }, room=m.name)


if __name__ == '__main__':
    socketio.run(app, debug=os.environ.get('DEBUG', False))
