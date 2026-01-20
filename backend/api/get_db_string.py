
import os


def get_db_string():
	"""Retrieve database connection info from environment variables"""
	db_host = os.getenv('DB_HOST', 'localhost')
	db_port = os.getenv('DB_PORT', '5433')
	db_name = os.getenv('DB_NAME', 'postgres')
	db_user = os.getenv('DB_USER', 'postgres')
	db_password = os.getenv('DB_PASSWORD', '11111')
	return f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
