import os
import base64
import hmac
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from datetime import datetime

def decrypt(e, t="server_date_time", n="client_date_time"):
    # Convert strings to bytes
    iv = n.encode('utf-8')
    key = t.encode('utf-8')

    # Decode the base64 encoded string
    e_bytes = base64.b64decode(e)

    # Initialize AES cipher
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    # Decrypt and unpad the data
    decrypted = unpad(cipher.decrypt(e_bytes), AES.block_size)

    return decrypted.decode('utf-8')

def xcode(t):
    e = ''.join([os.urandom(1).hex() for _ in range(36)])  # Generate a random UUID-like string
    current_time = int(datetime.now().timestamp() * 1000)  # Current time in milliseconds
    r = f"seat::{e}::{current_time}::{t.upper()}"
    
    # Decrypt the Global.NUMCODE (example value)
    o = decrypt("cDf+jadFUWncEn536MXItw==")  # Replace with your actual Global.NUMCODE
    
    # Generate HMAC
    request_key = hmac.new(o.encode('utf-8'), r.encode('utf-8'), hashlib.sha256).hexdigest()
    
    return e, str(current_time), request_key

# # Example usage
# if __name__ == "__main__":
#     result = xcode("GET")  # Example request type
#     print(result)