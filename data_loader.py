import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import traceback
import requests
from io import BytesIO

# Define the scope
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.readonly",
]

@st.cache_data(ttl=600)
def load_data():
    """
    Connects to Google Sheets and loads the product data into a Pandas DataFrame.
    """
    try:
        # Load credentials from secrets.toml
        secrets = st.secrets["gcp_service_account"]
        
        # Create credentials object
        creds = Credentials.from_service_account_info(
            secrets, scopes=SCOPES
        )
        
        # Authorize gspread
        client = gspread.authorize(creds)
        
        # DEBUG: Check visible sheets
        # st.write(f"Connected as: {creds.service_account_email}") 
        # spreadsheets = client.list_spreadsheet_files()
        # st.write(f"Visible Sheets: {[s['name'] for s in spreadsheets]}")
        
        # Open the specific sheet (Find by name, Open by ID)
        # We list files to find the ID because names can be tricky
        spreadsheets = client.list_spreadsheet_files()
        target_sheet = next((s for s in spreadsheets if s['name'] in ['DB_Products', 'DB_products']), None)
        
        if target_sheet:
            sheet = client.open_by_key(target_sheet['id']).sheet1
        else:
            # If not found via list, try direct open as fallback
            sheet = client.open("DB_Products").sheet1
            
        # Get all records
        data = sheet.get_all_records()
        
        if not data:
            return pd.DataFrame()

        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Ensure price is numeric
        if 'price' in df.columns:
            df['price'] = pd.to_numeric(df['price'].astype(str).str.replace(',', ''), errors='coerce').fillna(0).astype(int)
            
        return df
        
    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
        st.code(traceback.format_exc()) # Print full traceback
        return pd.DataFrame()

def get_image_url(file_id):
    """
    Converts a Google Drive File ID (or URL) into a direct viewable URL.
    """
    if not file_id or pd.isna(file_id):
        return None
    
    file_id = str(file_id).strip()
    
    import re
    patterns = [
        r'/d/([a-zA-Z0-9_-]+)',  # /file/d/ID/...
        r'id=([a-zA-Z0-9_-]+)',  # ...?id=ID
        r'^([a-zA-Z0-9_-]+)$'    # Just the ID
    ]
    
    for pattern in patterns:
        match = re.search(pattern, file_id)
        if match:
            clean_id = match.group(1)
            # Use thumbnail link for better embedding reliability (size=w1000 for high quality)
            return f"https://drive.google.com/thumbnail?id={clean_id}&sz=w1000"

    # Fallback and Original
    return f"https://drive.google.com/thumbnail?id={file_id}&sz=w1000"

@st.cache_data(ttl=3600*24, show_spinner=False)
def fetch_image_from_url(url):
    """
    Fetches image bytes from a URL to bypass browser-side blocking.
    """
    if not url:
        return None
    try:
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            return BytesIO(response.content)
    except Exception:
        return None
    return None
