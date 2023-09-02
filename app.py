from selenium import webdriver
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from flask import Flask, request, render_template, send_file, g, jsonify, Response
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

app = Flask(__name__)
app.config['DATABASE'] = os.path.join(app.root_path, 'database.db')

@app.route("/")
def takeimage():
    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("enable-automation")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(options=options)
        driver.get("https://accounts.google.com/v3/signin/identifier?continue=https%3A%2F%2Fclassroom.google.com&ifkv=AXo7B7VpDVNUhWg6wv5Mw-Zbzokwt8PRHv2zxZu-Nemyenda1bOnUpypa6_wbRu6DQo7TFMRkGo4Sw&passive=true&flowName=GlifWebSignIn&flowEntry=ServiceLogin&dsh=S-670368851%3A1693667962802672&theme=glif")
        time.sleep(5)
        img=driver.get_screenshot_as_png()
        image=Image.open(io.BytesIO(img))
        img_bytes_io = io.BytesIO()
        image.save(img_bytes_io, format='PNG')

        # Set the content type and send the image as a response
        response = Response(img_bytes_io.getvalue())
        response.headers['Content-Type'] = 'image/png'
        return response
    except Exception as e:
        return(str(e))

if __name__ == '__main__':
    serve(app,host = '0.0.0.0',port = 5000)
    #app.run(host='0.0.0.0')
    #app.run(debug=True,host='0.0.0.0')
