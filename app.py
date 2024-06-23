from flask import Flask, request
from flask_socketio import SocketIO, emit
app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/startTimer', methods=['POST'])
def startTimer():  # put application's code here
    print(request.get_json())
    socketio.emit('timer_started', {'message': 'Timer has started!'})
    return "ok", 200


@app.route('/weight', methods=['POST'])
def weight():
    print(request.get_json())
    return "ok", 200

@app.route('/valid', methods=['POST'])
def valid():
    print(request.get_json())
    return "ok", 200


if __name__ == '__main__':
    app.run()
