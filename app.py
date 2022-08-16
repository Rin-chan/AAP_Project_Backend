# from crypt import methods
from datetime import datetime
from fileinput import filename
from unittest import result
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, Response
from flaskext.mysql import MySQL
from Forms import ResetForm
import yagmail
import hashlib
import logging
import json

from camera import gen_frames, capturePhoto, closeCamera
from qr_generator import create_qr_code

from models.faceVerification.siamese import generateDiss
from models.imgClassification.imgClassification import classify_eWaste_j, classify_eWaste_s, reformat_predictions
from models.binRouting.routing import getPath

import string
import random
def unique_id(size):
    chars = list(set(string.ascii_uppercase + string.digits).difference('LIO01'))
    return ''.join(random.choices(chars, k=size))

with open('settings.json', 'r') as f:
    settings = json.load(f)

email_username = "appdevproto123@gmail.com"
email_password = "hocbwonzwnxplmlo"
server = yagmail.SMTP(email_username,email_password)
flaskServer = settings['flaskServer']

app = Flask(__name__)
app.config["CACHE_TYPE"] = "null"

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'rin'
app.config['MYSQL_DATABASE_PASSWORD'] = '123456'
app.config['MYSQL_DATABASE_DB'] = 'aap_project'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)
conn = mysql.connect()
cursor = conn.cursor()

# GENERATE TABLE IF DOESN'T EXIST
cursor.execute("CREATE TABLE IF NOT EXISTS `users` (`id` int NOT NULL AUTO_INCREMENT,`username` varchar(100) NOT NULL,`email` varchar(100) NOT NULL,`password` longtext,`contact` varchar(8) DEFAULT '',`address` varchar(100) DEFAULT '',`face` tinyint DEFAULT '0',`faceImage` longtext,`points` int DEFAULT '0',`disabled` tinyint DEFAULT '0',`verified` tinyint DEFAULT '0',`profilePic` longtext,PRIMARY KEY (`id`),UNIQUE KEY `id_UNIQUE` (`id`)) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci")
cursor.execute("CREATE TABLE IF NOT EXISTS `staff_users` (`id` int NOT NULL AUTO_INCREMENT,`username` varchar(100) NOT NULL,`email` varchar(100) NOT NULL,`password` longtext NOT NULL,`type` int DEFAULT '0',`disabled` tinyint DEFAULT '0',PRIMARY KEY (`id`),UNIQUE KEY `id_UNIQUE` (`id`)) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci")
cursor.execute("CREATE TABLE IF NOT EXISTS `bins` (`id` int NOT NULL AUTO_INCREMENT,`location` varchar(100) NOT NULL,`capacity` varchar(100) NOT NULL,`selected` tinyint DEFAULT '0',`x` varchar(100),`y` varchar(100),PRIMARY KEY (`id`),UNIQUE KEY `id_UNIQUE` (`id`)) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci")
cursor.execute("CREATE TABLE IF NOT EXISTS `reset_password` (`id` int NOT NULL AUTO_INCREMENT,`email` varchar(100) NOT NULL,`ref` longtext NOT NULL,PRIMARY KEY (`id`),UNIQUE KEY `id_UNIQUE` (`id`)) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci")
cursor.execute("CREATE TABLE IF NOT EXISTS `email_verification` (`id` int NOT NULL AUTO_INCREMENT,`email` varchar(100) NOT NULL,`ref` longtext NOT NULL,PRIMARY KEY (`id`),UNIQUE KEY `id_UNIQUE` (`id`)) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci")
cursor.execute("CREATE TABLE IF NOT EXISTS `gifts` (`id` int NOT NULL AUTO_INCREMENT,`giftname` varchar(100) NOT NULL,`description` longtext,`industry` varchar(100) DEFAULT '',`company` varchar(100) DEFAULT '',`code` varchar(100) NOT NULL,`points` int DEFAULT '0',`img` longtext,PRIMARY KEY (`id`),UNIQUE KEY `id_UNIQUE` (`id`))ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci")
cursor.execute("CREATE TABLE IF NOT EXISTS `redeem_history` (`id` int NOT NULL AUTO_INCREMENT,`redeemcode` varchar(100) DEFAULT '',`giftname` varchar(100) NOT NULL,`description` longtext,`industry` varchar(100) DEFAULT '',`company` varchar(100) DEFAULT '',`points` int DEFAULT '0',`img` longtext,`itemcode` varchar(100) DEFAULT '',`email` varchar(100) NOT NULL,`used` tinyint DEFAULT '0',PRIMARY KEY (`redeemcode`),UNIQUE KEY `id_UNIQUE` (`id`))ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;")
conn.commit()

# GENERATE DATA FOR BINS
cursor.execute('SELECT * FROM bins')
bin_num = cursor.fetchall()
if (len(bin_num) == 0):
    cursor.execute('INSERT INTO bins (location, capacity, selected, x, y) VALUES ("Woodlands", "Full", 1, "103.78608280407208", "1.4368884371488417")')
    cursor.execute('INSERT INTO bins (location, capacity, selected, x, y) VALUES ("Yishun", "Partial", 1, "103.83547675603042", "1.4287263455402195")')
    cursor.execute('INSERT INTO bins (location, capacity, selected, x, y) VALUES ("Sembawang", "Empty", 0, "103.81908202190971", "1.4479635226929266")')
    cursor.execute('INSERT INTO bins (location, capacity, selected, x, y) VALUES ("Holland", "Full", 1, "103.7956539984589", "1.3107906233617734")')
    cursor.execute('INSERT INTO bins (location, capacity, selected, x, y) VALUES ("Tuas", "Full", 1, "103.65172505378723", "1.330620825973527")')
    cursor.execute('INSERT INTO bins (location, capacity, selected, x, y) VALUES ("Tampines", "Partial", 1, "103.94501280794431", "1.354064943770207")')
    cursor.execute('INSERT INTO bins (location, capacity, selected, x, y) VALUES ("Bedok", "Full", 1, "103.9292746782303", "1.3245660237642984")')
    conn.commit()

# GENERATE DATA FOR GIFTS
cursor.execute('SELECT * FROM gifts')
gift_num = cursor.fetchall()
if (len(gift_num) == 0):
    cursor.execute('INSERT INTO gifts (giftname, description, industry, company, code, points, img) VALUES ("GRAB FOOD $2 OFF VOUCHER", "Terms & Conditions: 1. Valid for one-time use on a single Food order in Singapore only. 2. Valid on GrabFood only. GrabMart not included. 3. Voucher is non-transferable, non-refundable and non-exchangeable for cash/credit-in-kind If your voucher has an error, please visit our help centre to report on the issue: https://help.grab.com/hc/en-sg/articles/115011212167-My-promo-code-doesn-t-work", "Food", "GRAB FOOD", "K3479AD8", 200, "../../assets/images/grabfood.png")')
    cursor.execute('INSERT INTO gifts (giftname, description, industry, company, code, points, img) VALUES ("GRAB FOOD $10 OFF VOUCHER", "Terms & Conditions: 1. Valid for one-time use on a single Food order in Singapore only. 2. Valid on GrabFood only. GrabMart not included. 3. Voucher is non-transferable, non-refundable and non-exchangeable for cash/credit-in-kind If your voucher has an error, please visit our help centre to report on the issue: https://help.grab.com/hc/en-sg/articles/115011212167-My-promo-code-doesn-t-work", "Food", "GRAB FOOD", "K347C2L8", 800, "../../assets/images/grabfood.png")')
    cursor.execute('INSERT INTO gifts (giftname, description, industry, company, code, points, img) VALUES ("POPULAR $10 GIFTCARD", "Terms & Conditions: 1. eGiftCard validity showcased on Mooments URL to be considered final, and adhered to accordingly. 2.Redeemable at all POPULAR bookstores and UrbanWrite stores in Singapore only. 3. Redemption is not applicable at the self-checkout kiosk. 4.Not exchangeable for cash and not refundable for any unused balance (one-time use only) 5. Multiple POPULAR Gift Cards from Mooments can be used in a single transaction. 6. Not valid for purchase of Gift Vouchers or application / renewal/ replacement of POPULAR Card.", "Shopping", "POPULAR", "POP5663D", 800, "../../assets/images/popular.png")')
    conn.commit()


# FOR TESTING
# Web Pages Related
@app.route("/")
def home():
    closeCamera()
    return render_template('home.html')

@app.route("/takePhoto")
def takePhoto():
    return render_template('takePhoto.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/displayImg')
def displayImg():
    filename = capturePhoto()
    return render_template('displayImg.html', image=filename)

@app.route('/displayQR/<pred>')
def displayQR(pred):
    filename = create_qr_code(pred)
    return render_template('displayQR.html', qr=filename)

@app.route('/reset/<string:ref>', methods=['GET', 'POST'])
def reset(ref):
    conn = mysql.connect()  # reconnecting mysql
    with conn.cursor() as cursor:
        cursor.execute('SELECT * FROM reset_password WHERE ref = "{0}"'.format(ref))
        result = cursor.fetchall()

    if len(result) != 0:
        resetForm = ResetForm(request.form)
        if request.method == 'POST' and resetForm.validate():
            hashed_password = hashlib.sha256(resetForm.password.data.encode('utf-8')).hexdigest()
            conn = mysql.connect()  # reconnecting mysql
            with conn.cursor() as cursor:
                cursor.execute('UPDATE users SET password = "{0}" WHERE email = "{1}"'.format(hashed_password, result[0][1]))
                conn.commit()
                
            conn = mysql.connect()  # reconnecting mysql
            with conn.cursor() as cursor:
                cursor.execute('DELETE FROM reset_password WHERE ref = "{0}"'.format(ref))
                conn.commit()
                
            return redirect(url_for('home'))
        return render_template('reset.html', form=resetForm)
    return redirect(url_for('home'))

@app.route('/verified/<string:ref>', methods=['GET', 'POST'])
def verified(ref):
    conn = mysql.connect()  # reconnecting mysql
    with conn.cursor() as cursor:
        cursor.execute('SELECT * FROM email_verification WHERE ref = "{0}"'.format(ref))
        result = cursor.fetchall()

    if len(result) != 0:
        conn = mysql.connect()  # reconnecting mysql
        with conn.cursor() as cursor:
            cursor.execute('UPDATE users SET verified = "1" WHERE email = "{0}"'.format(result[0][1]))
            conn.commit()
                
        conn = mysql.connect()  # reconnecting mysql
        with conn.cursor() as cursor:
            cursor.execute('DELETE FROM email_verification WHERE ref = "{0}"'.format(ref))
            conn.commit()
            
        return render_template('verified.html')
    return redirect(url_for('home'))

# AI Related
@app.route("/faceVerification/", methods=['POST'])
def faceVerification():
    input = request.get_json()
    result = generateDiss(input['originalFaceImage'], input['faceImage'])
    return jsonify(result=result)

@app.route("/routing/", methods=['POST'])
def routing():
    conn = mysql.connect()  # reconnecting mysql
    with conn.cursor() as cursor:
        cursor.execute('SELECT * FROM bins')
        binResult = cursor.fetchall()
        
    result = getPath(binResult)
    return jsonify(result=result)

@app.route("/imgClassification/<filename>")
def imgClassification(filename):
    final_result = ""

    pred_j = classify_eWaste_j(filename)
    pred_S = classify_eWaste_s(filename)

    class_j, percent_j = reformat_predictions(pred_j, "j")
    class_s, percent_s = reformat_predictions(pred_S, "s")
    
    if percent_s > percent_j:
        if class_s == 'others':
            if (percent_j * 100) <= 50.0:
                final_result = "non_regulated"
            else:
                final_result = class_j
    else:
        if class_j == 'others':
            if (percent_s * 100) <= 50.0:
                final_result = "non_regulated"
            else:
                final_result = class_s
    print("final result =" + final_result)
    
    return render_template('ai_Results.html', prediction=final_result)
    
# Database Related
# Consumer App
@app.route("/addUser/", methods=["POST"])
def addUser():
    user = request.get_json()
    
    conn = mysql.connect()  # reconnecting mysql
    with conn.cursor() as cursor:
        cursor.execute('INSERT INTO users (username, email, password, verified) VALUES ("{0}", "{1}", "{2}", "{3}")'.format(user["username"], user["email"], user["password"], user["verified"]))
        conn.commit()
        
    return "Done"

@app.route("/getSpecificUser/", methods=["POST"])
def getSpecificUser():
    user = request.get_json()
    
    conn = mysql.connect()  # reconnecting mysql
    with conn.cursor() as cursor:
        cursor.execute('SELECT * FROM users WHERE email = "{0}"'.format(user["email"]))
        result = cursor.fetchall()
        
    return jsonify(result=result)
    
@app.route("/getAllUsersCount/", methods=["POST"])
def getAllUsersCount():
    req = request.get_json()
    
    conn = mysql.connect()  # reconnecting mysql
    with conn.cursor() as cursor:         
        cursor.execute('SELECT COUNT(*) FROM users WHERE username LIKE "%{0}%"'.format(req["query"]))
        result = cursor.fetchall()
    return jsonify(result=result)

@app.route("/getAllUsers/", methods=["POST"])
def getAllUser():
    req = request.get_json()
    
    offset = req["page"]*req["itemsPerPage"]
    
    conn = mysql.connect()  # reconnecting mysql
    with conn.cursor() as cursor:
        cursor.execute('SELECT * FROM users WHERE username LIKE "%{2}%" LIMIT {1} OFFSET {0}'.format(offset, req["itemsPerPage"], req["query"]))
        result = cursor.fetchall()
    return jsonify(result=result)

@app.route("/updateUserDetails/", methods=["POST"])
def updateUserDetails():
    user = request.get_json()
    
    conn = mysql.connect()  # reconnecting mysql
    with conn.cursor() as cursor:
        cursor.execute('UPDATE users SET username = "{0}", contact = "{2}", address = "{3}" WHERE email = "{1}"'.format(user["username"], user["email"], user["contact"], user["address"]))
        conn.commit()
        
    return "Done"

@app.route("/updateUserPassword/", methods=["POST"])
def updateUserPassword():
    user = request.get_json()
    
    conn = mysql.connect()  # reconnecting mysql
    with conn.cursor() as cursor:
        cursor.execute('UPDATE users SET password = "{1}" WHERE email = "{0}"'.format(user["email"], user["password"]))
        conn.commit()
        
    return "Done"

@app.route("/updateUserFace/", methods=["POST"])
def updateUserFace():
    user = request.get_json()
    
    conn = mysql.connect()  # reconnecting mysql
    with conn.cursor() as cursor:
        cursor.execute('UPDATE users SET faceImage = "{1}", face = "{2}" WHERE email = "{0}"'.format(user["email"], user["faceImage"], user["face"]))
        conn.commit()
        
    return "Done"

@app.route("/updateUserProfilePic/", methods=["POST"])
def updateUserProfilePic():
    user = request.get_json()
    
    conn = mysql.connect()  # reconnecting mysql
    with conn.cursor() as cursor:
        cursor.execute('UPDATE users SET profilePic = "{1}" WHERE email = "{0}"'.format(user["email"], user["profilePic"]))
        conn.commit()
        
    return "Done"

@app.route("/updateUserDisabled/", methods=["POST"])
def updateUserDisabled():
    user = request.get_json()
    
    conn = mysql.connect()  # reconnecting mysql
    with conn.cursor() as cursor:
        cursor.execute('UPDATE users SET disabled = "{0}" WHERE email = "{1}"'.format(user["disabled"], user["email"]))
        conn.commit()
    return "Done"

@app.route("/forgotPassword/", methods=["POST"])
def forgotPassword():
    user = request.get_json()
    
    cur_date = datetime.now()
    original_text = str(user["email"]) + str(cur_date)
    hashed_text = hashlib.sha1(original_text.encode('utf-8')).hexdigest()
    link = "http://{0}/reset/{1}" .format(flaskServer, hashed_text)

    # Sending emails
    try:
        text = "You requested for a password reset.\n Click the link below to reset your password.\n{0}" .format(link)

        server.send(to = user["email"], subject = "Forgot Password", contents = text)
    except Exception as e:
        print(e)
        
    conn = mysql.connect()  # reconnecting mysql
    with conn.cursor() as cursor:
        cursor.execute('INSERT INTO reset_password (email,ref) VALUES ("{0}","{1}")'.format(user["email"], hashed_text))
        conn.commit()
        
    return "Done"

@app.route("/emailVerification/", methods=["POST"])
def emailVerification():
    user = request.get_json()
    
    cur_date = datetime.now()
    original_text = str(user["email"]) + str(cur_date)
    hashed_text = hashlib.sha1(original_text.encode('utf-8')).hexdigest()
    link = "http://{0}/verified/{1}" .format(flaskServer, hashed_text)

    # Sending emails
    try:
        text = "You have registered an account for ALBA E-Waste app.\n Click the link below to verify your account.\n{0}" .format(link)

        server.send(to = user["email"], subject = "Email Verification", contents = text)
    except Exception as e:
        print(e)
        
    conn = mysql.connect()  # reconnecting mysql
    with conn.cursor() as cursor:
        cursor.execute('INSERT INTO email_verification (email,ref) VALUES ("{0}","{1}")'.format(user["email"], hashed_text))
        conn.commit()
        
    return "Done"

@app.route("/getAllGifts/", methods=["POST"])
def getAllGifts():
    req = request.get_json()
    conn = mysql.connect()  # reconnecting mysql
    with conn.cursor() as cursor:
        cursor.execute('SELECT giftname, points, industry, company, img, code FROM gifts LIMIT {1} OFFSET {0}'.format(req['offset'], req['pagelimit']))
        result = cursor.fetchall()

    return jsonify(result=result)

@app.route("/FilterGifts/", methods=["POST"])
def filterGifts():
    req = request.get_json()
    conn = mysql.connect()  # reconnecting mysql
    with conn.cursor() as cursor:
        cursor.execute('SELECT giftname, points, industry, img, code FROM gifts WHERE industry = "{0}"'.format(req['filter']))
        result = cursor.fetchall()

    return jsonify(result=result)

@app.route("/getSpecificGift/", methods=["POST"])
def getSpecificGift():
    req = request.get_json()
    
    conn = mysql.connect()  # reconnecting mysql
    with conn.cursor() as cursor:
        cursor.execute('SELECT * FROM gifts WHERE code = "{0}"'.format(req['code']))
        result = cursor.fetchall()
        
    return jsonify(result=result)


# Add Redeem Item
@app.route("/addRedeemItem/", methods=["POST"])
def addRedeemItem():

    redeemcode = unique_id(8)
    req = request.get_json()
    
    conn = mysql.connect()  # reconnecting mysql
    with conn.cursor() as cursor:
        cursor.execute('INSERT INTO redeem_history (itemcode, email, redeemcode, giftname, industry, company, points, img, description) VALUES ("{0}", "{1}", "{2}", "{3}", "{4}", "{5}","{6}", "{7}", "{8}")'.format(req["itemcode"], req["email"], redeemcode, req['giftname'] , req['industry'], req['company'], req['points'], req['img'], req['description']))
        conn.commit()
    return "done"

@app.route("/getSpecificRedeem/", methods=["POST"])
def getSpecificRedeem():
    req = request.get_json()
    
    conn = mysql.connect()  # reconnecting mysql
    with conn.cursor() as cursor:
        cursor.execute('SELECT * FROM redeem_history WHERE redeemcode = "{0}"'.format(req['redeemcode']))
        result = cursor.fetchall()
        
    return jsonify(result=result)

# Use Redeem Item
@app.route("/useRedeemItem/", methods=["POST"])
def usedRedeemItem(): 
    req = request.get_json()

    cur_date = datetime.now()
    original_text = str(req["email"]) + str(cur_date)
    hashed_text = hashlib.sha1(original_text.encode('utf-8')).hexdigest()

    # Sending emails
    try:
        text = "Hi,\n The code for {1} is {0}\n Thank you." .format(req["redeemcode"], req["giftname"])

        server.send(to = req["email"], subject = "Code for Redeemed item", contents = text)
    except Exception as e:
        print(e)
        
    conn = mysql.connect()  # reconnecting mysql
    with conn.cursor() as cursor:
        cursor.execute('UPDATE redeem_history SET used = 1 WHERE redeemcode = "{0}"'.format(req["redeemcode"]))
        conn.commit()
    return "Done"

@app.route("/getUnusedRedeemItems/", methods=["POST"])
def getAllUnusedRedeemItem():
    req = request.get_json()
    
    conn = mysql.connect()  # reconnecting mysql
    with conn.cursor() as cursor:
        cursor.execute('SELECT * FROM redeem_history WHERE email = "{0}" AND used = 0'.format(req['email']))
        result = cursor.fetchall()
        
    return jsonify(result=result)

@app.route("/getUsedRedeemItems/", methods=["POST"])
def getAllUsedRedeemItem():
    req = request.get_json()
    
    conn = mysql.connect()  # reconnecting mysql
    with conn.cursor() as cursor:
        cursor.execute('SELECT * FROM redeem_history WHERE email = "{0}" AND used = 1'.format(req['email']))
        result = cursor.fetchall()
        
    return jsonify(result=result)

@app.route("/getUserPoints/", methods=["POST"])
def getUserPoints():
    user = request.get_json()
    conn = mysql.connect()  # reconnecting mysql
    with conn.cursor() as cursor:
        cursor.execute('SELECT points FROM users WHERE email = "{0}"'.format(user["email"]))
        result = cursor.fetchall()
    return jsonify(result=result)

@app.route("/updateUserPoints/", methods=["POST"])
def updateUserPoints():
    user = request.get_json()
    conn = mysql.connect()  # reconnecting mysql
    with conn.cursor() as cursor:
        cursor.execute('UPDATE users SET points = "{1}" WHERE email = "{0}"'.format(user["email"], user["points"]))
        conn.commit()
    return 'Done'

# Staff App
@app.route("/addStaffUser/", methods=["POST"])
def addStaffUser():
    user = request.get_json()
    
    conn = mysql.connect()  # reconnecting mysql
    with conn.cursor() as cursor:
        cursor.execute('INSERT INTO staff_users (username, email, password, type) VALUES ("{0}", "{1}", "{2}", "{3}")'.format(user["username"], user["email"], user["password"], user["type"]))
        conn.commit()
    return "Done"

@app.route("/getStaffSpecificUser/", methods=["POST"])
def getStaffSpecificUser():
    user = request.get_json()
    
    conn = mysql.connect()  # reconnecting mysql
    with conn.cursor() as cursor:
        cursor.execute('SELECT * FROM staff_users WHERE email = "{0}"'.format(user["email"]))
        result = cursor.fetchall()
    return jsonify(result=result)

@app.route("/getStaffAllUsersCount/", methods=["POST"])
def getStaffAllUsersCount():
    req = request.get_json()
    
    conn = mysql.connect()  # reconnecting mysql
    with conn.cursor() as cursor:
        cursor.execute('SELECT COUNT(*) FROM staff_users WHERE username LIKE "%{0}%"'.format(req["query"]))
        result = cursor.fetchall()
    return jsonify(result=result)

@app.route("/getStaffAllUsers/", methods=["POST"])
def getStaffAllUser():
    req = request.get_json()
    
    offset = req["page"]*req["itemsPerPage"]
    
    conn = mysql.connect()  # reconnecting mysql
    with conn.cursor() as cursor:
        cursor.execute('SELECT * FROM staff_users WHERE username LIKE "%{2}%" LIMIT {1} OFFSET {0}'.format(offset, req["itemsPerPage"], req["query"]))
        result = cursor.fetchall()
        
    return jsonify(result=result)

@app.route("/updateStaffUserDisabled/", methods=["POST"])
def updateStaffUserDisabled():
    user = request.get_json()
    
    conn = mysql.connect()  # reconnecting mysql
    with conn.cursor() as cursor:
        cursor.execute('UPDATE staff_users SET disabled = "{0}" WHERE email = "{1}"'.format(user["disabled"], user["email"]))
        conn.commit()
    return "Done"

@app.route("/updateStaffUserType/", methods=["POST"])
def updateStaffUserType():
    user = request.get_json()
    
    conn = mysql.connect()  # reconnecting mysql
    with conn.cursor() as cursor:
        cursor.execute('UPDATE staff_users SET type = "{0}" WHERE email = "{1}"'.format(user["type"], user["email"]))
        conn.commit()
    return "Done"

@app.route("/updateStaffUserPassword/", methods=["POST"])
def updateStaffUserPassword():
    user = request.get_json()
    
    conn = mysql.connect()  # reconnecting mysql
    with conn.cursor() as cursor:
        cursor.execute('UPDATE staff_users SET password = "{1}" WHERE email = "{0}"'.format(user["email"], user["password"]))
        conn.commit()
        
    return "Done"

@app.route("/getStaffAllBins/", methods=["POST"])
def getStaffAllBins():
    conn = mysql.connect()  # reconnecting mysql
    with conn.cursor() as cursor:
        cursor.execute('SELECT * FROM bins')
        result = cursor.fetchall()
        
    return jsonify(result=result)

@app.route("/getStaffBins/", methods=["POST"])
def getStaffBins():
    req = request.get_json()
    
    offset = req["page"]*req["itemsPerPage"]
    
    conn = mysql.connect()  # reconnecting mysql
    with conn.cursor() as cursor:
        cursor.execute('SELECT * FROM bins WHERE location LIKE "%{2}%" LIMIT {1} OFFSET {0}'.format(offset, req["itemsPerPage"], req["query"]))
        result = cursor.fetchall()
        
    return jsonify(result=result)

@app.route("/updateStaffBins/", methods=["POST"])
def updateStaffBins():
    bin = request.get_json()
    
    conn = mysql.connect()  # reconnecting mysql
    with conn.cursor() as cursor:
        cursor.execute('UPDATE bins SET selected = "{1}" WHERE id = "{0}"'.format(bin["id"], bin["selected"]))
        conn.commit()
        
    return "Done"

@app.route("/getStaffAllBinsCount/", methods=["POST"])
def getStaffAllBinsCount():
    req = request.get_json()
    
    conn = mysql.connect()  # reconnecting mysql
    with conn.cursor() as cursor:
        cursor.execute('SELECT COUNT(*) FROM bins WHERE location LIKE "%{0}%"'.format(req["query"]))
        result = cursor.fetchall()
    return jsonify(result=result)

    
if __name__ == "__main__":
    app.run()