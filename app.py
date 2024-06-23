import time

from flask import Flask, request
from flask_cors import cross_origin
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/startTimer', methods=['POST'])
@cross_origin()
def startTimer():  # put application's code here
    tick = request.json.get('time')
    while tick:
        time.sleep(1)
        tick -= 1
        socketio.emit('time', tick)
        print(tick)


    return "ok", 200


@app.route('/values', methods=['POST'])
@cross_origin()
def values():
    # print(request.json)
    return "ok", 200

@app.route('/valid', methods=['POST'])
def valid():
    print(request.get_json())
    return "ok", 200


if __name__ == '__main__':
    app.run()
