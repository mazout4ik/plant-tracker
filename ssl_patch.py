import ssl
import certifi

# Force default HTTPS context to use certifi's CA bundle
ssl._create_default_https_context = ssl.create_default_context
ssl._create_default_https_context = lambda *args, **kwargs: ssl.create_default_context(cafile=certifi.where())