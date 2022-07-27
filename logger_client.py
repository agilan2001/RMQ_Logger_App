import json
import threading
import time
import pika

class LoggerClient:

    def __init__(self, clientId, log_levels, rmq_url, user, pswd, exch):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=rmq_url, credentials=pika.PlainCredentials(user, pswd)))
        self.clientId = clientId
        self.exch = exch

        self.log_file = open(f'logs/log-{self.clientId}.log', 'w')
        self.log_file.write(f"time,level,cpu,memory,disk,sent_bytes,rec_bytes\n")

        self.channel = self.connection.channel()

        self.channel.exchange_declare(exchange=self.exch, exchange_type='direct')

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.queue_name = result.method.queue

        self.log_levels = log_levels
        
        for log_level in log_levels:
            self.channel.queue_bind(exchange=self.exch, queue=self.queue_name, routing_key=log_level)


        
    def start_consumer(self):
        def on_message(ch, method, properties, body):
            log_txt = body.decode("UTF-8")
            log_json = json.loads(body)
            self.log_file.write(f"{log_json['time']},{log_json['level']},{log_json['cpu_stat']['cpu']},{log_json['cpu_stat']['memory']},{log_json['cpu_stat']['disk']},{log_json['cpu_stat']['sent_bytes']},{log_json['cpu_stat']['rec_bytes']}" + "\n")
            self.ws.send(log_txt)
           
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=on_message, auto_ack=True)
        self.channel.start_consuming()
        

    def start_client_consume(self, ws):
        self.ws = ws
        self.th = threading.Thread(target=self.start_consumer)
        self.th.start()
        self.ws.receive()

    def stop_consumer(self):
        self.log_file.close()
        self.channel.stop_consuming()
        self.connection.close()
        return "closed"




        