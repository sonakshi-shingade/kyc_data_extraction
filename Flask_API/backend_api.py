import pytesseract
print("Hello")
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import base64
from PIL import Image  # pillow module base 64 into bytes into image conversion
import io    # converts the generated base 64 into bytes
import uuid

from pan_extract import PanCardDetails   # provides a unique ID 

app = Flask(__name__) 
CORS(app)

pan_extract = PanCardDetails()

# MongoDB connection (Update with your MongoDB URI)
client = MongoClient("mongodb://localhost:27017")  # or MongoDB Atlas URI
db = client["kyc_db"]
users_collection = db["users"]
kyc_collection = db["kyc_records"]

# Helper to generate unique ID
def generate_id():
    return str(uuid.uuid4())

# Register
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if users_collection.find_one({"username": username}):
        return jsonify({"message": "Username already exists"}), 400

    users_collection.insert_one({"username": username, "password": password})
    return jsonify({"message": "Registration successful"}), 200

# Login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = users_collection.find_one({"username": username, "password": password})
    if not user:
        return jsonify({"message": "Invalid username or password"}), 401

    return jsonify({"message": "Login successful"}), 200

# Upload KYC
@app.route('/upload-kyc', methods=['POST'])
def upload_kyc():
    data = request.get_json()
    username = data.get("username")
    image_b64 = data.get("image_b64")

    if not username or not image_b64:
        return jsonify({"error": "Missing data"}), 400

    record_id = generate_id()
    kyc_data = {
        "id": record_id,
        "name": username,
        "doc_type": "image",
        "image_b64": image_b64
    }

    kyc_collection.insert_one(kyc_data)
    return jsonify({"message": "KYC uploaded", "record_id": record_id}), 200

# Get KYC Records
@app.route('/kyc-records/<username>', methods=['GET'])
def get_kyc_records(username):
    records = list(kyc_collection.find({"name": username}, {"_id": 0, "image_b64": 0}))  # Exclude _id, image
    return jsonify(records), 200

# Get KYC Details
@app.route('/kyc-details/<record_id>', methods=['GET'])
def get_kyc_details(record_id):
    record = kyc_collection.find_one({"id": record_id}, {"_id": 0})
    if not record:
        return jsonify({"error": "Record not found"}), 404
    return jsonify(record), 200

# New Endpoint: Extract text from KYC document using pytesseract
@app.route('/extract-text-from-kyc', methods=['POST'])
def extract_text_from_kyc():
    data = request.get_json()
    image_b64 = data.get("image_b64")

    if not image_b64:
        return jsonify({"error": "No image data provided"}), 400

    try:
        # Decode the base64 image
        image_data = base64.b64decode(image_b64.split(",")[1])  # Remove the 'data:image/png;base64,' part
        image = Image.open(io.BytesIO(image_data))

        details_dict = pan_extract.get_pan_details(file = image)
        return jsonify(details_dict), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)