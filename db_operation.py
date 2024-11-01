# db_operations.py
from database import db_query

def check_username_exists(username):
    query = f"SELECT username FROM customers WHERE username = '{username}';"
    result = db_query(query)
    return bool(result)

def check_account_number_exists(account_number):
    query = f"SELECT account_number FROM customers WHERE account_number = '{account_number}';"
    result = db_query(query)
    return bool(result)

def get_password(username):
    query = f"SELECT password FROM customers WHERE username = '{username}';"
    result = db_query(query)
    return result[0][0] if result else None