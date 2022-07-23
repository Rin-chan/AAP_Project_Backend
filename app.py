from flask import Flask, request, jsonify

from models.faceVerification.siamese import generateDiss


app = Flask(__name__)

@app.route("/")
def main() -> str:
    return "Hello World"

@app.route("/faceVerification/", methods=['POST'])
def faceVerification():
    input = request.get_json()
    
    result = generateDiss(input['originalFaceImage'], input['faceImage'])
    
    return jsonify(result=result)
    
if __name__ == "__main__":
    app.run()