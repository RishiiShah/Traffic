import os
import boto3

import shutil


def resolve_wkhtmltopdf_path() -> str | None:
    """Locate the wkhtmltopdf binary in a cross-platform way.

    Order of preference:
      1. WKHTMLTOPDF_PATH env var (explicit override)
      2. a `wkhtmltopdf` binary found on PATH (Linux/macOS via brew/apt)
      3. the default Windows install location
    Returns None if nothing is found, in which case pdfkit falls back to
    whatever is on PATH.
    """
    env_path = os.getenv("WKHTMLTOPDF_PATH")
    if env_path and os.path.exists(env_path):
        return env_path

    on_path = shutil.which("wkhtmltopdf")
    if on_path:
        return on_path

    windows_default = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
    if os.path.exists(windows_default):
        return windows_default

    return None


def upload_to_s3(file_path: str,
                 bucket_name: str,
                 region: str,
                 s3_prefix: str = "pdfs/") -> str:
    """
    Uploads `file_path` to S3, under `s3_prefix + basename`, and returns its HTTPS URL.
    Expects AWS creds & region either in env vars or passed here.
    """
    client = boto3.client(
        "s3",
        aws_access_key_id     = os.getenv("AWS_ACCESS_KEY"),
        aws_secret_access_key = os.getenv("AWS_SECRET_KEY"),
        region_name           = region
    )
    key = os.path.join(s3_prefix, os.path.basename(file_path))
    client.upload_file(file_path, bucket_name, key)
    return f"https://{bucket_name}.s3.{region}.amazonaws.com/{key}"
