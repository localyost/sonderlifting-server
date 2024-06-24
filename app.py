from flask import Flask, request
from flask_cors import cross_origin
from flask_socketio import SocketIO

app = Flask(__name__)

socketio = SocketIO(app, debug=True, cors_allowed_origins='*', use_reloader=False)

@app.route('/startTimer', methods=['POST'])
@cross_origin()
def startTimer():

    socketio.emit('VALUES', request.json)
    socketio.emit('TIMER_START', request.json.get('time'))
    return "ok", 200


@app.route('/values', methods=['POST'])
@cross_origin()
def values():
    socketio.emit('VALUES', request.json)
    return "ok", 200

@app.route('/valid', methods=['POST'])
@cross_origin()
def valid():
    socketio.emit('TIMER_STOP')
    socketio.emit('VALID', request.json.get('valid'))
    return "ok", 200


if __name__ == '__main__':
    app.run()
