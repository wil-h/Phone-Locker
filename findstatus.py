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

#-----------------------------------
conn = sqlite3.connect('database.db')
cursor = conn.cursor()
cursor.execute('INSERT INTO api (IP, WORKING, STATUS, ALIST) VALUES (?, ?, ?, ?)', ("helloabdulionigsdssdf", "false", "", "['https://teams.microsoft.com/_#/apps/66aeee93-507d-479a-a3ef-8f494af43945/sections/classroom', 'C', '-55,352', 'T', 'W', 'T', 'h', 'T', 'a', 'T', 'r', 'T', 'r', 'T', 'i', 'T', 'c', 'T', 'k', 'T', '2', 'T', '5', 'T', '@', 'T', 'c', 'T', 'h', 'T', 'a', 'T', 'r', 'T', 'l', 'T', 'o', 'T', 't', 'T', 't', 'T', 'e', 'T', 'c', 'T', 'o', 'T', 'u', 'T', 'n', 'T', 't', 'T', 'r', 'T', 'y', 'T', 'd', 'T', 'a', 'T', 'y', 'T', '.', 'T', 'o', 'T', 'r', 'T', 'g', 'C', '128,503', 'C', '-14,29', 'C', '60,-2', 'T', 'C', 'T', 'D', 'T', 'a', 'T', 'y', 'T', '2', 'T', '5', 'T', '2', 'T', '2', 'T', '8', 'T', '!', 'C', '43,75', 'C', '93,535']"))
conn.commit()
cursor.close()
conn.close()
print("wrote")
#-----------------------------------

def read_db(IP):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM api')
    al = cursor.fetchall()
    dicti=[dict(row) for row in al]
    reun=[]
    for dic in dicti:
        if dic["IP"]==IP:
            reun.append(dic["IP"])
            reun.append(dic["WORKING"])
            reun.append(dic["STATUS"])
            reun.append(dic['ALIST'])
    cursor.close()
    conn.close()
    return(reun)
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
    #actionlist=eval(eval(actionlst))
    actionlist=eval(actionlst)
    options = Options()
    #options.add_argument("--headless=new")
    #options.add_argument("--disable-gpu")
    #options.add_argument("--no-sandbox")
    #options.add_argument("enable-automation")
    #options.add_argument("--disable-infobars")
    #options.add_argument("--disable-dev-shm-usage")
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
    time.sleep(15)
    if driver.current_url==ur_l:
        #check for upcoming assingments
        if ur_l=="https://teams.microsoft.com/_#/apps/66aeee93-507d-479a-a3ef-8f494af43945/sections/classroom":
            
            #---------------------------------------------------------------------------------------------------------------------------------
            WebDriverWait(driver, 500).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            #time.sleep(15)
            #img=driver.get_screenshot_as_png()
            #pil=Image.open(io.BytesIO(img))
            #pil=pil.resize((1000,1000))
            #pil.save("image1.png", format='PNG')
            #driver.refresh()
            #time.sleep(15)
            #img=driver.get_screenshot_as_png()
            #pil=Image.open(io.BytesIO(img))
            #pil=pil.resize((1000,1000))
            #pil.save("image2.png", format='PNG')
            #---------------------------------------------------------------------------------------------------------------------------------

            WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.XPATH, "//iframe[@title='Assignments Tab View']")))
            driver.switch_to.frame(driver.find_element(By.XPATH, "//iframe[@title='Assignments Tab View']"))
            time.sleep(5)
            days=[]
            try:
                days=driver.find_elements(By.CLASS_NAME, "date-group-label-shorthand__pjq0w")
            except:
                status="false"
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
