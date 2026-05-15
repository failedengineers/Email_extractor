import pandas as pd
import re

EMAIL_REGEX = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"


def extract_emails(file_path):
    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path, dtype=str)
    else:
        df = pd.read_excel(file_path, dtype=str)

    emails = set()

    for column in df.columns:
        for value in df[column].dropna():
            text = str(value)
            found_emails = re.findall(EMAIL_REGEX, text)
            for email in found_emails:
                emails.add(email.lower())

    return list(emails)