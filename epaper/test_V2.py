#!/usr/bin/python3
# -*- coding:utf-8 -*-

# by TM, based on epd_2in7_test.py by Waveshare
# Python3
# sudo apt-get install python3-pip python-imaging
# sudo apt-get install libopenjp2-7
# pip3 install spidev 
# pip3 install RPi.GPIO 
# pip3 install Pillow
#
# sudo raspi-config: enable SPI 
#
# see https://www.waveshare.com/wiki/2.7inch_e-Paper_HAT

import sys
import os
# TM 
# picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
# libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pic')
libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import random
import logging
from waveshare_epd import epd2in7
import time
from PIL  import Image,ImageDraw,ImageFont
import traceback

logging.basicConfig(level=logging.DEBUG)

try:
    logging.info("TM 1")   
    epd = epd2in7.EPD()
    font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
    # font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
    # font35 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 35)
    
    # '''2Gray(Black and white) display'''
    # logging.info("init and Clear")
    epd.init()
    # epd.Clear(0xFF)

    # Drawing on the Horizontal image
    logging.info("1.Drawing on the Horizontal image...")
    Himage = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(Himage)
    draw.text((10, random.randint(0,40)), 'hello world', font = font24, fill = 0)
    # draw.text((150, 0), u'微雪电子', font = font24, fill = 0)    
    # draw.line((20, 50, 70, 100), fill = 0)
    # draw.line((70, 50, 20, 100), fill = 0)
    # draw.rectangle((20, 50, 70, 100), outline = 0)
    # draw.line((165, 50, 165, 100), fill = 0)
    # draw.line((140, 75, 190, 75), fill = 0)
    # draw.arc((140, 50, 190, 100), 0, 360, fill = 0)
    # draw.rectangle((80, 50, 130, 100), fill = 0)
    # draw.chord((200, 50, 250, 100), 0, 360, fill = 0)
    epd.display(epd.getbuffer(Himage))
    time.sleep(2)

    Himage = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(Himage)
    draw.text((10, random.randint(0,40)), 'hello world 2', font = font24, fill = 0)
    epd.display(epd.getbuffer(Himage))
    time.sleep(2)

    Himage = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(Himage)
    draw.text((10, random.randint(0,40)), 'hello world 3', font = font24, fill = 0)
    epd.display(epd.getbuffer(Himage))
    time.sleep(2)


    Himage = Image.open(os.path.join(picdir, '2in7_Scale.bmp'))
    epd.display_4Gray(epd.getbuffer_4Gray(Himage))
    time.sleep(2)
    
    # logging.info("Clear...")
    # epd.Clear(0xFF)
    logging.info("Goto Sleep...")
    epd.sleep()

    epd.Dev_exit()
        
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd2in7.epdconfig.module_exit()
    exit()
