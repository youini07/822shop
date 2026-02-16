import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import hashlib
from datetime import datetime
import time

# --- Constants ---
SHEET_CUSTOMERS = "고객정보"
SHEET_WISHLIST = "찜목록"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

class AuthManager:
    def __init__(self):
        self.client = self._connect_google_sheets()
        self.sh = self._get_or_open_spreadsheet()
        
        # Ensure sheets exist
        self.worksheet_customers = self._ensure_sheet(SHEET_CUSTOMERS, [
            'user_id', 'password', 'name', 'phone', 'address', 'zipcode', 'line_id', 'created_at'
        ])
        self.worksheet_wishlist = self._ensure_sheet(SHEET_WISHLIST, [
            'user_id', 'product_code', 'created_at'
        ])

    @st.cache_resource
    def _connect_google_sheets(_self):
        """Connect to Google Sheets using Streamlit secrets."""
        try:
            creds = Credentials.from_service_account_info(
                st.secrets["gcp_service_account"], scopes=SCOPES
            )
            return gspread.authorize(creds)
        except Exception as e:
            st.error(f"Google Sheets 연결 실패: {e}")
            return None

    def _get_or_open_spreadsheet(self):
        """Open the main spreadsheet."""
        try:
            # Try opening by name "상품목록" (as per data_loader.py logic context)
            # OR list and pick first. To be safe, we assume "상품목록" exists or we find the right one.
            # Ideally data_loader should share this, but for now we look for "DB_Products" or similar if known,
            # but user said "saved to 'Customer Info' spreadsheet". 
            # We will use the SAME spreadsheet as the product catalog for simplicity unless specified otherwise.
            # Let's try to find a spreadsheet named "822Shop_DB" or just use the first one found if specific name unknown.
            # Actually, `data_loader.py` logic prioritizes "상품목록". We should probably use that same spreadsheet file
            # to keep everything in one place, or create a new one?
            # User said "save to '고객정보' spreadsheet". It implies a sheet inside a file.
            # Let's try to open "상품목록" file first.
            
            # For robustness, we search for the spreadsheet accessible.
            # Since we validated write permissions on "상품목록" (or whatever file was found), we use that.
            
            # Simplified: List and take the first one, or search for "상품목록".
            # NOTE: In data_loader.py, it searches for "상품목록".
            for file in self.client.list_spreadsheet_files():
                if file['name'] == "상품목록":
                    return self.client.open_by_key(file['id'])
            
            # Fallback: Open the first one if "상품목록" not found (unlikely if app is running)
            all_sheets = self.client.list_spreadsheet_files()
            if all_sheets:
                return self.client.open_by_key(all_sheets[0]['id'])
                
            return None
        except Exception as e:
            st.error(f"스프레드시트 열기 실패: {e}")
            return None

    def _ensure_sheet(self, title, headers):
        """Ensure a worksheet exists with given headers."""
        if self.sh is None: return None
        
        try:
            ws = self.sh.worksheet(title)
            # Check headers? (Optional)
            return ws
        except gspread.WorksheetNotFound:
            # Create new
            ws = self.sh.add_worksheet(title=title, rows="100", cols=str(len(headers)))
            ws.append_row(headers)
            return ws

    def _hash_password(self, password):
        """SHA-256 password hashing."""
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, user_data):
        """
        Register a new user.
        user_data: dict with id, pw, name, phone, address, zipcode, line_id
        Returns: (success: bool, message: str)
        """
        if self.worksheet_customers is None:
            return False, "데이터베이스 연결 오류"

        user_id = user_data['user_id']
        
        # Check duplicate ID
        # Get all records is expensive, but for MVP it's okay. 
        # For scale, we'd cache this or use cell find.
        try:
            cell = self.worksheet_customers.find(user_id, in_column=1)
            if cell:
                return False, "이미 존재하는 아이디입니다."
        except:
            pass # ID not found is good

        # Hashing
        hashed_pw = self._hash_password(user_data['password'])
        
        # Append row
        row = [
            user_id,
            hashed_pw,
            user_data['name'],
            user_data['phone'],
            user_data['address'],
            user_data['zipcode'],
            user_data.get('line_id', ''),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ]
        
        try:
            self.worksheet_customers.append_row(row)
            return True, "회원가입이 완료되었습니다."
        except Exception as e:
            return False, f"저장 중 오류 발생: {e}"

    def login_user(self, user_id, password):
        """
        Verify credentials.
        Returns: (success: bool, user_info: dict/None, message: str)
        """
        if self.worksheet_customers is None:
            return False, None, "데이터베이스 연결 오류"

        try:
            cell = self.worksheet_customers.find(user_id, in_column=1)
            if not cell:
                return False, None, "존재하지 않는 아이디입니다."
            
            # Fetch row data
            row_data = self.worksheet_customers.row_values(cell.row)
            # Row structure: [id, pw, name, phone, ...]
            stored_pw = row_data[1]
            
            if self._hash_password(password) == stored_pw:
                # Login Success
                user_info = {
                    'user_id': row_data[0],
                    'name': row_data[2],
                    'phone': row_data[3]
                }
                return True, user_info, "로그인 성공"
            else:
                return False, None, "비밀번호가 일치하지 않습니다."
        except Exception as e:
            return False, None, f"로그인 처리 중 오류: {e}"

    def get_user_info(self, user_id):
        """
        Get user info by ID (for auto-login via cookie).
        Returns: (success: bool, user_info: dict/None)
        """
        if self.worksheet_customers is None: return False, None

        try:
            cell = self.worksheet_customers.find(user_id, in_column=1)
            if not cell:
                return False, None
            
            row_data = self.worksheet_customers.row_values(cell.row)
            # Row structure: [id, pw, name, phone, ...]
            user_info = {
                'user_id': row_data[0],
                'name': row_data[2],
                'phone': row_data[3]
            }
            return True, user_info
        except Exception as e:
            return False, None

    def toggle_like(self, user_id, product_code):
        """Toggle like status for a product."""
        if self.worksheet_wishlist is None: return False

        # Check if already liked
        # We need to find a row where col1=user_id AND col2=product_code
        # Gspread doesn't support multi-col find natively/easily.
        # MVP Strategy: Load all rows filter in python (caching advised for scale).
        # Better MVP: Append "ADD" or "REMOVE" audit log? No, user wants state.
        # Let's fetch all records for this user?
        
        try:
            records = self.worksheet_wishlist.get_all_values()
            # Skip header [0] if exists, but logic handles it
            
            row_to_delete = None
            for idx, row in enumerate(records):
                if idx == 0: continue # Header
                if len(row) >= 2 and row[0] == user_id and row[1] == str(product_code):
                    row_to_delete = idx + 1 # 1-based index
                    break
            
            if row_to_delete:
                self.worksheet_wishlist.delete_rows(row_to_delete)
                return "removed"
            else:
                self.worksheet_wishlist.append_row([
                    user_id, 
                    str(product_code), 
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ])
                return "added"
        except Exception as e:
            print(f"Error toggling like: {e}")
            return "error"

    def get_user_likes(self, user_id):
        """Get set of product codes liked by user."""
        if self.worksheet_wishlist is None: return set()
        try:
            records = self.worksheet_wishlist.get_all_values()
            likes = set()
            for idx, row in enumerate(records):
                if idx == 0: continue
                if len(row) >= 2 and row[0] == user_id:
                    likes.add(row[1])
            return likes
        except:
            return set()

    def get_all_like_counts(self):
        """Get dict of {product_code: count}."""
        if self.worksheet_wishlist is None: return {}
        try:
            records = self.worksheet_wishlist.get_all_values()
            counts = {}
            for idx, row in enumerate(records):
                if idx == 0: continue
                if len(row) >= 2:
                    p_code = row[1]
                    counts[p_code] = counts.get(p_code, 0) + 1
            return counts
        except:
            return {}
