import json
import threading
import time
import pika
import psutil

class PublisherClient:

    def __init__(self):
        self.log_level = 'log_info'
        self.interval = 2

        
        self.isPublishing = False


    def start_publish(self, rmq_url, user, pswd, exch):
        try:
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=rmq_url, credentials=pika.PlainCredentials(user, pswd)))
            self.channel = self.connection.channel()

            self.exch = exch

            print(exch)

            self.channel.exchange_declare(exchange=exch, exchange_type='direct')
            
            self.prev_sent_bytes = psutil.net_io_counters().bytes_sent
            self.prev_recv_bytes = psutil.net_io_counters().bytes_recv

            self.isPublishing = True
            self.th = threading.Thread(target= self.publish)
            self.th.start()
            return "Publish started"
        except:
            print(123)
            return "Error occurred"

    def stop_publish(self):
        self.isPublishing = False
        self.connection.close()
        return "Publish stopped"

    def set_interval(self, interval):
        self.interval = interval
        return "Interval set"

    def set_level(self, level):
        print(level)
        self.log_level = level
        return "Log_level set"
        
    def publish(self):
        while(self.isPublishing):
            cur_sent_bytes = psutil.net_io_counters().bytes_sent
            cur_rec_bytes = psutil.net_io_counters().bytes_recv
            log_val = {
                "time": time.time(),
                "level": self.log_level,
                "cpu_stat" : {
                    "cpu": psutil.cpu_percent(),
                    "memory": psutil.virtual_memory().percent,
                    "disk": psutil.disk_usage("/").percent,
                    "sent_bytes": cur_sent_bytes - self.prev_sent_bytes,
                    "rec_bytes":  cur_rec_bytes - self.prev_recv_bytes,
                }
            }
            
            self.prev_recv_bytes = cur_rec_bytes
            self.prev_sent_bytes = cur_sent_bytes
            # print(log_val)
            
            self.channel.basic_publish(exchange=self.exch, routing_key=self.log_level, body=json.dumps(log_val))
            # print(" [x] Sent %r:%r" % (self.log_level, log_val))
            time.sleep(self.interval)







