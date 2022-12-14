import sys
import RPi.GPIO as GPIO
import time
from time import sleep

signalLEDpin = 5
GPIO.setmode(GPIO.BCM)
GPIO.setup(signalLEDpin,GPIO.OUT, initial=GPIO.LOW)

def ledFunction():
    GPIO.output(signalLEDpin,GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(signalLEDpin, GPIO.LOW)
    return
