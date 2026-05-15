import os

ALLOWED_EXTENSIONS = {".xlsx", ".csv",}
MAX_FILE_SIZE_MB = 5


def validate_uploaded_file(uploaded_file):
    ext = os.path.splitext(uploaded_file.name)[1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Unsupported file type: {ext}"

    if uploaded_file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
        return False, f"File too large. Max size is {MAX_FILE_SIZE_MB}MB"

    return True, None
