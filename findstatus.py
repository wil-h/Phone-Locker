from selenium import webdriver 
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import threading
import time
import sqlite3

def write_db(IP, column, insert):
    done=False
    while not done:
        try:
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute('UPDATE api SET '+column+' = ? WHERE IP = ?', (insert, IP))
            conn.commit()
            cursor.close()
            conn.close()
            done=True
        except:
            nothing="nothing"
            done=False
def findstatus(IP, actionlst):
    print("started")
    actionlist=eval(eval(actionlst))
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("enable-automation")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    ur_l=actionlist[0]
    driver.get(ur_l)
    driver.set_window_size(1000,1000)
    WebDriverWait(driver, 500).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
    time.sleep(3)
    for x in range(1,len(actionlist),2):
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
            print(actionlist[x+1])
            print(l)
            actions.move_by_offset(l[0],l[1]).click() 
            actions.perform()
            WebDriverWait(driver, 500).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            time.sleep(4)
    print("waiting")
    time.sleep(15)
    print("woted")
    if driver.current_url==ur_l:
        print("url==url")
        #check for upcoming assingments
        if ur_l=="https://teams.microsoft.com/_#/apps/66aeee93-507d-479a-a3ef-8f494af43945/sections/classroom":
            print("url==teams")
            WebDriverWait(driver, 500).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.XPATH, "//iframe[@title='Assignments Tab View']")))
            driver.switch_to.frame(driver.find_element(By.XPATH, "//iframe[@title='Assignments Tab View']"))
            print("waited for iframe")
            time.sleep(5)
            days=[]
            try:
                WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, "date-group-label-shorthand__pjq0w")))
                print("waited for days")
                days=driver.find_elements(By.CLASS_NAME, "date-group-label-shorthand__pjq0w")
                print("found days:",days)
            except:
                status="false"
                print("had exception")
                days=driver.find_elements(By.CLASS_NAME, "date-group-label-shorthand__pjq0w")
            for day in days:
                if day.text=="Today" or day.text=="Tomorrow" or day.text=="Friday":
                    status="true"
                    break
                status="false"
    else:
        status="false"
    write_db(IP, "STATUS", status)
    write_db(IP, "WORKING", "done")
    print(status)
while True:
    try:
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM api')
            rows = cursor.fetchall()
        for row in rows:
            if row[3]=="false":
                thread = threading.Thread(target=findstatus, args=(row[2],row[5],))
                thread.start()
                write_db(row[2], "WORKING", "true")

        time.sleep(1)    
    except Exception as e:
        print(e)
        nothing="nothing"
