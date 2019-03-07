import os
import json
import requests
import time
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import copy

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/docx', methods=['POST'])
@cross_origin()
def docx():
    x = request.get_json()
    print(x)
    return "Your file has been successfully converted to a docx", 200
    


if __name__ == '__main__':
    app.run(debug=True, port=5000)
