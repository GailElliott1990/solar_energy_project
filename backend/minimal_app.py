from flask import Flask, jsonify
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
auth = HTTPBasicAuth()

users = {
	"admin": generate_password_hash("password123"),
}

@auth.verify_password
def verify_password(username, password):
	if username in users and check_password_hash(users.get(username), password):
		return username
	return None

@app.route('/api/test', methods=['GET'])
@auth.login_required
def test():
	return jsonify({"message": "Minimal Flask API is working!"}), 200

if __name__ == '__main__':
	app.run(debug=True)