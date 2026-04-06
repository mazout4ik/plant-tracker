import httpx
import contextlib

@contextlib.contextmanager
def no_ssl_verification():
    """
    Temporarily disable SSL verification for httpx.Client
    (affects libraries like supabase-py which use httpx under the hood).
    """
    # Save original Client
    OriginalClient = httpx.Client

    # New Client that forces verify=False
    def PatchedClient(*args, **kwargs):
        kwargs["verify"] = False
        return OriginalClient(*args, **kwargs)

    httpx.Client = PatchedClient
    try:
        yield
    finally:
        # Restore original
        httpx.Client = OriginalClient