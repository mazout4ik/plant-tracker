import ssl
import certifi

paths = ssl.get_default_verify_paths()
print("openssl_cafile:", paths.openssl_cafile)
print("certifi where:", certifi.where())