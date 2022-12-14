from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2

import telegram
from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters
from keras.models import load_model
import keras

import os
import time
from time import sleep
import datetime

from image import *
from training import *
from game import *
from alarm import *
from LED import *

from client1 import request_pi2

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 25

# creating global variable for loop checker within startSecurity
CONTINUE_CHECKER=True

# chances to deactivate alarm before it rings
deactivate = 5

# Pi1 detected intruder
pi1_intruder = False

# main function called when '/start' is inputted
def startSecurity(update,context):
    with keras.backend.get_session().graph.as_default(): #reset keras graph with every start
        model = load_model("game-model.h5")
        global chat_id #utilising global version
        global CONTINUE_CHECKER #utilising global version
        global pi1_intruder #utilising global version
        captureCheck=False
        update.message.reply_text("Security ready!")
        
        #loop within main function to keep scanning each frame
        while CONTINUE_CHECKER:
            print('security active')
            captureCheck=False
            rawCapture1 = PiRGBArray(camera, size=(640, 480)) # grab the raw NumPy array representing the first image
            camera.capture(rawCapture1, format="bgr")
            frame1 = rawCapture1.array
            gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
            gray1 = cv2.GaussianBlur(gray1, (21, 21), 0)

            rawCapture2 = PiRGBArray(camera, size=(640, 480)) # grab the raw NumPy array representing the second image
            camera.capture(rawCapture2, format="bgr")
            frame2 = rawCapture2.array
            gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.GaussianBlur(gray2, (21, 21), 0)
            cv2.imwrite('photo_for_photo_function.jpg',frame2)
            
            #comparison between both frames to find difference
            deltaframe=cv2.absdiff(gray1,gray2) 
            threshold = cv2.threshold(deltaframe, 25, 255, cv2.THRESH_BINARY)[1]
            threshold = cv2.dilate(threshold,None)
            countour,heirarchy = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            print("no motion detected")
            i=0
            for j in countour:
                if cv2.contourArea(j) < 7000: #7000 can be changed to vary the sensitivity
                    continue #if difference not significant enough

                (x, y, w, h) = cv2.boundingRect(j)
                cv2.rectangle(frame2, (x, y), (x + w, y + h), (255, 0, 0), 2)
                captureCheck=True;
            
            if captureCheck: #if found, alarm activated but havent ring
                cv2.imwrite('frame.jpg',frame2) #saving image
                
                for i in range(deactivate): #chances to deactivate alarm before it rings
                    print("i is: ",i)
                    ledFunction()
                    test=gameFunction(camera,model)
                    print("gameFunction is: ",test)
                    if test==True:
                        print("gameFunction is verified")
                        update.message.reply_text('Successful deactivation of alarm by user, continuing security')
                        time.sleep(3)
                        break
                    elif test==False:
                        print("gameFunction not verified")
                    if i==deactivate-1: # no more chances, intruder found
                        update.message.reply_text('The motion sensor is triggered, high alert starting!')
                        context.bot.send_photo(chat_id=update.effective_chat.id,photo=open("frame.jpg","rb"))
                        buzzFunction1()
                        captureCheck=False;
                        pi1_intruder=True
                    time.sleep(0.5)
            elif pi1_intruder:
                update.message.reply_text('High alert has began, checking both pi for intruder')
                print('starting high alert')
                high_alert(update,context)

            key = cv2.waitKey(1) & 0xFF

            # clear the stream in preparation for the next frame
            rawCapture1.truncate(0)
            rawCapture2.truncate(0)

            # if the q key was pressed, break from the loop
            if key == ord("q"):
                break

def high_alert(update,context):
    while True:
            captureCheck=False
            print('checking pi 2')
            request_pi2()
            captureCheck=False
            #rawCapture1 = PiRGBArray(camera, size=(640, 480)) # grab the raw NumPy array representing the first image
            #camera.capture(rawCapture1, format="bgr")
            #frame1 = rawCapture1.array
            frame1 = cv2.imread("receive1.jpg")
            gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
            gray1 = cv2.GaussianBlur(gray1, (21, 21), 0)

            #rawCapture2 = PiRGBArray(camera, size=(640, 480)) # grab the raw NumPy array representing the second image
            #camera.capture(rawCapture2, format="bgr")
            #frame2 = rawCapture2.array
            frame2 = cv2.imread("receive2.jpg")
            gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.GaussianBlur(gray2, (21, 21), 0)
            cv2.imwrite('photo_for_photo_function.jpg',frame2)

            #comparison between both frames to find difference
            deltaframe=cv2.absdiff(gray1,gray2) 
            threshold = cv2.threshold(deltaframe, 25, 255, cv2.THRESH_BINARY)[1]
            threshold = cv2.dilate(threshold,None)
            countour,heirarchy = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            i=0
            for j in countour:
                if cv2.contourArea(j) < 7000: #7000 can be changed to vary the sensitivity
                    continue #if difference not significant enough

                (x, y, w, h) = cv2.boundingRect(j)
                cv2.rectangle(frame2, (x, y), (x + w, y + h), (255, 0, 0), 2)
                captureCheck=True;

            if captureCheck: #if found, alarm activated but havent ring
                cv2.imwrite('frame.jpg',frame2) #saving image
                buzzFunction1()
                update.message.reply_text('The motion sensor for 2nd pi is triggered!')
                print('The motion sensor for 2nd pi is triggered!')
                context.bot.send_photo(chat_id=update.effective_chat.id,photo=open("frame.jpg","rb"))
            
            print('checking pi 1')
            rawCapture1 = PiRGBArray(camera, size=(640, 480)) # grab the raw NumPy array representing the first image
            camera.capture(rawCapture1, format="bgr")
            frame1 = rawCapture1.array
            gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
            gray1 = cv2.GaussianBlur(gray1, (21, 21), 0)
            time.sleep(1)
            rawCapture2 = PiRGBArray(camera, size=(640, 480)) # grab the raw NumPy array representing the second image
            camera.capture(rawCapture2, format="bgr")
            frame2 = rawCapture2.array
            gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.GaussianBlur(gray2, (21, 21), 0)
            cv2.imwrite('photo_for_photo_function.jpg',frame2)
            
            #comparison between both frames to find difference
            deltaframe=cv2.absdiff(gray1,gray2) 
            threshold = cv2.threshold(deltaframe, 25, 255, cv2.THRESH_BINARY)[1]
            threshold = cv2.dilate(threshold,None)
            countour,heirarchy = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            i=0
            for j in countour:
                if cv2.contourArea(j) < 7000: #7000 can be changed to vary the sensitivity
                    continue #if difference not significant enough

                (x, y, w, h) = cv2.boundingRect(j)
                cv2.rectangle(frame2, (x, y), (x + w, y + h), (255, 0, 0), 2)
                captureCheck=True;
            
            if captureCheck: #if found, alarm activated but havent ring
                cv2.imwrite('frame.jpg',frame2) #saving image
                buzzFunction1()
                update.message.reply_text('The motion sensor for 1st pi is triggered!')
                print('The motion sensor for 1st pi is triggered!')
                context.bot.send_photo(chat_id=update.effective_chat.id,photo=open("frame.jpg","rb"))
            
            
updater = Updater("5721555744:AAGpA-DJt1kBkdO10KcZVX3KMvua2U2I8Nk",use_context=True)

def start(update: Update, context: CallbackContext):
    update.message.reply_text("start selected, setting up security please wait...")
    global CONTINUE_CHECKER
    CONTINUE_CHECKER=True
    startSecurity(update,context)

def end(update: Update, context: CallbackContext):
    update.message.reply_text("end selected, security deactivated")
    global CONTINUE_CHECKER
    CONTINUE_CHECKER=False
    
def photo(update: Update, context: CallbackContext):
    context.bot.send_photo(chat_id=update.effective_chat.id,photo=open("photo_for_photo_function.jpg","rb"))
    
def help(update: Update, context: CallbackContext):
    update.message.reply_text("help selected")
    update.message.reply_text(
    '''
    -input '/start' to start security

-input '/end' to stop security

-input '/photo' to send a real time picture
    
-input '/train' to start data collection and training
    '''
    )

def train(update: Update, context: CallbackContext):
    update.message.reply_text("train selected")
    update.message.reply_text("Put out ur secret hand gesture for data collection")
    update.message.reply_text("3")
    time.sleep(1)
    update.message.reply_text("2")
    time.sleep(1)
    update.message.reply_text("1")
    time.sleep(1)
    update.message.reply_text("Hold hand gesture")
    dataCollection(camera,'v')
    update.message.reply_text("remove secret hand gesture for data collection")
    update.message.reply_text("3")
    time.sleep(1)
    update.message.reply_text("2")
    time.sleep(1)
    update.message.reply_text("1")
    time.sleep(1)
    update.message.reply_text("Hold")
    dataCollection(camera,'n')
    update.message.reply_text("Done with data collection, starting model training")
    modelTraining()
    update.message.reply_text("Done with model training, security ready to start")

def unknown(update: Update, context: CallbackContext):
    update.message.reply_text("Sorry '%s' is not a valid command, input '/help' to find out the commands" % update.message.text)

def unknown_text(update: Update, context: CallbackContext):
    update.message.reply_text("Sorry I can't recognize you , you said '%s', input '/help' to find out the commands" % update.message.text)

updater.dispatcher.add_handler(CommandHandler('start', start,filters=None, allow_edited=None, pass_args=False, pass_update_queue=False, pass_job_queue=False, pass_user_data=False, pass_chat_data=False, run_async=True)) #run_async=True allowing multithreading so programme can still receive telegram inputs from users while running other programmes, needed for example to stop security
updater.dispatcher.add_handler(CommandHandler('end', end))
updater.dispatcher.add_handler(CommandHandler('photo', photo,filters=None, allow_edited=None, pass_args=False, pass_update_queue=False, pass_job_queue=False, pass_user_data=False, pass_chat_data=False, run_async=True))
updater.dispatcher.add_handler(CommandHandler('train', train))
updater.dispatcher.add_handler(CommandHandler('help', help))
updater.dispatcher.add_handler(MessageHandler(Filters.text, unknown))
updater.dispatcher.add_handler(MessageHandler(Filters.command, unknown)) # Filters out unknown commands

# Filters out unknown messages.
updater.dispatcher.add_handler(MessageHandler(Filters.text, unknown_text))

updater.start_polling(0)
updater.idle()
