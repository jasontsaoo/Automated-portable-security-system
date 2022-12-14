from picamera import PiCamera
camera = PiCamera()
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
  print("Connected with result code "+str(rc))
  # Subscribing in on_connect() means that if we lose the connection and
  # reconnect then subscriptions will be renewed.
  client.subscribe("topiceecs149part1")
  
# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
  print ('msg received')
  camera.capture("2nd_pi's_camera_picture.jpg")
  f= open("2nd_pi's_camera_picture.jpg","rb")
  filecontent = f.read()
  byteArr = bytearray(filecontent)
  publish.single('topiceecs149part2', byteArr, qos=1, hostname='broker.hivemq.com')
  
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("broker.hivemq.com", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()








