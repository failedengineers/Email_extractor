import re

EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"


def extract_emails(file_path):
    emails = []

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            found = re.findall(EMAIL_REGEX, line)
            if found:
                emails.extend(found)

    return emails
