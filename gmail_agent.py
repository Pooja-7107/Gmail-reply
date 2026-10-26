
import os
import base64
import json

from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from google_auth_oauthlib.flow import InstalledAppFlow

from googleapiclient.discovery import build


# ============================================================
# GMAIL PERMISSIONS
# ============================================================

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose"
]


# ============================================================
# AUTHENTICATION
# ============================================================

def authenticate_gmail():

    credentials = None

    # --------------------------------------------------------
    # EXISTING TOKEN
    # --------------------------------------------------------

    if os.path.exists("token.json"):

        credentials = Credentials.from_authorized_user_file(
            "token.json",
            SCOPES
        )


    # --------------------------------------------------------
    # REFRESH TOKEN
    # --------------------------------------------------------

    if credentials and credentials.expired:

        if credentials.refresh_token:

            credentials.refresh(
                Request()
            )


    # --------------------------------------------------------
    # FIRST LOGIN
    # --------------------------------------------------------

    if not credentials or not credentials.valid:

        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json",
            SCOPES
        )

        credentials = flow.run_local_server(
            port=0
        )


        # Save authentication token

        with open(
            "token.json",
            "w"
        ) as token_file:

            token_file.write(
                credentials.to_json()
            )


    # --------------------------------------------------------
    # GMAIL SERVICE
    # --------------------------------------------------------

    service = build(
        "gmail",
        "v1",
        credentials=credentials
    )

    return service


# ============================================================
# GET EMAIL HEADER
# ============================================================

def get_header(
    headers,
    name
):

    for header in headers:

        if header["name"].lower() == name.lower():

            return header["value"]

    return ""


# ============================================================
# DECODE EMAIL BODY
# ============================================================

def decode_body(payload):

    body = ""

    # --------------------------------------------------------
    # SIMPLE EMAIL
    # --------------------------------------------------------

    if "body" in payload:

        data = payload["body"].get("data")

        if data:

            body = base64.urlsafe_b64decode(
                data
            ).decode(
                "utf-8",
                errors="ignore"
            )


    # --------------------------------------------------------
    # MULTIPART EMAIL
    # --------------------------------------------------------

    if "parts" in payload:

        for part in payload["parts"]:

            if part["mimeType"] == "text/plain":

                data = part["body"].get(
                    "data"
                )

                if data:

                    body += (
                        base64.urlsafe_b64decode(
                            data
                        ).decode(
                            "utf-8",
                            errors="ignore"
                        )
                    )


    return body


# ============================================================
# GET EMAILS
# ============================================================

def get_emails(
    service,
    max_results=10
):

    result = service.users().messages().list(

        userId="me",

        maxResults=max_results,

        labelIds=["INBOX"]

    ).execute()


    messages = result.get(
        "messages",
        []
    )


    emails = []


    for message in messages:

        email_data = service.users().messages().get(

            userId="me",

            id=message["id"],

            format="full"

        ).execute()


        payload = email_data.get(
            "payload",
            {}
        )


        headers = payload.get(
            "headers",
            []
        )


        sender = get_header(
            headers,
            "From"
        )


        subject = get_header(
            headers,
            "Subject"
        )


        date = get_header(
            headers,
            "Date"
        )


        body = decode_body(
            payload
        )


        emails.append({

            "id": message["id"],

            "sender": sender,

            "subject": subject,

            "date": date,

            "body": body

        })


    return emails


# ============================================================
# CREATE REPLY DRAFT
# ============================================================

def create_reply_draft(
    service,
    original_email,
    reply_text
):

    sender = original_email["sender"]

    subject = original_email["subject"]


    # Gmail reply subject

    if not subject.lower().startswith(
        "re:"
    ):

        subject = (
            "Re: " + subject
        )


    message = MIMEText(
        reply_text
    )


    message["To"] = sender

    message["Subject"] = subject


    raw_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()


    draft_body = {

        "message": {

            "raw": raw_message,

            "threadId": original_email["id"]

        }

    }


    draft = service.users().drafts().create(

        userId="me",

        body=draft_body

    ).execute()


    return draft
