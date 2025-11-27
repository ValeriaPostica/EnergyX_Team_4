from flask import Blueprint, request, jsonify
from sqlalchemy import create_engine, text
from werkzeug.security import generate_password_hash, check_password_hash
import re
import jwt
import datetime
from functools import wraps
import os

auth_bp = Blueprint('auth', __name__)

#db connection

DATABASE_URL = "postgresql://postgres:11111@localhost:5433/postgres"
engine = create_engine(DATABASE_URL)

# secret key for jwt
SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-this-in-production')

def validate_email(email):
	"""Checking whether email is valid"""
	pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
	return re.match(pattern, email) is not None

def validate_role(role):
	"""Checking whether role is valid"""
	return role in ['provider', 'consumer']

def generate_token(user_id, username, role):
	"""Generate JWT token for authenticated user"""
	payload = {
		'user_id': user_id,
		'username': username,
		'role': role,
		'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24),
		'iat': datetime.datetime.utcnow()
	}
	token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
	return token

def token_required(f):
	"""Decorator to protect routes - required valid jwt token"""
	@wraps(f)
	def decorated(*args, **kwargs):
		token = None

		#get token from authorization header
		if 'Authorization' in request.headers:
			auth_header = request.headers['Authorization']
			try:
				token = auth_header.split(" ")[1]
			except IndexError:
				return jsonify({'error': 'Invalid token format'}), 401
		
		if not token:
			return jsonify({'error': 'Token is missing'}), 401
		
		try:
			#decode and verify token
			data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
			current_user = {
				'user_id': data['user_id'],
				'username': data['username'],
				'role': data['role']
			}
		except jwt.ExpiredSignatureError:
			return jsonify({'error': 'Token has expired'}), 401
		except jwt.InvalidTokenError:
			return jsonify({'error': 'Invalid token'}), 401

		return f(current_user, *args, **kwargs)

	return decorated

@auth_bp.route('/register', methods=['POST'])
def register():
	"""Register a new user"""
	data = request.get_json()

	if not data:
		return jsonify({'error': 'No data provided'}), 400

	username = data.get('username')
	email = data.get('email')
	password = data.get('password')
	role = data.get('role')
	smart_meter_id = data.get('smart_meter_id')

	#check fields
	if not username:
		return jsonify({'error': 'Username is required'}), 400
	if not email:
		return jsonify({'error': 'Email is required'}), 400
	if not password:
		return jsonify({'error': 'Password is required'}), 400
	if not role:
		return jsonify({'error': 'Role is required'}), 400
	if not smart_meter_id:
		return jsonify({'error': 'Smart meter ID is required'}), 400

	#validate email format
	if not validate_email(email):
		return jsonify({'error': 'Invalid email format'}), 400

	#validate role
	if not validate_role(role):
		return jsonify({'error': 'Role must be either "provider" or "consumer"'}), 400

	try:
		with engine.connect() as conn:
			#checking if username already exists
			result = conn.execute(
				text("SELECT id FROM users WHERE username = :username"),
				{"username": username}
			)
			if result.fetchone():
				return jsonify({'error': 'Username already exists'}), 400

			#checking if email already exists
			result = conn.execute(
				text("SELECT id FROM users WHERE email = :email"),
				{"email": email}
			)
			if result.fetchone():
				return jsonify({'error': 'Email already exists'}), 400

			#hash the password
			hashed_password = generate_password_hash(password)

			#insert new user
			conn.execute(
				text("""
					INSERT INTO users (username, email, password, role, smart_meter_id)
					VALUES (:username, :email, :password, :role, :smart_meter_id)
				"""),
				{
					"username": username,
					"email": email,
					"password": hashed_password,
					"role": role,
					"smart_meter_id": smart_meter_id
				}
			)
			conn.commit()
			
			from leaderBoard import update_user_points
			update_user_points(username, 0)  # Start with 0 points

			return jsonify({
				'message': 'User registered successfully',
				'username': username,
				'role': role
			}), 201

	except Exception as e:
		return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
	"""Login user and return jwt token"""
	data = request.get_json()

	if not data:
		return jsonify({'error': 'No data provided'}), 400

	username = data.get('username')
	password = data.get('password')

	#checking fields
	if not username:
		return jsonify({'error': 'Username is required'}), 400
	if not password:
		return jsonify({'error': 'Password is required'}), 400

	try:
		with engine.connect() as conn:
			#get user from db
			result = conn.execute(
				text("SELECT id, username, email, password, role, smart_meter_id FROM users WHERE username = :username"),
				{"username": username}
			)
			user = result.fetchone()

			if not user:
				return jsonify({'error': 'Invalid username or password'}), 401

			if not check_password_hash(user[3], password):
				return jsonify({'error': 'Invalid username or password'}), 401

			#generate jwt token
			token = generate_token(user[0], user[1], user[4])

			#login successful
			return jsonify({
				'message': 'Login successful',
				'token': token,
				'user': {
					'id': user[0],
					'username': user[1],
					'email': user[2],
					'role': user[4],
					'smart_meter_id': user[5]
				}
			}), 200

	except Exception as e:
		return jsonify({'error': f'Login failed: {str(e)}'}), 500

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
	"""Logout user (token becomes invalid on client side)"""
	return jsonify({'message': 'Logout successful'}), 200

@auth_bp.route('/verify', methods=['GET'])
@token_required
def verify_token(current_user):
	"""Verify if token is valid and return user info"""
	return jsonify({
		'valid': True,
		'user': current_user
	}), 200