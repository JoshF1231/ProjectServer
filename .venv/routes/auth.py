import bcrypt
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from server import mysql
from werkzeug.security import generate_password_hash, check_password_hash
from MySQLdb.cursors import DictCursor  # Import DictCursor
from flask_bcrypt import Bcrypt


bp = Blueprint('auth', __name__)

@bp.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            return jsonify({"error":"All fields are required"}),400

        salt = bcrypt.gensalt()
        #hashed_password = generate_password_hash(password)
        hashed = bcrypt.hashpw(password.encode('utf-8'),salt)
        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT into users (username, email, password) VALUES (%s, %s, %s)",
            (username,email,hashed.decode('utf-8'))
        )
        mysql.connection.commit()
        cursor.close()
        return jsonify({"message":"User registered successfully"}),201
    except Exception as e:
        return jsonify({"error" : str(e)}), 500

@bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400
    cur = mysql.connection.cursor(DictCursor)
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cur.fetchone()
    cur.close()
    if bcrypt.checkpw(password.encode('utf-8'),user['password'].encode('utf-8')):
        access_token = create_access_token(identity=username)
        return jsonify(access_token),200
    else:
        return jsonify({"error": "Incorrect username or password"}),401
#    if user and check_password_hash(user['password'],password):
#        return jsonify({"message":"Succesfully logged in !"}),201

