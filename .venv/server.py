from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from flask_bcrypt import Bcrypt



app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_USER'] = 'task_manager'
app.config['MYSQL_PASSWORD'] = 'qweQWE123!@#'
app.config['MYSQL_DB'] = 'task_manager'
app.config['JWT_SECRET_KEY'] = 'secretSECRET123!@#'




mysql= MySQL(app)
jwt = JWTManager(app)
CORS(app)
Bcrypt(app)

def register_blueprints():
    from routes import auth
    app.register_blueprint(auth.bp)

if __name__ == '__main__':
    register_blueprints()
    app.run(debug=True)