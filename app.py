import logging
import time

from flask import Flask, request
from flask_cors import cross_origin
from flask_socketio import SocketIO

app = Flask(__name__)

socketio = SocketIO(app, debug=True, cors_allowed_origins='*', use_reloader=False)


@app.route('/startTimer', methods=['POST'])
@cross_origin()
def startTimer():
    logging.info('starting timer...')
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


@app.route('/name', methods=['POST'])
@cross_origin()
def name():
    value = request.json.get('name')
    logging.info('received name: %s', value)
    return "ok", 200


@app.route('/attempt', methods=['POST'])
@cross_origin()
def attempt():
    value = request.json.get('attempt')
    logging.info('received attempt: %d', value)
    return "ok", 200


@app.route('/weight', methods=['POST'])
@cross_origin()
def weight():
    value = request.json.get('weight')
    logging.info('received weight: %.1f', value)
    return "ok", 200


@app.route('/lift', methods=['POST'])
@cross_origin()
def lift():
    name_value = request.json.get('name')
    attempt_value = request.json.get('attempt')
    weight_value = request.json.get('weight')
    valid_value = request.json.get('valid')
    logging.info('received lift: name %s, attempt %d, weight %.1f, valid %r',
                  name_value, attempt_value, weight_value, valid_value)
    return "ok", 200


if __name__ == '__main__':
    app.run()
