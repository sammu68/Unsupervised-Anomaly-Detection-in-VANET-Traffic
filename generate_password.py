"""
Helper script to generate bcrypt password hashes for new users.
Usage: python generate_password.py
"""
import bcrypt

def generate_hash(password: str) -> str:
    """Generate bcrypt hash for a password"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

if __name__ == "__main__":
    print("=== Password Hash Generator ===\n")
    
    # Generate hashes for multiple users
    users = [
        ("operator2", "pass123"),
        ("operator3", "pass456"),
        ("john", "john123"),
        ("alice", "alice123"),
        ("bob", "bob123"),
    ]
    
    print("Generated hashes for new users:\n")
    for username, password in users:
        hash_value = generate_hash(password)
        print(f'"{username}": {{')
        print(f'    "username": "{username}",')
        print(f'    "full_name": "{username.capitalize()}",')
        print(f'    "role": "operator",')
        print(f'    "hashed_password": "{hash_value}"')
        print('},\n')
    
    print("\n=== Custom Password ===")
    print("Enter a password to generate its hash (or press Enter to skip):")
    custom_password = input("Password: ").strip()
    
    if custom_password:
        custom_hash = generate_hash(custom_password)
        print(f"\nHash: {custom_hash}")
        print(f'\nAdd this to fake_users_db:')
        print(f'"username": {{')
        print(f'    "username": "username",')
        print(f'    "full_name": "Full Name",')
        print(f'    "role": "operator",  # or "admin"')
        print(f'    "hashed_password": "{custom_hash}"')
        print(f'}}')
