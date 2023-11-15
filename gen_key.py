import sys
import os
import secrets

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py secret/api")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "api":
        print(secrets.token_urlsafe(32))
    elif command == "secret":
        print(os.urandom(24).hex())
    else:
        print(command + " not valid use secret/api")
        sys.exit(2)
