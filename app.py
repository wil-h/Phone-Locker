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
            reun.append(dic["USERNAME"])
            reun.append(dic["PASSWORD"])
            reun.append(dic["FIRST_TIME"])
            reun.append(dic["DATA_RECEIVED"])
            reun.append(dic["DONE"])
            reun.append(dic["SCode"])
            reun.append(dic["action_list"])
            reun.append(dic["DATA"])
            reun.append(dic["EMPTY"])
            reun.append(dic["RECEIVED"])
            reun.append(dic["IMAGE"])
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
    try:
        actionlst=request.data.decode('utf-8')
        actionlist=eval(eval(actionlst))
        uname=actionlist[0]
        pword=actionlist[1]
        ur_l=actionlist[2]
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("enable-automation")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(options=options)
        driver.get(ur_l)
        idlist=[]
        noidpage=False
        for id in actionlist:
            if id!=uname and id!=pword and id!=ur_l and id!='username' and id!='password' and id!='submit' and id!='return' and id!='wait':
                idlist.append(id)
        while driver.current_url==ur_l:
            time.sleep(0.1)
        for action in range(3,len(actionlist)-1):
            WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.TAG_NAME, 'body'))) 
            if actionlist[action]!=uname and actionlist[action]!=pword and actionlist[action]!=ur_l:
                #ignore everything until the next page when a page has an element with no ID
                if not noidpage:
                    if actionlist[action]=='username':
                        id=actionlist[action+1]
                        WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.ID, id))) 
                        element=driver.find_element(By.ID, id)
                        element.send_keys(uname)
                        idlist.remove(id)
                    if actionlist[action]=='password':
                        id=actionlist[action+1]
                        WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.ID, id))) 
                        element=driver.find_element(By.ID, id)
                        element.send_keys(pword)
                        idlist.remove(id)
                    if actionlist[action]=='submit':
                        id=actionlist[action+1]
                        WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.ID, id))) 
                        element=driver.find_element(By.ID, id)
                        element.click()
                        idlist.remove(id)
                    if actionlist[action]=='return':
                        driver.switch_to.active_element.send_keys(Keys.RETURN)
                    if actionlist[action]=='noid':
                        noidpage=True
                        oldurl=driver.current_url
                        coordinates=eval(actionlist[action+1])
                        while driver.current_url==oldurl:
                            yvalues = []
                            xvalues=[]
                            ids=[]
                            submit=[]
                            for g in range(0,len(coordinates)):
                                if coordinates[g]=='username' or coordinates[g]=='password' or coordinates[g]=='submit' or coordinates[g]=='none':
                                    ids.append(coordinates[g])
                                    xvalues.append(coordinates[(g+1)])
                                    yvalues.append(coordinates[(g+2)])
                            y1=[]
                            y2=[]
                            y3=[]
                            y4=[]
                            y5=[]
                            accounted=[]
                            rep=1
                            done=False
                            if len(coordinates)>0:
                                while(not done):
                                    if rep==1:
                                        y1.append(yvalues.index(min(yvalues)))
                                    if rep==2:
                                        y2.append(yvalues.index(min(yvalues)))
                                    if rep==3:
                                        y3.append(yvalues.index(min(yvalues)))
                                    if rep==4:
                                        y4.append(yvalues.index(min(yvalues)))
                                    if rep==5:
                                        y5.append(yvalues.index(min(yvalues)))
                                    accounted.append(yvalues.index(min(yvalues)))
                                    for j in range(0,len(ids)):
                                        if (yvalues[j]-25)<min(yvalues) and j!=int(yvalues.index(min(yvalues))):
                                            if j not in y1 and j not in y2 and j not in y3 and j not in y4 and j not in y5:
                                                if rep==1:
                                                    y1.append(j)
                                                if rep==2:
                                                    y2.append(j)
                                                if rep==3:
                                                    y3.append(j)
                                                if rep==4:
                                                    y4.append(j)
                                                if rep==5:
                                                    y5.append(j)
                                                accounted.append(j)
                                                yvalues[j]=max(yvalues)+10
                                    if len(accounted)==len(yvalues):
                                        done=True 
                                    rep=rep+1
                                    yvalues[yvalues.index(min(yvalues))]=max(yvalues)+10
                                x1=[]
                                x2=[]
                                x3=[]
                                x4=[]
                                x5=[]
                                accounted=[]
                                rep=1
                                done=False
                                while(not done):
                                    if rep==1:
                                        x1.append(xvalues.index(min(xvalues)))
                                    if rep==2:
                                        x2.append(xvalues.index(min(xvalues)))
                                    if rep==3:
                                        x3.append(xvalues.index(min(xvalues)))
                                    if rep==4:
                                        x4.append(xvalues.index(min(xvalues)))
                                    if rep==5:
                                        x5.append(xvalues.index(min(xvalues)))
                                    accounted.append(xvalues.index(min(xvalues)))
                                    for j in range(0,len(ids)):
                                        if (xvalues[j]-25)<min(xvalues) and xvalues[j]!=min(xvalues):
                                            if j not in x1 and j not in x2 and j not in x3 and j not in x4 and j not in x5:
                                                if rep==1:
                                                    x1.append(j)
                                                if rep==2:
                                                    x2.append(j)
                                                if rep==3:
                                                    x3.append(j)
                                                if rep==4:
                                                    x4.append(j)
                                                if rep==5:
                                                    x5.append(j)
                                                accounted.append(j)
                                                xvalues[j]=max(xvalues)+10
                                    if len(accounted)==len(xvalues):
                                        done=True 
                                    rep=rep+1
                                    xvalues[xvalues.index(min(xvalues))]=max(xvalues)+10
                                if y2==[]:
                                    y=1
                                elif y3==[]:
                                    y=2
                                elif y4==[]:
                                    y=3
                                elif y5==[]:
                                    y=4
                                elif y5!=[]:
                                    y=5
                                if x2==[]:
                                    x=1
                                elif x3==[]:
                                    x=2
                                elif x4==[]:
                                    x=3
                                elif x5==[]:
                                    x=4
                                elif x5!=[]:
                                    x=5
                                element_matrix = np.empty((y, x), dtype=np.dtype('U100'))
                                for o in range(0,len(ids)):
                                    if o in x1:
                                        xcoord=0
                                    if o in x2:
                                        xcoord=1
                                    if o in x3:
                                        xcoord=2
                                    if o in x4:
                                        xcoord=3
                                    if o in x5:
                                        xcoord=4
                                    if o in y1:
                                        ycoord=0
                                    if o in y2:
                                        ycoord=1
                                    if o in y3:
                                        ycoord=2
                                    if o in y4:
                                        ycoord=3  
                                    if o in y5:
                                        ycoord=4
                                    element_matrix[ycoord,xcoord]=ids[o]
                                letters=['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
                                elements = driver.find_elements(By.XPATH,"//*")
                                ids = []
                                yvalues=[]
                                xvalues=[]
                                for element in elements:
                                    element_id = element.get_attribute("id")
                                    tag = element.tag_name
                                    location = element.location
                                    size = element.size
                                    if (tag!="" and tag != "a" and tag != "abbr" and tag != "address" and tag != "article" and tag != "aside" and
                                        tag != "audio" and tag != "b" and tag != "blockquote" and tag != "body" and tag != "canvas" and
                                        tag != "caption" and tag != "cite" and tag != "code" and tag != "col" and tag != "colgroup" and
                                        tag != "datalist" and tag != "dd" and tag != "del" and tag != "details" and tag != "dfn" and
                                        tag != "dialog" and tag != "div" and tag != "dl" and tag != "dt" and tag != "em" and tag != "embed" and
                                        tag != "fieldset" and tag != "figcaption" and tag != "figure" and tag != "footer" and tag != "form" and
                                        tag != "head" and tag != "header" and tag != "html" and tag != "i" and tag != "iframe" and tag != "img" and
                                        tag != "ins" and tag != "kbd" and tag != "label" and tag != "legend" and tag != "link" and tag != "main" and
                                        tag != "map" and tag != "mark" and tag != "menu" and tag != "meta" and tag != "meter" and tag != "nav" and
                                        tag != "noscript" and tag != "object" and tag != "ol" and tag != "optgroup" and tag != "option" and
                                        tag != "output" and tag != "p" and tag != "param" and tag != "pre" and tag != "progress" and tag != "q" and
                                        tag != "rp" and tag != "rt" and tag != "ruby" and tag != "s" and tag != "samp" and tag != "script" and
                                        tag != "section" and tag != "select" and tag != "small" and tag != "source" and tag != "span" and
                                        tag != "strong" and tag != "style" and tag != "sub" and tag != "summary" and tag != "sup" and
                                        tag != "svg" and tag != "table" and tag != "tbody" and tag != "template" and tag != "time" and
                                        tag != "title" and tag != "tr" and tag != "track" and tag != "u" and tag != "ul" and tag != "var" and
                                        tag != "video" and tag != "wbr" and tag!="h1" and tag!="h2" and tag!="h3" and tag!="h4" and tag!="h5" 
                                        and tag!="h6"):
                                        if(size["height"]>0 and size["width"]>0 and "hidden" not in element.get_attribute("style").lower() and
                                            "display: none" not in element.get_attribute("style").lower() and
                                            "visibility: hidden" not in element.get_attribute("style").lower() and
                                            element.get_attribute("aria-hidden") != "true" and
                                            element.get_attribute("hidden") is None and
                                            element.is_displayed()):
                                            if element_id=="":
                                                element_id=random.choice(letters)+random.choice(letters)+random.choice(letters)+random.choice(letters)
                                                driver.execute_script("arguments[0].setAttribute('id', arguments[1]);", element, element_id)
                                            ids.append(element_id)
                                            xvalues.append(location["x"])
                                            yvalues.append(location["y"])
                                y1=[]
                                y2=[]
                                y3=[]
                                y4=[]
                                y5=[]
                                accounted=[]
                                rep=1
                                done=False
                                while(not done):
                                    if rep==1:
                                        y1.append(yvalues.index(min(yvalues)))
                                    if rep==2:
                                        y2.append(yvalues.index(min(yvalues)))
                                    if rep==3:
                                        y3.append(yvalues.index(min(yvalues)))
                                    if rep==4:
                                        y4.append(yvalues.index(min(yvalues)))
                                    if rep==5:
                                        y5.append(yvalues.index(min(yvalues)))
                                    accounted.append(yvalues.index(min(yvalues)))
                                    for j in range(0,len(ids)):
                                        if (yvalues[j]-25)<min(yvalues) and j!=int(yvalues.index(min(yvalues))):
                                            if j not in y1 and j not in y2 and j not in y3 and j not in y4 and j not in y5:
                                                if rep==1:
                                                    y1.append(j)
                                                if rep==2:
                                                    y2.append(j)
                                                if rep==3:
                                                    y3.append(j)
                                                if rep==4:
                                                    y4.append(j)
                                                if rep==5:
                                                    y5.append(j)
                                                accounted.append(j)
                                                yvalues[j]=max(yvalues)+10
                                    if len(accounted)==len(yvalues):
                                        done=True 
                                    rep=rep+1
                                    yvalues[yvalues.index(min(yvalues))]=max(yvalues)+10
                                x1=[]
                                x2=[]
                                x3=[]
                                x4=[]
                                x5=[]
                                accounted=[]
                                rep=1
                                done=False
                                while(not done):
                                    if rep==1:
                                        x1.append(xvalues.index(min(xvalues)))
                                    if rep==2:
                                        x2.append(xvalues.index(min(xvalues)))
                                    if rep==3:
                                        x3.append(xvalues.index(min(xvalues)))
                                    if rep==4:
                                        x4.append(xvalues.index(min(xvalues)))
                                    if rep==5:
                                        x5.append(xvalues.index(min(xvalues)))
                                    accounted.append(xvalues.index(min(xvalues)))
                                    for j in range(0,len(ids)):
                                        if (xvalues[j]-40)<min(xvalues) and j!=int(xvalues.index(min(xvalues))):
                                            if j not in x1 and j not in x2 and j not in x3 and j not in x4 and j not in x5:
                                                if rep==1:
                                                    x1.append(j)
                                                if rep==2:
                                                    x2.append(j)
                                                if rep==3:
                                                    x3.append(j)
                                                if rep==4:
                                                    x4.append(j)
                                                if rep==5:
                                                    x5.append(j)
                                                accounted.append(j)
                                                xvalues[j]=max(xvalues)+10
                                    if len(accounted)==len(xvalues):
                                        done=True 
                                    rep=rep+1
                                    xvalues[xvalues.index(min(xvalues))]=max(xvalues)+10
                                if y2==[]:
                                    y=1
                                elif y3==[]:
                                    y=2
                                elif y4==[]:
                                    y=3
                                elif y5==[]:
                                    y=4
                                elif y5!=[]:
                                    y=5
                                if x2==[]:
                                    x=1
                                elif x3==[]:
                                    x=2
                                elif x4==[]:
                                    x=3
                                elif x5==[]:
                                    x=4
                                elif x5!=[]:
                                    x=5
                                id_matrix = np.empty((y, x), dtype=np.dtype('U100'))
                                for o in range(0,len(ids)):
                                    if o in x1:
                                        xcoord=0
                                    if o in x2:
                                        xcoord=1
                                    if o in x3:
                                        xcoord=2
                                    if o in x4:
                                        xcoord=3
                                    if o in x5:
                                        xcoord=4
                                    if o in y1:
                                        ycoord=0
                                    if o in y2:
                                        ycoord=1
                                    if o in y3:
                                        ycoord=2
                                    if o in y4:
                                        ycoord=3
                                    if o in y5:
                                        ycoord=4
                                    id_matrix[ycoord,xcoord]=ids[o]
                                submit=[]
                                irows,icolumns=id_matrix.shape
                                erows,ecolumns=element_matrix.shape
                                if irows>erows:
                                    rows=erows
                                if irows<erows or irows==erows:
                                    rows=irows
                                if icolumns>ecolumns:
                                    columns=ecolumns
                                if icolumns<ecolumns or icolumns==ecolumns:
                                    columns=icolumns
                                for row in range(0, rows):
                                    for column in range(0,columns):
                                        if id_matrix[row,column]!='':
                                            if element_matrix[row,column]=='submit':
                                                submit.append(row)
                                                submit.append(column)
                                            else:
                                                if element_matrix[row,column]=='username':
                                                    element=driver.find_element(By.ID,id_matrix[row,column])
                                                    for j in range(0,100):
                                                        element.send_keys(Keys.BACKSPACE)
                                                    element.send_keys(uname)
                                                if element_matrix[row,column]=='password':
                                                    element=driver.find_element(By.ID,id_matrix[row,column])
                                                    for j in range(0,100):
                                                        element.send_keys(Keys.BACKSPACE)
                                                    element.send_keys(pword)
                            if len(submit)>0:
                                driver.find_element(By.ID,id_matrix[submit[0],submit[1]]).click()
                            else:
                                driver.switch_to.active_element.send_keys(Keys.RETURN)
                            WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
                            time.sleep(1)
                if actionlist[action]=='wait':
                    noidpage=False
                    WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.TAG_NAME, 'body'))) 
                    hasid=False
                    for v in range(action, len(actionlist)-1):
                        if actionlist[v]=='wait':
                            hasid=False
                            break
                        if actionlist[v]=='username' or actionlist[v]=='password' or actionlist[v]=='submit':
                            hasid=True
                            break
                    if hasid:
                        try:
                            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, idlist[0])))
                        except:
                            time.sleep(5)
                    else:
                        time.sleep(5)
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
                    return jsonify("false")
                for day in days:
                    if day.text=="Today" or day.text=="Tomorrow":
                        return jsonify("true")
                return jsonify("false")
        else:
            return jsonify("false")
    except Exception as e:
        return(e)
    #TEST THIS ONCE TEACHERS START ASSIGNING STUFF FOR SCHOOL!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@app.route('/api/setup', methods=['GET'])
def api_data():
    db=get_db()
    try:
        ie=read_db(request.remote_addr)
        SCode=ie[6]
        cursor = db.execute('SELECT * FROM al')
        al=cursor.fetchall()
        alist=[dict(row) for row in al]
        for dic in alist:
            if dic["SCode"]==SCode:
                retun=dic["action_list"]
                if retun!="[]":
                    curs=db.cursor()
                    curs.execute('DELETE FROM al WHERE SCode = ?', (SCode,))
                    db.commit()
                    return jsonify(retun)
        return jsonify("none")
    except:
        return jsonify("none")
@app.route('/')
def home():
    return(render_template('usernamepassword.html'))
@app.route('/error')
def aiisdumb():
    return render_template('usergenerate.html')
@app.route('/draw')
def servedraw():
    return send_file('images/draw.PNG')
@app.route('/delete')
def servedelete():
    return send_file('images/delete.PNG')
@app.route('/submit')
def servesubmit():
    return send_file('images/submit.PNG')
@app.route('/expanded')
def serveexpanded():
    return send_file('images/expanded.PNG')
@app.route('/username')
def serveusername():
    return send_file('images/username.PNG')
@app.route('/password')
def servepassword():
    return send_file('images/password.PNG')
@app.route('/button')
def servebutton():
    return send_file('images/button.PNG')
@app.route('/none')
def servenone():
    return send_file('images/none.PNG')
@app.route('/upload')
def sendESP(action_list, IP):
    ie=read_db(IP)
    SCode=ie[6]
    with app.app_context():
        db=get_db()
        cursor=db.cursor()
        cursor.execute("UPDATE al SET action_list = ? WHERE IP = ?", (str(action_list), IP))
        cursor.execute("UPDATE al SET DONE = ? WHERE IP = ?", ("True", IP))
        db.commit()
        done=True
@app.route('/setting')
def servesetting():
    return send_file('images/setting.gif')
@app.route('/seleniuim')
def selenium(IP):
    with app.app_context():
        ie=read_db(IP)
    url=ie[0]
    username=ie[1]
    password=ie[2]
    action_list=[]
    action_list.append(username)
    action_list.append(password)
    action_list.append(url)
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("enable-automation")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    try:
        #load first page
        driver.get(url)
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
                cursor=db.cursor()
                cursor.execute("UPDATE al SET DATA_RECEIVED = ? WHERE IP = ?", ("False", IP))
                db.commit()
            #runs while page is being edited
            while data_received=="False":
                #build the screen
                #with tempfile.NamedTemporaryFile(suffix='.PNG', delete=False) as temp_file:
                img=driver.get_screenshot_as_png()
                pil=Image.open(io.BytesIO(img))
                pil=pil.resize((1000,1000))
                buffer=io.BytesIO()
                pil.save(buffer,format='PNG')
                imgdata=buffer.getvalue()
                with app.app_context():
                    db=get_db()
                    cursor=db.cursor()
                    cursor.execute("UPDATE al SET IMAGE = ? WHERE IP = ?", (imgdata, IP))
                    db.commit()
                rep+=1
                with app.app_context():
                    data_received=read_db(IP)[4]
                if rep>20000:
                    break
                if driver.current_url==url:
                    break
                time.sleep(0.1)
            #clear image cache
            time.sleep(5)
            if rep>20000:
                break 
            with app.app_context():
                datal=read_db(IP)[8]
            #FIX FOR REALLY WEIRD MOBILE BROWSER DATA LOSS BUG 
            with app.app_context():
                while True:
                    if read_db(IP)[9]=="False":
                        if datal=="[]":
                            datal=read_db(IP)[8]
                        else:
                            db=get_db()
                            cursor=db.cursor()
                            cursor.execute("UPDATE al SET RECEIVED = ? WHERE IP = ?", ("True", IP))
                            db.commit()
                            break
                    else:
                        db=get_db()
                        cursor=db.cursor()
                        cursor.execute("UPDATE al SET RECEIVED = ? WHERE IP = ?", ("True", IP))
                        datal="[]"
                        db.commit()
                        break
            coordinates=eval(datal)
            for ghf in range(0, len(coordinates)):
                if coordinates[ghf]=="button":
                    coordinates[ghf]="submit"
            yvalues = []
            xvalues=[]
            ids=[]
            submit=[]
            for g in range(0,len(coordinates)):
                if coordinates[g]=='username' or coordinates[g]=='password' or coordinates[g]=='submit' or coordinates[g]=='none':
                    ids.append(coordinates[g])
                    xvalues.append(coordinates[(g+1)])
                    yvalues.append(coordinates[(g+2)])
            y1=[]
            y2=[]
            y3=[]
            y4=[]
            y5=[]
            accounted=[]
            rep=1
            done=False
            if len(coordinates)>0:
                while(not done):
                    if rep==1:
                        y1.append(yvalues.index(min(yvalues)))
                    if rep==2:
                        y2.append(yvalues.index(min(yvalues)))
                    if rep==3:
                        y3.append(yvalues.index(min(yvalues)))
                    if rep==4:
                        y4.append(yvalues.index(min(yvalues)))
                    if rep==5:
                        y5.append(yvalues.index(min(yvalues)))
                    accounted.append(yvalues.index(min(yvalues)))
                    for j in range(0,len(ids)):
                        if (yvalues[j]-25)<min(yvalues) and j!=int(yvalues.index(min(yvalues))):
                            if j not in y1 and j not in y2 and j not in y3 and j not in y4 and j not in y5:
                                if rep==1:
                                    y1.append(j)
                                if rep==2:
                                    y2.append(j)
                                if rep==3:
                                    y3.append(j)
                                if rep==4:
                                    y4.append(j)
                                if rep==5:
                                    y5.append(j)
                                accounted.append(j)
                                yvalues[j]=max(yvalues)+10
                    if len(accounted)==len(yvalues):
                        done=True 
                    rep=rep+1
                    #removing this would shift the indexes
                    yvalues[yvalues.index(min(yvalues))]=max(yvalues)+10

                #x coords
                x1=[]
                x2=[]
                x3=[]
                x4=[]
                x5=[]
                accounted=[]
                rep=1
                done=False
                while(not done):
                    if rep==1:
                        x1.append(xvalues.index(min(xvalues)))
                    if rep==2:
                        x2.append(xvalues.index(min(xvalues)))
                    if rep==3:
                        x3.append(xvalues.index(min(xvalues)))
                    if rep==4:
                        x4.append(xvalues.index(min(xvalues)))
                    if rep==5:
                        x5.append(xvalues.index(min(xvalues)))
                    accounted.append(xvalues.index(min(xvalues)))
                    for j in range(0,len(ids)):
                        if (xvalues[j]-25)<min(xvalues) and xvalues[j]!=min(xvalues):
                            if j not in x1 and j not in x2 and j not in x3 and j not in x4 and j not in x5:
                                if rep==1:
                                    x1.append(j)
                                if rep==2:
                                    x2.append(j)
                                if rep==3:
                                    x3.append(j)
                                if rep==4:
                                    x4.append(j)
                                if rep==5:
                                    x5.append(j)
                                accounted.append(j)
                                xvalues[j]=max(xvalues)+10
                    if len(accounted)==len(xvalues):
                        done=True 
                    rep=rep+1
                    #removing this would shift the indexes
                    xvalues[xvalues.index(min(xvalues))]=max(xvalues)+10
                #form the matrix
                if y2==[]:
                    y=1
                elif y3==[]:
                    y=2
                elif y4==[]:
                    y=3
                elif y5==[]:
                    y=4
                elif y5!=[]:
                    y=5
                if x2==[]:
                    x=1
                elif x3==[]:
                    x=2
                elif x4==[]:
                    x=3
                elif x5==[]:
                    x=4
                elif x5!=[]:
                    x=5

                element_matrix = np.empty((y, x), dtype=np.dtype('U100'))

                for o in range(0,len(ids)):
                    if o in x1:
                        xcoord=0
                    if o in x2:
                        xcoord=1
                    if o in x3:
                        xcoord=2
                    if o in x4:
                        xcoord=3
                    if o in x5:
                        xcoord=4
                    if o in y1:
                        ycoord=0
                    if o in y2:
                        ycoord=1
                    if o in y3:
                        ycoord=2
                    if o in y4:
                        ycoord=3  
                    if o in y5:
                        ycoord=4
                    element_matrix[ycoord,xcoord]=ids[o]
                #try the ai's login method
                letters=['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
                elements = driver.find_elements(By.XPATH,"//*")
                ids = []
                yvalues=[]
                xvalues=[]
                for element in elements:
                    #get info about all the elements in the page
                    element_id = element.get_attribute("id")
                    tag = element.tag_name
                    location = element.location
                    size = element.size
                    #filter out all the stuff that isnt a relevant button or text box
                    if (tag!="" and tag != "a" and tag != "abbr" and tag != "address" and tag != "article" and tag != "aside" and
                        tag != "audio" and tag != "b" and tag != "blockquote" and tag != "body" and tag != "canvas" and
                        tag != "caption" and tag != "cite" and tag != "code" and tag != "col" and tag != "colgroup" and
                        tag != "datalist" and tag != "dd" and tag != "del" and tag != "details" and tag != "dfn" and
                        tag != "dialog" and tag != "div" and tag != "dl" and tag != "dt" and tag != "em" and tag != "embed" and
                        tag != "fieldset" and tag != "figcaption" and tag != "figure" and tag != "footer" and tag != "form" and
                        tag != "head" and tag != "header" and tag != "html" and tag != "i" and tag != "iframe" and tag != "img" and
                        tag != "ins" and tag != "kbd" and tag != "label" and tag != "legend" and tag != "link" and tag != "main" and
                        tag != "map" and tag != "mark" and tag != "menu" and tag != "meta" and tag != "meter" and tag != "nav" and
                        tag != "noscript" and tag != "object" and tag != "ol" and tag != "optgroup" and tag != "option" and
                        tag != "output" and tag != "p" and tag != "param" and tag != "pre" and tag != "progress" and tag != "q" and
                        tag != "rp" and tag != "rt" and tag != "ruby" and tag != "s" and tag != "samp" and tag != "script" and
                        tag != "section" and tag != "select" and tag != "small" and tag != "source" and tag != "span" and
                        tag != "strong" and tag != "style" and tag != "sub" and tag != "summary" and tag != "sup" and
                        tag != "svg" and tag != "table" and tag != "tbody" and tag != "template" and tag != "time" and
                        tag != "title" and tag != "tr" and tag != "track" and tag != "u" and tag != "ul" and tag != "var" and
                        tag != "video" and tag != "wbr" and tag!="h1" and tag!="h2" and tag!="h3" and tag!="h4" and tag!="h5" 
                        and tag!="h6"):
                        #make sure its not hidden
                        if(size["height"]>0 and size["width"]>0 and "hidden" not in element.get_attribute("style").lower() and
                            "display: none" not in element.get_attribute("style").lower() and
                            "visibility: hidden" not in element.get_attribute("style").lower() and
                            element.get_attribute("aria-hidden") != "true" and
                            element.get_attribute("hidden") is None and
                            element.is_displayed()):
                            if element_id=="":
                                element_id=random.choice(letters)+random.choice(letters)+random.choice(letters)+random.choice(letters)
                                driver.execute_script("arguments[0].setAttribute('id', arguments[1]);", element, element_id)
                                action_list.append('noid')
                                action_list.append(str(coordinates))
                            ids.append(element_id)
                            xvalues.append(location["x"])
                            yvalues.append(location["y"])
                #y coords
                y1=[]
                y2=[]
                y3=[]
                y4=[]
                y5=[]
                accounted=[]
                rep=1
                done=False
                while(not done):
                    if rep==1:
                        y1.append(yvalues.index(min(yvalues)))
                    if rep==2:
                        y2.append(yvalues.index(min(yvalues)))
                    if rep==3:
                        y3.append(yvalues.index(min(yvalues)))
                    if rep==4:
                        y4.append(yvalues.index(min(yvalues)))
                    if rep==5:
                        y5.append(yvalues.index(min(yvalues)))
                    accounted.append(yvalues.index(min(yvalues)))
                    for j in range(0,len(ids)):
                        if (yvalues[j]-25)<min(yvalues) and j!=int(yvalues.index(min(yvalues))):
                            if j not in y1 and j not in y2 and j not in y3 and j not in y4 and j not in y5:
                                if rep==1:
                                    y1.append(j)
                                if rep==2:
                                    y2.append(j)
                                if rep==3:
                                    y3.append(j)
                                if rep==4:
                                    y4.append(j)
                                if rep==5:
                                    y5.append(j)
                                accounted.append(j)
                                yvalues[j]=max(yvalues)+10
                    if len(accounted)==len(yvalues):
                        done=True 
                    rep=rep+1
                    #removing this would shift the indexes
                    yvalues[yvalues.index(min(yvalues))]=max(yvalues)+10

                #x coords
                x1=[]
                x2=[]
                x3=[]
                x4=[]
                x5=[]
                accounted=[]
                rep=1
                done=False
                while(not done):
                    if rep==1:
                        x1.append(xvalues.index(min(xvalues)))
                    if rep==2:
                        x2.append(xvalues.index(min(xvalues)))
                    if rep==3:
                        x3.append(xvalues.index(min(xvalues)))
                    if rep==4:
                        x4.append(xvalues.index(min(xvalues)))
                    if rep==5:
                        x5.append(xvalues.index(min(xvalues)))
                    accounted.append(xvalues.index(min(xvalues)))
                    for j in range(0,len(ids)):
                        if (xvalues[j]-40)<min(xvalues) and j!=int(xvalues.index(min(xvalues))):
                            if j not in x1 and j not in x2 and j not in x3 and j not in x4 and j not in x5:
                                if rep==1:
                                    x1.append(j)
                                if rep==2:
                                    x2.append(j)
                                if rep==3:
                                    x3.append(j)
                                if rep==4:
                                    x4.append(j)
                                if rep==5:
                                    x5.append(j)
                                accounted.append(j)
                                xvalues[j]=max(xvalues)+10
                    if len(accounted)==len(xvalues):
                        done=True 
                    rep=rep+1
                    #removing this would shift the indexes
                    xvalues[xvalues.index(min(xvalues))]=max(xvalues)+10
                #form the matrix
                if y2==[]:
                    y=1
                elif y3==[]:
                    y=2
                elif y4==[]:
                    y=3
                elif y5==[]:
                    y=4
                elif y5!=[]:
                    y=5
                if x2==[]:
                    x=1
                elif x3==[]:
                    x=2
                elif x4==[]:
                    x=3
                elif x5==[]:
                    x=4
                elif x5!=[]:
                    x=5

                id_matrix = np.empty((y, x), dtype=np.dtype('U100'))

                for o in range(0,len(ids)):
                    if o in x1:
                        xcoord=0
                    if o in x2:
                        xcoord=1
                    if o in x3:
                        xcoord=2
                    if o in x4:
                        xcoord=3
                    if o in x5:
                        xcoord=4
                    if o in y1:
                        ycoord=0
                    if o in y2:
                        ycoord=1
                    if o in y3:
                        ycoord=2
                    if o in y4:
                        ycoord=3
                    if o in y5:
                        ycoord=4
                    id_matrix[ycoord,xcoord]=ids[o]
                #use matrices to perform actions
                submit=[]
                irows,icolumns=id_matrix.shape
                erows,ecolumns=element_matrix.shape
                if irows>erows:
                    rows=erows
                if irows<erows or irows==erows:
                    rows=irows
                if icolumns>ecolumns:
                    columns=ecolumns
                if icolumns<ecolumns or icolumns==ecolumns:
                    columns=icolumns
                for row in range(0, rows):
                    for column in range(0,columns):
                        if id_matrix[row,column]!='':
                            if element_matrix[row,column]=='submit':
                                submit.append(row)
                                submit.append(column)
                            else:
                                if element_matrix[row,column]=='username':
                                    element=driver.find_element(By.ID,id_matrix[row,column])
                                    for j in range(0,100):
                                        element.send_keys(Keys.BACKSPACE)
                                    element.send_keys(username)
                                    action_list.append('username')
                                    action_list.append(id_matrix[row,column])
                                if element_matrix[row,column]=='password':
                                    element=driver.find_element(By.ID,id_matrix[row,column])
                                    for j in range(0,100):
                                        element.send_keys(Keys.BACKSPACE)
                                    element.send_keys(password)
                                    action_list.append('password')
                                    action_list.append(id_matrix[row,column])
            #if there were no coordinates appended to submit or:[],[], the length of this will still=0 meaning it will try return if something messed up with the alignment
            #do it this way because it has to be the last thing to happen
            if len(submit)>0:
                driver.find_element(By.ID,id_matrix[submit[0],submit[1]]).click()
                action_list.append('submit')
                action_list.append(id_matrix[submit[0],submit[1]])
            else:
                driver.switch_to.active_element.send_keys(Keys.RETURN)
                action_list.append('return')

            WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            action_list.append('wait')
            iteration=0
            while iteration<46:
                if old_url==driver.current_url:
                    time.sleep(1)
                    iteration=iteration+1
                else:
                    break
        if driver.current_url==url:
            with app.app_context():
                sendESP(action_list, IP)
                db=get_db()
                cursor=db.cursor()
                cursor.execute("UPDATE al SET DATA_RECEIVED = ? WHERE IP = ?", ("done", IP))
                db.commit()
    except Exception as e:  
        print(e)
@app.route('/recieve', methods=['POST'])
def recieve():
    datal=request.form['actionlist']
    data_received=True
    db=get_db()
    cursor=db.cursor()
    cursor.execute("UPDATE al SET DATA = ? WHERE IP = ?", (str(datal), request.remote_addr))
    cursor.execute("UPDATE al SET DATA_RECEIVED = ? WHERE IP = ?", ("True", request.remote_addr))
    #FIX FOR REALLY WEIRD MOBILE BROWSER DATA LOSS BUG 
    if datal=="[]":
        cursor.execute("UPDATE al SET EMPTY = ? WHERE IP = ?", ("True", request.remote_addr))
    else:
        cursor.execute("UPDATE al SET EMPTY = ? WHERE IP = ?", ("False", request.remote_addr))
        while read_db(request.remote_addr)[10]=="False":
            cursor.execute("UPDATE al SET DATA = ? WHERE IP = ?", (str(datal), request.remote_addr))
            db.commit()
            time.sleep(0.1)
    cursor.execute("UPDATE al SET RECEIVED = ? WHERE IP = ?", ("False", request.remote_addr))
    db.commit()
    ie=read_db(request.remote_addr)
    return render_template('usergenerate.html')
@app.route('/usergenerate')
def UserGenerate():
    try:
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
                cursor.execute("UPDATE al SET FIRST_TIME = ? WHERE IP = ?", ("False", request.remote_addr))
                db.commit()
                return send_file('images/Loading.png', mimetype='image/png')
            if data_received=="done":
                return send_file('images/success.PNG', mimetype='image/png')
            try:
                if data_received=="False" and image!="":
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
    except:
        return send_file('images/Loading.png', mimetype='image/png')
@app.route('/login-process', methods=['POST'])
def AIGenerate():
    #this method will open an actual web browser and preform operations on its own like parsing and clicks and scrolls.
    #great tutorial https://www.youtube.com/watch?v=SPM1tm2ZdK4
    #standard for every app
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("enable-automation")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    actions=ActionChains(driver)
    #get these after they were entered 
    letters=['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
    username=request.form['username']
    password=request.form['password']
    SCode=random.choice(letters)+random.choice(letters)+random.choice(letters)+random.choice(letters)+random.choice(letters)+random.choice(letters)+random.choice(letters)+random.choice(letters)+random.choice(letters)
    service=request.form['teams']
    if service=="Teams":
        url="https://teams.microsoft.com/_#/apps/66aeee93-507d-479a-a3ef-8f494af43945/sections/classroom"
    first_time="True"
    data_received="False"
    IP=request.remote_addr
    with app.app_context():
        db=get_db()
        curs=db.cursor()
        try:
            curs.execute('DELETE FROM al WHERE SCode = ?', (SCode,))
            db.commit()
        except:
            donothing="nothing"
        db.execute('INSERT INTO al (IP, URL, USERNAME, PASSWORD, FIRST_TIME, DATA_RECEIVED, DONE, DATA, EMPTY, RECEIVED, SCode, action_list) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (IP, url, username, password, first_time, data_received, "False", "", "False", "False", SCode, "[]"))
        db.commit()

    action_list=[]
    action_list.append(username)
    action_list.append(password)
    action_list.append(url)
    #navigate to url(need to include the whole url link)
#----------------------------------------------
    #return render_template('aiisdumb.html')
#----------------------------------------------
    try:
        driver.get(url)
        driver.maximize_window()


        #waits for that url to fully load 
        while driver.current_url==url:
            time.sleep(10)
        while(driver.current_url!=url):
            WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            time.sleep(10)
            old_url=driver.current_url
            #code taken from predict new images.py
            #returns image of webpage to custom designed AI model that will return the coordinates of all elements that need to be addressed
            #dont reset this string so the elements in all the pictures can combine together
            coordinates=[]
            usernamecount=0
            passwordcount=0
            submitcount=0
            def return_elements(it,yit,xsize,ysize,usernamecount,passwordcount,submitcount):
                model = YOLO("best(output-from-training).pt")
                usernamex=[]
                passwordx=[]
                submitx=[]
                usernamey=[]
                passwordy=[]
                submity=[]
                usernamexlength=[]
                passwordxlength=[]
                submitxlength=[]
                usernameylength=[]
                passwordylength=[]
                submitylength=[]
                userscore=[]
                passscore=[]
                submitscore=[]
                

                #identify elements with the ai
                results = model(temp_file.name)[0]
                #for each box:
                for result in results.boxes.data.tolist():
                    x1, y1, x2, y2, score, class_id = result
                #find the center of the box
                    x=(x1+x2)/2
                    y=(y1+y2)/2
                    pagex=(it*xsize)+x
                    pagey=(yit*ysize)+y
                #find side length
                    xlength=x2-x1
                    ylength=y2-y1
                #add all the coordinates to lists
                    if(class_id==0):
                        usernamex.append(pagex)
                        usernamey.append(pagey)
                        userscore.append(score)
                        usernamexlength.append(xlength)
                        usernameylength.append(ylength)
                    if(class_id==1):
                        passwordx.append(pagex) 
                        passwordy.append(pagey)
                        passscore.append(score)
                        passwordxlength.append(xlength)
                        passwordylength.append(ylength)
                    if(class_id==2):
                        submitx.append(pagex)
                        submity.append(pagey)
                        submitscore.append(score)
                        submitxlength.append(xlength)
                        submitylength.append(ylength)
                #if there are multiple of the same element, accept the one with the highest certainty score
                if len(usernamex)>1:
                    for score in range(0,len(userscore)):
                        if max(userscore)==userscore[score]:
                            usernamex.insert(0,usernamex[score])
                            usernamey.insert(0,usernamey[score])
                            usernamexlength.insert(0,usernamexlength[score])
                            usernameylength.insert(0,usernameylength[score])
                if len(passwordx)>1:
                    for score in range(0,len(passscore)):
                        if max(passscore)==passscore[score]:
                            passwordx.insert(0,passwordx[score])
                            passwordy.insert(0,passwordy[score])
                            passwordxlength.insert(0,passwordxlength[score])
                            passwordylength.insert(0,passwordylength[score])
                if len(submitx)>1:
                    for score in range(0,len(submitscore)):
                        if max(submitscore)==submitscore[score]:
                            submitx.insert(0,submitx[score])
                            submity.insert(0,submity[score])
                            submitxlength.insert(0,submitxlength[score])
                            submitylength.insert(0,submitylength[score])
                #add the chosen coordinates to a list that specifies the class of the element they are identifying
                if(len(usernamex)>0):
                    usernamecount=usernamecount+1
                    if(usernamecount>1):
                        for var in range(0,len(coordinates)):
                            if(coordinates[var]=='username'):
                                if(coordinates[(var+3)]<usernamexlength[0]):
                                    for f in range(0,4):
                                        coordinates.remove(var)
                                    coordinates.append("username")
                                    coordinates.append(usernamex[0])
                                    coordinates.append(usernamey[0])
                                    coordinates.append(usernamexlength[0])
                                    coordinates.append(usernameylength[0])
                    else:
                        coordinates.append("username")
                        coordinates.append(usernamex[0])
                        coordinates.append(usernamey[0])
                        coordinates.append(usernamexlength[0])
                        coordinates.append(usernameylength[0])
                if(len(passwordx)>0):
                    passwordcount=passwordcount+1
                    if(passwordcount>1):
                        for var in range(0,len(coordinates)):
                            if(coordinates[var]=='password'):
                                if(coordinates[(var+3)]<passwordxlength[0]):
                                    for f in range(0,4):
                                        coordinates.remove(var)
                                    coordinates.append("password")
                                    coordinates.append(passwordx[0])
                                    coordinates.append(passwordy[0])
                                    coordinates.append(passwordxlength[0])
                                    coordinates.append(passwordylength[0])
                    else:
                        coordinates.append("password")
                        coordinates.append(passwordx[0])
                        coordinates.append(passwordy[0])
                        coordinates.append(passwordxlength[0])
                        coordinates.append(passwordylength[0])
                if(len(submitx)>0):
                    submitcount=submitcount+1
                    if(submitcount>1):
                        for var in range(0,len(coordinates)):
                            if(coordinates[var]=='submit'):
                                if(coordinates[(var+3)]<submitxlength[0]):
                                    for f in range(0,4):
                                        coordinates.remove(var)
                                    coordinates.append("submit")
                                    coordinates.append(submitx[0])
                                    coordinates.append(submity[0])
                                    coordinates.append(submitxlength[0])
                                    coordinates.append(submitylength[0])
                    else:
                        coordinates.append("submit")
                        coordinates.append(submitx[0])
                        coordinates.append(submity[0])
                        coordinates.append(submitxlength[0])
                        coordinates.append(submitylength[0])
                return coordinates
            
            #now we are at the organization specific parts and need to get the user to show us how to sign in
            #first we will save a picture of the start of their organization's sign in page that we can send to the ai 
            image = driver.get_screenshot_as_png()  
            with tempfile.NamedTemporaryFile(suffix='.PNG', delete=False) as temp_file:
                temp_file.write(image)

            img = Image.open(temp_file.name)
            size = img.size
            xsize=int(size[0])/3
            ysize=int(size[1])/3
            for it in range(0,2):
                for yit in range(0,2):
                    with tempfile.NamedTemporaryFile(suffix='.PNG', delete=False) as temp_file:
                        img.crop((it*xsize,yit*ysize,(it+1)*xsize,(yit+1)*ysize)).save(temp_file)
                    coordinates = return_elements(it,yit,xsize,ysize,usernamecount,passwordcount,submitcount)
            temp_file.close()
            #list format is["type",]
            #create the ai's matrix__________________________________________________________________________________________________________________________________________________________________________________________________________________________
            yvalues = []
            xvalues=[]
            ids=[]
            for g in range(0,len(coordinates)):
                if coordinates[g]=='username' or coordinates[g]=='password' or coordinates[g]=='submit':
                    ids.append(coordinates[g])
                    xvalues.append(coordinates[(g+1)])
                    yvalues.append(coordinates[(g+2)])
            y1=[]
            y2=[]
            y3=[]
            y4=[]
            y5=[]
            accounted=[]
            rep=1
            done=False
            while(not done):
                if rep==1:
                    y1.append(yvalues.index(min(yvalues)))
                if rep==2:
                    y2.append(yvalues.index(min(yvalues)))
                if rep==3:
                    y3.append(yvalues.index(min(yvalues)))
                if rep==4:
                    y4.append(yvalues.index(min(yvalues)))
                if rep==5:
                    y5.append(yvalues.index(min(yvalues)))
                accounted.append(yvalues.index(min(yvalues)))
                for j in range(0,len(ids)):
                    if (yvalues[j]-25)<min(yvalues) and j!=int(yvalues.index(min(yvalues))):
                        if j not in y1 and j not in y2 and j not in y3 and j not in y4 and j not in y5:
                            if rep==1:
                                y1.append(j)
                            if rep==2:
                                y2.append(j)
                            if rep==3:
                                y3.append(j)
                            if rep==4:
                                y4.append(j)
                            if rep==5:
                                y5.append(j)
                            accounted.append(j)
                            yvalues[j]=max(yvalues)+10
                if len(accounted)==len(yvalues):
                    done=True 
                rep=rep+1
                #removing this would shift the indexes
                yvalues[yvalues.index(min(yvalues))]=max(yvalues)+10

            #x coords
            x1=[]
            x2=[]
            x3=[]
            x4=[]
            x5=[]
            accounted=[]
            rep=1
            done=False
            while(not done):
                if rep==1:
                    x1.append(xvalues.index(min(xvalues)))
                if rep==2:
                    x2.append(xvalues.index(min(xvalues)))
                if rep==3:
                    x3.append(xvalues.index(min(xvalues)))
                if rep==4:
                    x4.append(xvalues.index(min(xvalues)))
                if rep==5:
                    x5.append(xvalues.index(min(xvalues)))
                accounted.append(xvalues.index(min(xvalues)))
                for j in range(0,len(ids)):
                    if (xvalues[j]-25)<min(xvalues) and xvalues[j]!=min(xvalues):
                        if j not in x1 and j not in x2 and j not in x3 and j not in x4 and j not in x5:
                            if rep==1:
                                x1.append(j)
                            if rep==2:
                                x2.append(j)
                            if rep==3:
                                x3.append(j)
                            if rep==4:
                                x4.append(j)
                            if rep==5:
                                x5.append(j)
                            accounted.append(j)
                            xvalues[j]=max(xvalues)+10
                if len(accounted)==len(xvalues):
                    done=True 
                rep=rep+1
                #removing this would shift the indexes
                xvalues[xvalues.index(min(xvalues))]=max(xvalues)+10
            #form the matrix
            if y2==[]:
                y=1
            elif y3==[]:
                y=2
            elif y4==[]:
                y=3
            elif y5==[]:
                y=4
            elif y5!=[]:
                y=5
            if x2==[]:
                x=1
            elif x3==[]:
                x=2
            elif x4==[]:
                x=3
            elif x5==[]:
                x=4
            elif x5!=[]:
                x=5

            element_matrix = np.empty((y, x), dtype=np.dtype('U100'))

            for o in range(0,len(ids)):
                if o in x1:
                    xcoord=0
                if o in x2:
                    xcoord=1
                if o in x3:
                    xcoord=2
                if o in x4:
                    xcoord=3
                if o in x5:
                    xcoord=4
                if o in y1:
                    ycoord=0
                if o in y2:
                    ycoord=1
                if o in y3:
                    ycoord=2
                if o in y4:
                    ycoord=3
                if o in y5:
                    ycoord=4
                element_matrix[ycoord,xcoord]=ids[o]
            #try the ai's login method
            letters=['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
            elements = driver.find_elements(By.XPATH,"//*")
            ids = []
            yvalues=[]
            xvalues=[]
            for element in elements:
                #get info about all the elements in the page
                element_id = element.get_attribute("id")
                tag = element.tag_name
                location = element.location
                size = element.size
                #filter out all the stuff that isnt a relevant button or text box
                if (tag!="" and tag != "a" and tag != "abbr" and tag != "address" and tag != "article" and tag != "aside" and
                    tag != "audio" and tag != "b" and tag != "blockquote" and tag != "body" and tag != "canvas" and
                    tag != "caption" and tag != "cite" and tag != "code" and tag != "col" and tag != "colgroup" and
                    tag != "datalist" and tag != "dd" and tag != "del" and tag != "details" and tag != "dfn" and
                    tag != "dialog" and tag != "div" and tag != "dl" and tag != "dt" and tag != "em" and tag != "embed" and
                    tag != "fieldset" and tag != "figcaption" and tag != "figure" and tag != "footer" and tag != "form" and
                    tag != "head" and tag != "header" and tag != "html" and tag != "i" and tag != "iframe" and tag != "img" and
                    tag != "ins" and tag != "kbd" and tag != "label" and tag != "legend" and tag != "link" and tag != "main" and
                    tag != "map" and tag != "mark" and tag != "menu" and tag != "meta" and tag != "meter" and tag != "nav" and
                    tag != "noscript" and tag != "object" and tag != "ol" and tag != "optgroup" and tag != "option" and
                    tag != "output" and tag != "p" and tag != "param" and tag != "pre" and tag != "progress" and tag != "q" and
                    tag != "rp" and tag != "rt" and tag != "ruby" and tag != "s" and tag != "samp" and tag != "script" and
                    tag != "section" and tag != "select" and tag != "small" and tag != "source" and tag != "span" and
                    tag != "strong" and tag != "style" and tag != "sub" and tag != "summary" and tag != "sup" and
                    tag != "svg" and tag != "table" and tag != "tbody" and tag != "template" and tag != "time" and
                    tag != "title" and tag != "tr" and tag != "track" and tag != "u" and tag != "ul" and tag != "var" and
                    tag != "video" and tag != "wbr" and tag!="h1" and tag!="h2" and tag!="h3" and tag!="h4" and tag!="h5" 
                    and tag!="h6"):
                    #make sure its not hidden
                    if(size["height"]>0 and size["width"]>0 and "hidden" not in element.get_attribute("style").lower() and
                        "display: none" not in element.get_attribute("style").lower() and
                        "visibility: hidden" not in element.get_attribute("style").lower() and
                        element.get_attribute("aria-hidden") != "true" and
                        element.get_attribute("hidden") is None and
                        element.is_displayed()):
                        if element_id=="":
                            element_id=random.choice(letters)+random.choice(letters)+random.choice(letters)+random.choice(letters)
                            driver.execute_script("arguments[0].setAttribute('id', arguments[1]);", element, element_id)
                            action_list.append('noid')
                            action_list.append(str(coordinates))
                        ids.append(element_id)
                        xvalues.append(location["x"])
                        yvalues.append(location["y"])
            #y coords
            y1=[]
            y2=[]
            y3=[]
            y4=[]
            y5=[]
            accounted=[]
            rep=1
            done=False
            while(not done):
                if rep==1:
                    y1.append(yvalues.index(min(yvalues)))
                if rep==2:
                    y2.append(yvalues.index(min(yvalues)))
                if rep==3:
                    y3.append(yvalues.index(min(yvalues)))
                if rep==4:
                    y4.append(yvalues.index(min(yvalues)))
                if rep==5:
                    y5.append(yvalues.index(min(yvalues)))
                accounted.append(yvalues.index(min(yvalues)))
                for j in range(0,len(ids)):
                    if (yvalues[j]-25)<min(yvalues) and j!=int(yvalues.index(min(yvalues))):
                        if j not in y1 and j not in y2 and j not in y3 and j not in y4 and j not in y5:
                            if rep==1:
                                y1.append(j)
                            if rep==2:
                                y2.append(j)
                            if rep==3:
                                y3.append(j)
                            if rep==4:
                                y4.append(j)
                            if rep==5:
                                y5.append(j)
                            accounted.append(j)
                            yvalues[j]=max(yvalues)+10
                if len(accounted)==len(yvalues):
                    done=True 
                rep=rep+1
                #removing this would shift the indexes
                yvalues[yvalues.index(min(yvalues))]=max(yvalues)+10

            #x coords
            x1=[]
            x2=[]
            x3=[]
            x4=[]
            x5=[]
            accounted=[]
            rep=1
            done=False
            while(not done):
                if rep==1:
                    x1.append(xvalues.index(min(xvalues)))
                if rep==2:
                    x2.append(xvalues.index(min(xvalues)))
                if rep==3:
                    x3.append(xvalues.index(min(xvalues)))
                if rep==4:
                    x4.append(xvalues.index(min(xvalues)))
                if rep==5:
                    x5.append(xvalues.index(min(xvalues)))
                accounted.append(xvalues.index(min(xvalues)))
                for j in range(0,len(ids)):
                    if (xvalues[j]-25)<min(xvalues) and j!=int(xvalues.index(min(xvalues))):
                        if j not in x1 and j not in x2 and j not in x3 and j not in x4 and j not in x5:
                            if rep==1:
                                x1.append(j)
                            if rep==2:
                                x2.append(j)
                            if rep==3:
                                x3.append(j)
                            if rep==4:
                                x4.append(j)
                            if rep==5:
                                x5.append(j)
                            accounted.append(j)
                            xvalues[j]=max(xvalues)+10
                if len(accounted)==len(xvalues):
                    done=True 
                rep=rep+1
                #removing this would shift the indexes
                xvalues[xvalues.index(min(xvalues))]=max(xvalues)+10
            #form the matrix
            if y2==[]:
                y=1
            elif y3==[]:
                y=2
            elif y4==[]:
                y=3
            elif y5==[]:
                y=4
            elif y5!=[]:
                y=5
            if x2==[]:
                x=1
            elif x3==[]:
                x=2
            elif x4==[]:
                x=3
            elif x5==[]:
                x=4
            elif x5!=[]:
                x=5

            id_matrix = np.empty((y, x), dtype=np.dtype('U100'))

            for o in range(0,len(ids)):
                if o in x1:
                    xcoord=0
                if o in x2:
                    xcoord=1
                if o in x3:
                    xcoord=2
                if o in x4:
                    xcoord=3
                if o in x5:
                    xcoord=4
                if o in y1:
                    ycoord=0
                if o in y2:
                    ycoord=1
                if o in y3:
                    ycoord=2
                if o in y4:
                    ycoord=3
                if o in y5:
                    ycoord=4
                id_matrix[ycoord,xcoord]=ids[o]
            #use matrices to perform actions
            submit=[]
            rows,columns=id_matrix.shape
            for row in range(0, rows):
                for column in range(0,columns):
                    if id_matrix[row,column]!='':
                        if element_matrix[row,column]=='submit':
                            submit.append(row)
                            submit.append(column)
                        else:
                            if element_matrix[row,column]=='username':
                                element=driver.find_element(By.ID,id_matrix[row,column])
                                for j in range(0,100):
                                    element.send_keys(Keys.BACKSPACE)
                                element.send_keys(username)
                                action_list.append('username')
                                action_list.append(id_matrix[row,column])
                            if element_matrix[row,column]=='password':
                                element=driver.find_element(By.ID,id_matrix[row,column])
                                for j in range(0,100):
                                    element.send_keys(Keys.BACKSPACE)
                                element.send_keys(password)
                                action_list.append('password')
                                action_list.append(id_matrix[row,column])
            #if there were no coordinates appended to submit or:[],[], the length of this will still=0 meaning it will try return if something messed up with the alignment
            #do it this way because it has to be the last thing to happen
            if len(submit)>0:
                driver.find_element(By.ID,id_matrix[submit[0],submit[1]]).click()
                action_list.append('submit')
                action_list.append(id_matrix[submit[0],submit[1]])
            else:
                driver.switch_to.active_element.send_keys(Keys.RETURN)
                action_list.append('return')

            WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            action_list.append('wait')
            iteration=0
            while iteration<6:
                if old_url==driver.current_url:
                    time.sleep(10)
                    iteration=iteration+1
                else:
                    break
            time.sleep(5)
            if old_url==driver.current_url:
                driver.quit()
                return render_template('aiisdumb.html')
        if driver.current_url==url:
            #return action list
            sendESP(action_list, request.remote_addr)
            return render_template('success.html')
            #finding yes or no is for a different function
        else:
            driver.quit()
            return render_template('aiisdumb.html')
        driver.quit()
        #window will close when operations are done
    except Exception as e:
        driver.quit()
        return render_template('aiisdumb.html')
       

if __name__ == '__main__':
    serve(app,host = '0.0.0.0',port = 5000)
    #app.run(host='0.0.0.0')
    #app.run(debug=True,host='0.0.0.0')
