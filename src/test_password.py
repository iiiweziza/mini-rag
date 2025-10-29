#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

from models.db_schemes.minirag.schemes.user import User
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_password_processing():
    print("Testing password processing...")
    
    # Test with a simple password
    test_password = "password123"
    print(f"Test password: '{test_password}'")
    print(f"Test password length: {len(test_password)}")
    print(f"Test password type: {type(test_password)}")
    
    # Check the bytes
    password_bytes = test_password.encode('utf-8')
    print(f"Password bytes: {password_bytes}")
    print(f"Password bytes length: {len(password_bytes)}")
    
    try:
        print("Attempting to hash password...")
        hashed = User.hash_password(test_password)
        print(f"Hashed password: {hashed}")
        
        print("Attempting to verify password...")
        result = User.verify_password(User(), test_password)  # Create a dummy user instance
        print(f"Verification result: {result}")
        
    except Exception as e:
        print(f"Error during password processing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_password_processing()