"""
Script to generate password hashes for multiple users.
Run this to get the hashes, then copy them to auth.py
"""
import bcrypt

def generate_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Define your users here
users = [
    ("operator2", "pass123", "Network Operator 2", "operator"),
    ("operator3", "pass456", "Network Operator 3", "operator"),
    ("john", "john123", "John Doe", "operator"),
    ("alice", "alice123", "Alice Smith", "operator"),
    ("bob", "bob123", "Bob Johnson", "operator"),
]

print("Copy these entries to fake_users_db in auth.py:\n")

for username, password, full_name, role in users:
    hash_value = generate_hash(password)
    print(f'    "{username}": {{')
    print(f'        "username": "{username}",')
    print(f'        "full_name": "{full_name}",')
    print(f'        "role": "{role}",')
    print(f'        # Password: {password}')
    print(f'        "hashed_password": "{hash_value}"')
    print(f'    }},')
    print()
