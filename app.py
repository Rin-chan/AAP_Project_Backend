from flask import Flask, request, jsonify
from flaskext.mysql import MySQL

from models.faceVerification.siamese import generateDiss


app = Flask(__name__)

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'rin'
app.config['MYSQL_DATABASE_PASSWORD'] = '123456'
app.config['MYSQL_DATABASE_DB'] = 'aap_project'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)
conn = mysql.connect()
cursor = conn.cursor()


# FOR TESTING
@app.route("/")
def main() -> str:
    return "Hello World"


# AI Related
@app.route("/faceVerification/", methods=['POST'])
def faceVerification():
    input = request.get_json()
    result = generateDiss(input['originalFaceImage'], input['faceImage'])
    return jsonify(result=result)
    
    
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

    
if __name__ == "__main__":
    app.run()