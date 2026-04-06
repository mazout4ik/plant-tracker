import ssl
import certifi

# Force default HTTPS context to use certifi's CA bundle
_original_create_default_context = ssl.create_default_context

def _patched_default_context(*args, **kwargs):
    # Always use certifi's CA file
    kwargs["cafile"] = certifi.where()
    return _original_create_default_context(*args, **kwargs)

ssl.create_default_context = _patched_default_context
ssl._create_default_https_context = _patched_default_context