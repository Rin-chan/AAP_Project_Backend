from flask import Flask, request, jsonify
from flaskext.mysql import MySQL

from models.faceVerification.siamese import generateDiss
from models.binRouting.routing import getPath


app = Flask(__name__)

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'rin'
app.config['MYSQL_DATABASE_PASSWORD'] = '123456'
app.config['MYSQL_DATABASE_DB'] = 'aap_project'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)
conn = mysql.connect()
cursor = conn.cursor()

# GENERATE TABLE IF DOESN'T EXIST
cursor.execute("CREATE TABLE IF NOT EXISTS `users` (`id` int NOT NULL AUTO_INCREMENT,`username` varchar(100) NOT NULL,`email` varchar(100) NOT NULL,`password` longtext NOT NULL,`contact` varchar(8) DEFAULT '',`address` varchar(100) DEFAULT '',`face` tinyint DEFAULT '0',`faceImage` longtext,`points` int DEFAULT '0',PRIMARY KEY (`id`),UNIQUE KEY `id_UNIQUE` (`id`)) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci")
cursor.execute("CREATE TABLE IF NOT EXISTS `staff_users` (`id` int NOT NULL AUTO_INCREMENT,`username` varchar(100) NOT NULL,`email` varchar(100) NOT NULL,`password` longtext NOT NULL,PRIMARY KEY (`id`),UNIQUE KEY `id_UNIQUE` (`id`)) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci")
cursor.execute("CREATE TABLE IF NOT EXISTS `bins` (`id` int NOT NULL AUTO_INCREMENT,`location` varchar(100) NOT NULL,`capacity` varchar(100) NOT NULL,`selected` tinyint DEFAULT '0',`x` varchar(100),`y` varchar(100),PRIMARY KEY (`id`),UNIQUE KEY `id_UNIQUE` (`id`)) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci")
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

@app.route("/routing/", methods=['POST'])
def routing():
    cursor.execute('SELECT * FROM bins')
    binResult = cursor.fetchall()
    result = getPath(binResult)
    return jsonify(result=result)
    
    
# Database Related
# Consumer App
@app.route("/addUser/", methods=["POST"])
def addUser():
    user = request.get_json()
    
    conn = mysql.connect()  # reconnecting mysql
    with conn.cursor() as cursor:
        cursor.execute('INSERT INTO users (username, email, password) VALUES ("{0}", "{1}", "{2}")'.format(user["username"], user["email"], user["password"]))
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
    conn = mysql.connect()  # reconnecting mysql
    with conn.cursor() as cursor:         
        cursor.execute('SELECT COUNT(*) FROM users')
        result = cursor.fetchall()
    return jsonify(result=result)

@app.route("/getAllUsers/", methods=["POST"])
def getAllUser():
    req = request.get_json()
    
    offset = req["page"]*req["itemsPerPage"]
    
    conn = mysql.connect()  # reconnecting mysql
    with conn.cursor() as cursor:
        cursor.execute('SELECT * FROM users LIMIT {1} OFFSET {0}'.format(offset, req["itemsPerPage"]))
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

# Staff App
@app.route("/addStaffUser/", methods=["POST"])
def addStaffUser():
    user = request.get_json()
    
    conn = mysql.connect()  # reconnecting mysql
    with conn.cursor() as cursor:
        cursor.execute('INSERT INTO staff_users (username, email, password) VALUES ("{0}", "{1}", "{2}")'.format(user["username"], user["email"], user["password"]))
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
    conn = mysql.connect()  # reconnecting mysql
    with conn.cursor() as cursor:
        cursor.execute('SELECT COUNT(*) FROM staff_users')
        result = cursor.fetchall()
    return jsonify(result=result)

@app.route("/getStaffAllUsers/", methods=["POST"])
def getStaffAllUser():
    req = request.get_json()
    
    offset = req["page"]*req["itemsPerPage"]
    
    conn = mysql.connect()  # reconnecting mysql
    with conn.cursor() as cursor:
        cursor.execute('SELECT * FROM staff_users LIMIT {1} OFFSET {0}'.format(offset, req["itemsPerPage"]))
        result = cursor.fetchall()
        
    return jsonify(result=result)

@app.route("/getStaffBins/", methods=["POST"])
def getStaffBins():
    conn = mysql.connect()  # reconnecting mysql
    with conn.cursor() as cursor:
        cursor.execute('SELECT * FROM bins')
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

    
if __name__ == "__main__":
    app.run()