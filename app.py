import time

from flask import Flask, request
from flask_cors import cross_origin
from flask_socketio import SocketIO

app = Flask(__name__)

socketio = SocketIO(app, debug=True, cors_allowed_origins='*', use_reloader=False)


@app.route('/startTimer', methods=['POST'])
@cross_origin()
def startTimer():
    duration = request.json.get('time')
    socketio.emit('VALUES', request.json)
    socketio.emit('VALID')
    while duration >= 0:
        socketio.emit('TIME', duration)
        time.sleep(1)
        duration -= 1
    return "ok", 200


@app.route('/values', methods=['POST'])
@cross_origin()
def values():
    socketio.emit('VALUES', request.json)
    return "ok", 200


@app.route('/valid', methods=['POST'])
@cross_origin()
def valid():
    socketio.emit('VALID', request.json.get('valid'))
    return "ok", 200


@app.route('/clear', methods=['POST'])
@cross_origin()
def clear():
    socketio.emit('VALID')
    return "ok", 200


if __name__ == '__main__':
    app.run()
