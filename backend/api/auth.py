from flask import Blueprint, request, jsonify
from sqlalchemy import create_engine, text
from werkzeug.security import generate_password_hash, check_password_hash
import re

auth_bp = Blueprint('auth', __name__)

#db connection

DATABASE_URL = "postgresql://postgres:11111@localhost:5433/postgres"
engine = create_engine(DATABASE_URL)

def validate_email(email):
	"""Checking whether email is valid"""
	pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
	return re.match(pattern, email) is not None

def validate_role(role):
	"""Checking whether role is valid"""
	return role in ['provider', 'consumer']

#registering process...
@auth_bp.route('/register', methods=['POST'])
def register():
	"""Register a new user"""
	data = request.get_json()

	#vakidate required fields
	if not data:
		return jsonify({'error': 'No data provided'}), 400

	username = data.get('username')
	email = data.get('email')
	password = data.get('password')
	role = data.get('role')
	smart_meter_id = data.get('smart_meter_id')

	#check fields:
	if not username:
		return jsonify({'error': 'Username is required'}), 400
	if not email:
		return jsonify({'error': 'Email is required'}), 400
	if not password:
		return jsonify({'error': 'Password is required'}), 400
	if not role:
		return jsonify({'error': 'Role is required'}), 400

	#validate email folmat
	if not validate_email(email):
		return jsonify({'error': 'Invalid email format'}), 400

	#validate role
	if not validate_role(role):
		return jsonify({'error': 'Role must be either provider or consumer'}), 400

	#check if provider has a smart meter
	if role == 'provider' and not smart_meter_id:
		return jsonify({'error': 'Smart meter ID is required for providers'}), 400

	try:
		with engine.connect() as conn:
			#checking if username already exists
			result = conn.execute(
				text("SELECT id FROM users WHERE username =:username"),
				{"username":username}
			)
			if result.fetchone():
				return jsonify({'error': 'Username already exists'}), 400

			#checking if email already exists
			result = conn.execute(
				text("SELECT id FROM users WHERE email =:email"),
				{"email":email}
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

			return jsonify ({
				'message': 'User registered successfully',
				'username': username,
				'role': role
			}), 201

	except Exception as e:
		return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
	"""Login user"""
	data = request.get_json()

	if not data:
		return jsonify({'error': 'No data provded'}), 400

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
				text("SELECT id, username, password, role, smart_meter_id FROM users WHERE username = :username"),
				{"username": username}
			)
			user = result.fetchone()

			#check user and password
			if not user:
				return jsonify({'error': 'Invalid username or password'}), 401

			if not check_password_hash(user[3], password):
				return jsonify({'error': 'Invalid username or password'}), 401

			#login successful
			return jsonify({
				'message': 'Login successful',
				'user': {
					'id': user[0],
					'username': user[1],
					'email': user[2],
					'role': user[4],
					'smart_meter_id': user[5]
				}
			}), 200

	except Exception as e:
		return jsonify({'error': f'Login failed:{str(e)}'}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
	"""Logout user"""
	return jsonify({'message': 'Logout successful'}), 200