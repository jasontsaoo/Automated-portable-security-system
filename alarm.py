import sys
import RPi.GPIO as GPIO
import time
from time import sleep

def buzzFunction1():
    signalBUZZERpin = 12
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(signalBUZZERpin,GPIO.OUT)
    buzzer = GPIO.PWM(signalBUZZERpin, 1000) # Set frequency to 1 Khz
    buzzer.start(10) # Set dutycycle to 10
    time.sleep(0.5)
    return
