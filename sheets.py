import json
import os
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_sheet():
    creds_json = json.loads(os.getenv("GOOGLE_CREDENTIALS_JSON"))

    creds = Credentials.from_service_account_info(
        creds_json,
        scopes=SCOPES
    )

    client = gspread.authorize(creds)
    return client.open("mensajes_bot").sheet1


def guardar_mensaje(user_id, text, respuesta):
    sheet = get_sheet()
    sheet.append_row([
        str(datetime.now()),
        user_id,
        text,
        respuesta
    ])