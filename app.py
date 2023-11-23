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
import traceback
import logging
import sqlite3
import io
import sys
#TBD:
#make tutorial
#test with father

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR) 

app = Flask(__name__)
app.config['DATABASE'] = os.path.join(app.root_path, 'database.db')

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db
def read_db(IP):
    db=get_db()
    cursor = db.execute('SELECT * FROM al')
    al=cursor.fetchall()
    dicti=[dict(row) for row in al]
    for dic in dicti:
        if dic["IP"]==IP:
            reun=[]
            reun.append(dic["URL"])
            reun.append("")
            reun.append("")
            reun.append(dic["FIRST_TIME"])
            reun.append(dic["DATA_RECEIVED"])
            reun.append(dic["DONE"])
            reun.append("")
            reun.append(dic["action_list"])
            reun.append(dic["DATA"])
            reun.append(dic["EMPTY"])
            reun.append(dic["RECEIVED"])
            reun.append(dic["IMAGE"])
            reun.append(dic['QUEUE'])
            return(reun)
    
with app.app_context():
    db = get_db()
    with app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))
    db.commit()

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.route('/api/status', methods=['POST'])
def getstatus():
    actionlst=request.data.decode('utf-8')
    actionlist=eval(eval(actionlst))
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("enable-automation")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    ur_l=actionlist[0]
    driver.get(ur_l)
    WebDriverWait(driver, 500).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
    time.sleep(1)
    for x in range(0,len(actionlist),2):
        if actionlist[x]=='T':
            elem = driver.switch_to.active_element
            if actionlist[x+1]!='BS':
                elem.send_keys(actionlist[x+1])
            else:
                elem.send_keys(Keys.BACKSPACE)
        if actionlist[x]=='C':
            WebDriverWait(driver, 500).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            time.sleep(1)
            actions = ActionChains(driver)
            body=driver.find_element(By.TAG_NAME, "body")
            actions.move_to_element(body)
            l=actionlist[x+1].split(',')
            actions.move_by_offset(l[0],l[1]).click() 
            actions.perform()
            WebDriverWait(driver, 500).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            time.sleep(1)
    if driver.current_url==ur_l:
        #check for upcoming assingments
        if ur_l=="https://teams.microsoft.com/_#/apps/66aeee93-507d-479a-a3ef-8f494af43945/sections/classroom":
            WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.XPATH, "//iframe[@title='Assignments Tab View']")))
            driver.switch_to.frame(driver.find_element(By.XPATH, "//iframe[@title='Assignments Tab View']"))
            time.sleep(5)
            days=[]
            try:
                days=driver.find_elements(By.CLASS_NAME, "date-group-label-shorthand__pjq0w")
            except:
                return("false")
            for day in days:
                if day.text=="Today" or day.text=="Tomorrow":
                    return("true")
            return("false")
    else:
        return("false")

@app.route('/api/setup', methods=['GET'])
def api_data():
    db=get_db()
    cursor = db.execute('SELECT * FROM al')
    al=cursor.fetchall()
    alist=[dict(row) for row in al]
    for dic in alist:
        if dic["IP"]==request.remote_addr:
            retun=dic["action_list"]
            curs=db.cursor()
            curs.execute('DELETE FROM al WHERE IP = ?', (request.remote_addr,))
            db.commit()
            return jsonify(retun)
    return jsonify("none")
@app.route('/')
def home():
    with app.app_context():
        db=get_db()
        curs=db.cursor()
        try:
            curs.execute('DELETE FROM al WHERE IP = ?', (request.remote_addr,))
            db.commit()
        except:
            donothing="nothing"
        done=False
        while not done:
            try:
                db.execute('INSERT INTO al (IP, URL, FIRST_TIME, DATA_RECEIVED, DONE, DATA, EMPTY, RECEIVED, action_list, QUEUE) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (request.remote_addr, "", "True", "False", "False", "[]", "False", "False", "[]", "[]"))
                db.commit()
                done=True
            except:
                nothing="nothing"
    return(render_template('usernamepassword.html'))
@app.route('/login')
def aiisdumb():
    #make other routes for other services
    with app.app_context():
        db=get_db()
        curs=db.cursor()
        curs.execute("UPDATE al SET URL = ? WHERE IP = ?", ("https://teams.microsoft.com/_#/apps/66aeee93-507d-479a-a3ef-8f494af43945/sections/classroom", request.remote_addr))
        db.commit()
    return render_template('aiisdumb.html')
@app.route('/ug')
def ug():
    return render_template("usergenerate.html")
@app.route('/upload')
def sendESP(action_list, IP):
    ie=read_db(IP)
    SCode=ie[6]
    with app.app_context():
        db=get_db()
        cursor=db.cursor()
        done=False
        while not done:
            try:
                cursor.execute("UPDATE al SET action_list = ? WHERE IP = ?", (str(action_list), IP))
                cursor.execute("UPDATE al SET DONE = ? WHERE IP = ?", ("True", IP))
                db.commit()
                done=True
            except:
                nothing="nothing"
        done=True
@app.route('/setting')
def servesetting():
    return send_file('images/setting.gif')
@app.route('/seleniuim')
def selenium(IP):
    with app.app_context():
        ie=read_db(IP)
    url=ie[0]
    action_list=[]
    action_list.append(url)
    options = Options()
    oldurl=" "
    xdim=0
    ydim=0
    x=0
    y=0
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("enable-automation")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    try:
        #load first page
        driver.get(url)
        driver.set_window_size(1000, 1000)
        actions = ActionChains(driver)
        while(driver.current_url==url):
            time.sleep(0.1)
        #runs when new page is loaded
        while(driver.current_url!=url):
            old_url=driver.current_url
            WebDriverWait(driver, 500).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))      
            rep=0
            data_received="False"
            with app.app_context():
                db=get_db()
                done=False
                while not done:
                    try:
                        cursor=db.cursor()
                        cursor.execute("UPDATE al SET DATA_RECEIVED = ? WHERE IP = ?", ("False", IP))
                        db.commit()
                        done=True
                    except:
                        nothing="nothing"
            #runs while page is being edited
            with app.app_context():
                while read_db(IP)[4]=="False" or read_db(IP)[8]=="[]":
                    #build the screen
                    img=driver.get_screenshot_as_png()
                    pil=Image.open(io.BytesIO(img))
                    pil=pil.resize((1000,1000))
                    buffer=io.BytesIO()
                    pil.save(buffer,format='PNG')
                    imgdata=buffer.getvalue()
                    with app.app_context():
                        db=get_db()
                        cursor=db.cursor()
                        done=False
                        while not done:
                            try:
                                cursor.execute("UPDATE al SET IMAGE = ? WHERE IP = ?", (imgdata, IP))
                                db.commit()
                                done=True
                            except:
                                nothing="nothing"
                    rep+=1
                    with app.app_context():
                        data_received=read_db(IP)[4]
                    if rep>20000:
                        break
                    if driver.current_url==url:
                        break
                    time.sleep(0.1)
            if driver.current_url==url:
                break
            if rep>20000:
                break 
            with app.app_context():
                datal=read_db(IP)[8]
            #FIX FOR REALLY WEIRD MOBILE BROWSER DATA LOSS BUG 
            #with app.app_context():
            #    while True:
            #        if read_db(IP)[9]=="False":
            #            if datal=="[]":
            #                datal=read_db(IP)[8]
            #            else:
            #                db=get_db()
            #                cursor=db.cursor()
            #                cursor.execute("UPDATE al SET RECEIVED = ? WHERE IP = ?", ("True", IP))
            #                db.commit()
            #                break
            #        else:
            #            db=get_db()
            #            cursor=db.cursor()
            #            cursor.execute("UPDATE al SET RECEIVED = ? WHERE IP = ?", ("True", IP))
            #            datal="[]"
            #            db.commit()
            #            break
            with app.app_context():
               # while(len(eval(read_db(IP)[8]))>0): 
                #deal with keys/clicks
                datal=read_db(IP)[8]
                action=eval(datal)
                try:
                    if eval(action[0])[0]=="type":
                        #test
                        #make sure that only letter keys are sent in JS
                        print("type")
                        elem = driver.switch_to.active_element
                        action_list.append("T")
                        if eval(action[0])[1]=="Backspace":
                            elem.send_keys(Keys.BACKSPACE)
                            action_list.append("BS")
                        else:
                            elem.send_keys(eval(action[0])[1])
                            action_list.append(eval(action[0])[1])
                    if eval(action[0])[0]=="click": 
                        print("received")
                        if oldurl!=driver.current_url:
                            old_url=driver.current_url
                            try:
                                body=driver.find_element(By.TAG_NAME, "body")
                                actions.move_to_element(body)
                                actions.move_by_offset(-1,0).click() 
                                actions.perform()
                                xdim=480
                            except:
                                xdim=960
                            try:
                                body=driver.find_element(By.TAG_NAME, "body")
                                actions.move_to_element(body)
                                actions.move_by_offset(0,-1).click() 
                                actions.perform()
                                ydim=430
                            except:
                                ydim=860
                            print("dimensions determined")
                        if xdim==480:
                            x=round(int(eval(action[0])[1])/1000*960-480)
                        if xdim==960:
                            x=round(int(eval(action[0])[1])/1000*960)
                        if ydim==430:
                            y=round(int(eval(action[0])[2])/1000*860-430)  
                        if ydim==860:
                            y=round(int(eval(action[0])[2])/1000*860)  
                        body=driver.find_element(By.TAG_NAME, "body")
                        actions.move_to_element(body)
                        actions.move_by_offset(x,y).click() 
                        actions.perform()
                        print("executed")
                        action_list.append("C")
                        action_list.append(str(x)+","+str(y))
                except:
                    nothing="nothing"
                with app.app_context():
                    db=get_db()
                    cursor=db.cursor()
                    done=False
                    olddata=eval(read_db(IP)[8])
                    print("before: ",eval(read_db(IP)[8]))
                    while True:
                        while not done:
                            try:
                                cursor.execute("UPDATE al SET DATA = ? WHERE IP = ?", (str(eval(read_db(IP)[8])[1:]), IP))
                                db.commit()
                                done=True
                            except:
                                nothing="nothing"
                        if(eval(read_db(IP)[8])!=olddata):
                            break
                    print("updated")
                    print("after: ",eval(read_db(IP)[8]))
        if driver.current_url==url:
            with app.app_context():
                sendESP(action_list, IP)
                db=get_db()
                cursor=db.cursor()
                done=False
                while not done:
                    try:
                        cursor.execute("UPDATE al SET DATA_RECEIVED = ? WHERE IP = ?", ("done", IP))
                        db.commit()
                        done=True
                    except:
                        nothing="nothing"
    except Exception as e:  
        line=traceback.extract_tb(e.__traceback__)[-1].lineno
        print(e,line)
#all this is still good for new method, just transferring data between two functions that need editing
@app.route('/receive', methods=['POST'])
def recieve():
    print("/receive ran")
    datal=request.get_json().get("message")
    if(read_db(request.remote_addr)[11]!=""):#image has loaded
        data_received=True
        db=get_db()
        ie=read_db(request.remote_addr)
        data=eval(read_db(request.remote_addr)[12])
        data.append(str(datal))
        #could restructure to put all received into a queue and just wait here to send the next thing using while eval(read[8])!=[]: time.sleep(0.1), then send the next thing and remove it from the queue, this should also improve framerate 
        cursor=db.cursor()
        done=False
        while not done:
            try:
                cursor.execute("UPDATE al SET QUEUE = ? WHERE IP = ?", (str(data), request.remote_addr))
                db.commit()
                done=True
            except:
                nothing="nothing"
        while(len(eval(read_db(request.remote_addr)[12]))>0):
            if(read_db(request.remote_addr)[4]=="False"):
                done=False
                while not done:
                    try:
                        cursor.execute("UPDATE al SET DATA = ? WHERE IP = ?", (str("["+str('"'+eval(read_db(request.remote_addr)[12])[0]+'"')+"]"), request.remote_addr))
                        db.commit()
                        done=True
                    except:
                        nothing="nothing"
                done=False
                while not done:
                    try:
                        cursor.execute("UPDATE al SET DATA_RECEIVED = ? WHERE IP = ?", ("True", request.remote_addr))
                        db.commit()
                        done=True
                    except:
                        nothing="nothing"
                done=False
                while not done:
                    try:
                        cursor.execute("UPDATE al SET QUEUE = ? WHERE IP = ?", (str(eval(read_db(request.remote_addr)[12])[1:]), request.remote_addr))
                        db.commit()
                        done=True
                    except:
                        nothing="nothing"
                #FIX FOR REALLY WEIRD MOBILE BROWSER DATA LOSS BUG 
         #       if data=="[]":
         #           cursor.execute("UPDATE al SET EMPTY = ? WHERE IP = ?", ("True", request.remote_addr))
         #       else:
         #           cursor.execute("UPDATE al SET EMPTY = ? WHERE IP = ?", ("False", request.remote_addr))
         #           while read_db(request.remote_addr)[10]=="False":
         #               cursor.execute("UPDATE al SET DATA = ? WHERE IP = ?", (str(data), request.remote_addr))
         #               db.commit()
          #              time.sleep(0.1)
          #      cursor.execute("UPDATE al SET RECEIVED = ? WHERE IP = ?", ("False", request.remote_addr))
          #      db.commit()
    return {'status': 'success'}
@app.route('/usergenerate')
def UserGenerate():
    ie=read_db(request.remote_addr)
    first_time=ie[3]
    done=ie[5]
    data_received=ie[4]
    image=ie[11]
    if done=="False":
        if first_time=="True":
            thread = threading.Thread(target=selenium, args=(request.remote_addr,))
            thread.start()
            first_time=False
            db=get_db()
            cursor=db.cursor()
            done=False
            while not done:
                try:
                    cursor.execute("UPDATE al SET FIRST_TIME = ? WHERE IP = ?", ("False", request.remote_addr))
                    db.commit()
                    done=True
                except:
                    nothing="nothing"
            return send_file('images/Loading.png', mimetype='image/png')
        if data_received=="done":
            return send_file('images/success.PNG', mimetype='image/png')
        try:
            if image!="":
                pill=Image.open(io.BytesIO(image))
                buffer=io.BytesIO()
                pill.save(buffer, format="PNG")
                buffer.seek(0)
                return send_file(buffer, mimetype='image/png')
            else:
                return send_file('images/Loading.png', mimetype='image/png')
        except:
            return send_file('images/Loading.png', mimetype='image/png')
    else:
       return send_file('images/success.PNG')      

if __name__ == '__main__':
    serve(app,host = '0.0.0.0',port = 5000)
    #app.run(host='0.0.0.0')
    #app.run(debug=True,host='0.0.0.0')
