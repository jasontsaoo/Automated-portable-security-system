import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
from time import sleep

broker = "broker.hivemq.com"
port = 1883
query = 60
QOS = 1

image = True

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
  print("Connected with result code "+str(rc))
  # Subscribing in on_connect() means that if we lose the connection and
  # reconnect then subscriptions will be renewed.
  client.subscribe("topiceecs149part2")
  
# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global image
    if image:
        f = open('receive1.jpg','wb')
    else:
        f = open('receive2.jpg','wb')
    image = not image        
    f.write(msg.payload)
    f.close()
    print ('image received')
  
def send_message():
    message = "Switch on"
    publish.single("topiceecs149part1", message, qos=QOS, hostname=broker)

def request_pi2():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker, port, query)
    client.loop_start()
    client.subscribe("topiceecs149part2")
    for i in range(3):
        print('Sending message ' + str(i))
        send_message()
        sleep(5)
    client.disconnect()
    client.loop_stop()
