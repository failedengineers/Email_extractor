ALLOWED_EXTENSIONS = [
    ".csv",
    ".xlsx"
]

MAX_FILE_SIZE = 5 * 1024 * 1024


def validate_uploaded_file(file):

    # file size
    if file.size > MAX_FILE_SIZE:
        return False, "File too large"

    # extension
    filename = file.name.lower()

    valid = False

    for ext in ALLOWED_EXTENSIONS:

        if filename.endswith(ext):
            valid = True
            break

    if not valid:
        return False, "Invalid file type"

    return True, None