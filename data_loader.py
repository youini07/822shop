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
    "https://www.googleapis.com/auth/drive.metadata.readonly",
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
        
        # Open the specific sheet (Find by name, Open by ID)
        # We list files to find the ID because names can be tricky
        spreadsheets = client.list_spreadsheet_files()
        
        # [MODIFIED] Search for "상품목록" ONLY.
        # We enforce "상품목록" usage.
        target_sheet = next((s for s in spreadsheets if s['name'] == '상품목록'), None)
        
        if target_sheet:
            sheet = client.open_by_key(target_sheet['id']).sheet1
        else:
            # If not found via list, try direct open
            try:
                sheet = client.open("상품목록").sheet1
            except Exception as e:
                st.error("Error: '상품목록' sheet not found. Please share the sheet with the service account.")
                raise e
            
        # Get all values (list of lists) to handle headers manually
        data = sheet.get_all_values()
        
        if not data:
            return pd.DataFrame()

        # Create DataFrame
        # Assume first row is header
        headers = data[0]
        rows = data[1:]
        
        df = pd.DataFrame(rows, columns=headers)
        
        # [MODIFIED] Column Mapping (Korean -> English Internal Names)
        # t_id -> code
        # brand -> brand
        # name -> name
        # category -> category
        # size -> size
        # condition -> condition
        # price -> price
        # description -> description
        # image_file_id -> image_file_id
        # stock -> stock
        
        column_mapping = {
            '제품번호': 'code',
            't_id': 'code',
            'cc': 'code',
            '브랜드': 'brand',
            '물품명': 'name',
            '카테고리': 'category',
            '사이즈': 'size',
            '컨디션': 'condition',
            '판매가': 'price',
            '제품설명': 'description',
            '이미지': 'image_file_id',
            '상태': 'stock',
            '등록일': 'updated_at',
            '도착예정일': 'arrival_date', 'eta': 'arrival_date', 'ETA': 'arrival_date'
        }
        
        # Normalize headers (strip whitespace)
        df.columns = [str(c).strip() for c in df.columns]
        
        # Apply mapping
        df.rename(columns=column_mapping, inplace=True)
        
        # Normalize headers to lowercase to avoid case sensitivity issues for mapped columns
        df.columns = [str(c).lower().strip() for c in df.columns]
        
        # [Safety Net] Ensure 'code' column exists. If not, assume the first column is 'code'.
        if 'code' not in df.columns and not df.empty:
            cols = list(df.columns)
            cols[0] = 'code'
            df.columns = cols

        # [MODIFIED] Image Fallback Logic
        fallback_image_url = "https://drive.google.com/thumbnail?id=1Wk4sdliFYg8I8TvyDkUFWgemxXKq9fwB&sz=w1000"
        # The user provided a view link: "https://drive.google.com/file/d/1Wk4sdliFYg8I8TvyDkUFWgemxXKq9fwB/view?usp=drive_link"
        # Extracted ID: 1Wk4sdliFYg8I8TvyDkUFWgemxXKq9fwB
        
        if 'image_file_id' in df.columns:
            # Replace empty strings, NaN, or strict whitespace with Fallback ID/URL
            # NOTE: get_image_url handles the ID extraction. We can just put the ID '1Wk4sdliFYg8I8TvyDkUFWgemxXKq9fwB'
            # OR we can pre-fill it.
            # Let's clean the column first.
            df['image_file_id'] = df['image_file_id'].astype(str).str.strip()
            
            # Identify "empty" values
            empty_mask = (df['image_file_id'] == '') | (df['image_file_id'].str.lower() == 'nan') | (df['image_file_id'].str.lower() == 'none')
            
            # Assign fallback ID
            df.loc[empty_mask, 'image_file_id'] = '1Wk4sdliFYg8I8TvyDkUFWgemxXKq9fwB'
        
        # Ensure price is numeric
        if 'price' in df.columns:
            # Handle cases where price might include currency symbols or commas
            df['price'] = (
                df['price']
                .astype(str)
                .str.replace(r'[^\d]', '', regex=True) # Keep only digits
            )
            df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0).astype(int)
            
        # Attach Metadata: Source Sheet Name
        if target_sheet:
             df.attrs['source_sheet'] = target_sheet['name']
        else:
             df.attrs['source_sheet'] = "Unknown (Fallback)"

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
