import os
import os.path
import ssl
import stat
import subprocess
import sys

import certifi

STAT_0o775 = (
    stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR
    | stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP
    | stat.S_IROTH | stat.S_IXOTH
)

def main():
    # Where Python thinks the OpenSSL CA file is
    default_paths = ssl.get_default_verify_paths()
    openssl_dir, openssl_cafile = os.path.split(default_paths.openssl_cafile)

    print("Default OpenSSL dir:", openssl_dir)
    print("Default OpenSSL cafile:", openssl_cafile)

    # Upgrade certifi to latest
    print(" -- upgrading certifi")
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "--upgrade", "certifi"]
    )

    cafile = certifi.where()
    print("Certifi cafile:", cafile)

    # Ensure OpenSSL dir exists
    os.makedirs(openssl_dir, exist_ok=True)
    os.chdir(openssl_dir)

    # Remove existing CA file if present
    try:
        os.remove(openssl_cafile)
        print(" -- removed existing", openssl_cafile)
    except FileNotFoundError:
        print(" -- no existing", openssl_cafile)

    # Try to symlink certifi’s bundle; if that fails, copy it
    try:
        os.symlink(cafile, openssl_cafile)
        print(" -- symlink created")
    except (AttributeError, NotImplementedError, OSError):
        import shutil
        shutil.copyfile(cafile, openssl_cafile)
        print(" -- copied certifi bundle")

    os.chmod(openssl_cafile, STAT_0o775)
    print(" -- update complete")

if __name__ == "__main__":
    main()