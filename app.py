from selenium import webdriver
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from flask import Flask, request, render_template, send_file, g, jsonify
from ultralytics import YOLO
from PIL import Image
import random
from waitress import serve
import numpy as np
import threading
import tempfile
import time
import os   
import logging
import sqlite3
import io

#TBD:
#make tutorial
#test with father

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR) 

app = Flask(__name__)
app.config['DATABASE'] = os.path.join(app.root_path, 'database.db')

@app.route("/")
def home():
    return("hello")
       

if __name__ == '__main__':
    serve(app,host = '0.0.0.0',port = 5000)
    #app.run(host='0.0.0.0')
    #app.run(debug=True,host='0.0.0.0')
