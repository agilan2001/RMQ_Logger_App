
import time
from flask import Flask, render_template, request
from flask_sock import Sock

app = Flask(__name__)
sock = Sock(app)

from publish_client import PublisherClient
publisher = PublisherClient()

from logger_client import LoggerClient
log_clients = dict()

@app.post("/start_publish")
def start_publish():
    rmq_url = request.json['rmq_url']
    user = request.json['user']
    pswd = request.json['pswd']
    exch = request.json['exch']
    return publisher.start_publish(rmq_url, user, pswd, exch)

@app.get("/stop_publish")
def stop_publish():
    return publisher.stop_publish()

@app.post("/set_interval")
def set_interval():
    interval = request.json['interval']
    return publisher.set_interval(interval)

@app.post("/set_level")
def set_level():
    log_level = request.json['log_level']
    return publisher.set_level(log_level)

@app.post("/new_client")
def new_client():
    try:
        log_levels = [x for x in request.form if request.form[x] == 'true']
        # print(log_levels)
        # return "hi"
        clientId = f"Client_{str(int(time.time()))}_{str(len(log_clients) + 1)}"
        new_log_client = LoggerClient(clientId, log_levels, request.form['rmq_url'], request.form['rmq_user'], request.form['rmq_pswd'], request.form['rmq_exch'])
        log_clients[clientId] = new_log_client
        return render_template("Logger_Client.html", clientId = clientId, log_levels = str(log_levels))
    except:
        return "Error Occurred"

@sock.route("/log_client")
def log_client(ws):
    clientId = ws.receive()
    log_clients[clientId].start_client_consume(ws)

@app.post("/stop_client")
def stop_client():
    clientId = request.json['clientId']
    return log_clients[clientId].stop_consumer()
    
    





