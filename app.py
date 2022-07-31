# from crypt import methods
from fileinput import filename
from unittest import result
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, Response
from flaskext.mysql import MySQL

import logging

from camera import gen_frames, capturePhoto, closeCamera
from qr_generator import create_qr_code

from models.faceVerification.siamese import generateDiss
from models.imgClassification.imgClassification import classify_eWaste, reformat_predictions

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
# Create user table
cursor.execute("CREATE TABLE IF NOT EXISTS `users` (`id` int NOT NULL AUTO_INCREMENT,`username` varchar(100) NOT NULL,`email` varchar(100) NOT NULL,`password` longtext NOT NULL,`contact` varchar(8) DEFAULT '',`address` varchar(100) DEFAULT '',`face` tinyint DEFAULT '0',`faceImage` longtext,`points` int DEFAULT '0',PRIMARY KEY (`id`),UNIQUE KEY `id_UNIQUE` (`id`)) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci")
conn.commit()

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

# AI Related
@app.route("/faceVerification/", methods=['POST'])
def faceVerification():
    input = request.get_json()
    result = generateDiss(input['originalFaceImage'], input['faceImage'])
    return jsonify(result=result)

@app.route("/imgClassification/<filename>")
def imgClassification(filename):
    predictions = classify_eWaste(filename)
    print(predictions)
    logging.info(predictions)
    final_result = reformat_predictions(predictions)
    print(final_result)
    logging.info(final_result)
    
    return render_template('ai_Results.html', prediction=final_result)
    
# Database Related
@app.route("/addUser/", methods=["POST"])
def addUser():
    user = request.get_json()
    cursor.execute('INSERT INTO users (username, email, password) VALUES ("{0}", "{1}", "{2}")'.format(user["username"], user["email"], user["password"]))
    conn.commit()
    return "Done"

@app.route("/getSpecificUser/", methods=["POST"])
def getSpecificUser():
    user = request.get_json()
    cursor.execute('SELECT * FROM users WHERE email = "{0}"'.format(user["email"]))
    result = cursor.fetchall()
    return jsonify(result=result)
    
@app.route("/updateUserDetails/", methods=["POST"])
def updateUserDetails():
    user = request.get_json()
    cursor.execute('UPDATE users SET username = "{0}", contact = "{2}", address = "{3}" WHERE email = "{1}"'.format(user["username"], user["email"], user["contact"], user["address"]))
    conn.commit()
    return "Done"

@app.route("/updateUserPassword/", methods=["POST"])
def updateUserPassword():
    user = request.get_json()
    cursor.execute('UPDATE users SET password = "{1}" WHERE email = "{0}"'.format(user["email"], user["password"]))
    conn.commit()
    return "Done"

@app.route("/updateUserFace/", methods=["POST"])
def updateUserFace():
    user = request.get_json()
    cursor.execute('UPDATE users SET faceImage = "{1}", face = "{2}" WHERE email = "{0}"'.format(user["email"], user["faceImage"], user["face"]))
    conn.commit()
    return "Done"

@app.route("/getUserPoints/", methods=["POST"])
def getUserPoints():
    user = request.get_json()
    cursor.execute('SELECT points FROM users WHERE email = "{0}"'.format(user["email"]))
    result = cursor.fetchall()
    return jsonify(result=result)

@app.route("/updateUserPoints/", methods=["POST"])
def updateUserPoints():
    user = request.get_json()
    cursor.execute('UPDATE users SET points = "{1}" WHERE email = "{0}"'.format(user["email"], user["points"]))
    conn.commit()
    return "Done"

    
if __name__ == "__main__":
    app.run()