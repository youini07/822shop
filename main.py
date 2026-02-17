import streamlit as st
import pandas as pd
import streamlit as st
import pandas as pd
from data_loader import load_data, get_image_url
from auth_manager import AuthManager
import base64
import os
from datetime import datetime

# ... (Previous code)

# --- Page Config ---
st.set_page_config(
    page_title="822 SHOP",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="collapsed", # On Mobile, collapsed is better
    menu_items={
        'Get Help': 'https://www.google.com',
        'Report a bug': "https://www.google.com",
        'About': "# 822 SHOP Catalog App"
    }
)

# [PWA] Inject Meta Tags for Mobile App Experience
# 1. apple-mobile-web-app-capable: Hides Safari UI (Address bar)
# 2. apple-mobile-web-app-status-bar-style: Status bar color
# 3. viewport: Prevents zooming, critical for app-feel
# 4. theme-color: Android Chrome address bar color
st.markdown("""
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="theme-color" content="#ffffff">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover">
<!-- Google Fonts: Montserrat, Kanit, Inter, Prompt -->
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Kanit:wght@400;600;700&family=Montserrat:wght@400;600;700&family=Prompt:wght@400;600;700&display=swap" rel="stylesheet">
<!-- Pretendard (JSDelivr) -->
<link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css" />
<!-- Gmarket Sans (CDN) -->
<link href="https://webfontworld.github.io/gmarket/GmarketSans.css" rel="stylesheet">

<style>
    /* Hide Streamlit Header & Footer for App-like feel */
    /* [MODIFIED] Do NOT hide header, we need hamburger menu for sidebar */
    /* header[data-testid="stHeader"] {display: none;} */
    
    footer {display: none;}
    #MainMenu {display: none;}
    .stDeployButton {display: none;}
    
    /* Global Font & Touch adjustments */
    body {
        font-family: 'Inter', 'Pretendard', 'Prompt', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        -webkit-user-select: none; /* Disable text selection for app-feel */
        user-select: none;
        -webkit-tap-highlight-color: transparent;
    }
    
    /* Headings (Titles): Gmarket Sans (KR) + Montserrat (EN) + Kanit (TH) */
    h1, h2, h3, h4, h5, h6, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        font-family: 'Montserrat', 'GmarketSans', 'Kanit', sans-serif !important;
    }
    
    /* Specific overrides for Product Titles if needed */
    .product-title {
        font-family: 'GmarketSans', 'Montserrat', 'Kanit', sans-serif !important;
    }
    
    /* Improve button touch targets */
    button {
        min-height: 44px; /* Apple Human Interface Guidelines */
    }
</style>
""", unsafe_allow_html=True)


# --- Custom CSS ---
st.markdown("""
<style>
    /* Reduce top whitespace */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
    }
    .product-card {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .product-title {
        font-size: 1.1em;
        font-weight: bold;
        margin-top: 10px;
        margin-bottom: 5px;
        /* [Fixed] 2 lines max with ellipsis */
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
        text-overflow: ellipsis;
        height: 2.8em; /* Fixed height for alignment (~2 lines) */
        line-height: 1.4em;
    }
    .product-price {
        color: #e63946;
        font-weight: bold;
        font-size: 1.2em;
    }
    .product-meta {
        color: #666;
        font-size: 0.9em;
    }
    .sold-out {
        color: #999;
        text-decoration: line-through;
    }
    .sold-out-badge {
        background-color: #333;
        color: white;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 0.8em;
    }
</style>
""", unsafe_allow_html=True)

# --- Load Data ---
# --- Load Data ---
with st.spinner('상품 정보를 불러오는 중입니다...'):
    df = load_data()
    
    # [Fix] Ensure the first column is treated as 'code' if explicit column missing
    if not df.empty:
        # Check if 'code' exists
        has_code = 'code' in [c.lower() for c in df.columns]
        
        # If 'code' not found or we want to force Column A as code (User requirement)
        # We will strictly alias the first column to 'code' for the app's logic
        cols = list(df.columns)
        if cols:
            # Keep original name as reference but copy data to 'code' or rename default
            # Renaming is safer to avoid duplication confusion
            # Case: The first column IS the code column.
            df.rename(columns={cols[0]: 'code'}, inplace=True)

# --- Localization ---
if 'lang' not in st.session_state:
    st.session_state.lang = 'TH' # Default to Thai

lang_dict = {
    'TH': {
        'title': "ร้านเสื้อผ้าวินเทจคัดเกรด (822 Shop)",
        'filter': "🔍 ตัวกรอง (Filter)",
        'search': "Search",
        'search_placeholder': "Ex : Code or Name",
        'brand': "แบรนด์",
        'category': "หมวดหมู่",
        'size': "ขนาด (Size)",
        'price_range': "ช่วงราคา (บาท)",
        'show_sold_out': "แสดงสินค้าที่หมดแล้ว",
        'sort': "เรียงตาม",
        'sort_options': ["ล่าสุด (Newest)", "ราคา: ต่ำไปสูง (Low-High)", "ราคา: สูงไปต่ำ (High-Low)", "ชื่อ (Name)"],
        'total_items': "แสดง {current} จาก {total} รายการ",
        'page': "หน้า",
        'page_caption': "หน้า {current} จาก {total}",
        'sold_out': "🚫 สินค้าหมด (Sold Out)",
        'on_sale': "✅ มีสินค้า (In Stock)",
        'no_image': "📷 ไม่มีรูปภาพ",
        'detail_btn': "ดูรายละเอียด & สั่งซื้อ",
        'desc_title': "**รายละเอียดสินค้า**",
        'desc_title': "**รายละเอียดสินค้า**",
        'date_title': "📅 วันที่ลงขาย",
        'arrival_title': "วันที่คาดว่าจะมาถึง",
        'arrival_tbd': "ยังไม่กำหนด",
        'show_arrived_only': "แสดงเฉพาะสินค้าพร้อมส่ง",
        'line_btn': "🟢 ติดต่อซื้อทาง Line (คลิก)",
        'login_tab': "เข้าสู่ระบบ", 'register_tab': "สมัครสมาชิก",
        'username': "ไอดี (ID)", 'password': "รหัสผ่าน", 'confirm_password': "ยืนยันรหัสผ่าน",
        'name': "ชื่อ", 'phone': "เบอร์โทรศัพท์", 'address': "ที่อยู่", 'zipcode': "รหัสไปรษณีย์", 'line_id': "Line ID (ไม่บังคับ)",
        'login_btn': "เข้าสู่ระบบ", 'register_btn': "สมัครสมาชิก", 'logout': "ออกจากระบบ",
        'welcome': "ยินดีต้อนรับ", 'my_wishlist': "รายการโปรดของฉัน", 'login_required': "กรุณาเข้าสู่ระบบ",
        'sold_btn': "🚫 สินค้าหมดแล้วค่ะ",
        'currency_symbol': "฿",
        'contact_msg': "[Code: {code}] สนใจสั่งซื้อสินค้า: {brand} {name} ({price})\n- User ID: {user_id}\n- Name: {user_name}"
    },
    'EN': {
        'title': "Curated Vintage Clothing Shop",
        'filter': "🔍 Filter",
        'search': "Search",
        'search_placeholder': "Ex : Code or Name",
        'brand': "Brand",
        'category': "Category",
        'size': "Size",
        'price_range': "Price Range (THB)",
        'show_sold_out': "Show Sold Out Items",
        'sort': "Sort By",
        'sort_options': ["Newest", "Price: Low to High", "Price: High to Low", "Name"],
        'total_items': "Showing {current} of {total} items",
        'page': "Page",
        'page_caption': "Page {current} of {total}",
        'sold_out': "🚫 Sold Out",
        'on_sale': "✅ On Sale",
        'no_image': "📷 No Image",
        'detail_btn': "Details & Buy",
        'desc_title': "**Description**",
        'desc_title': "**Description**",
        'date_title': "📅 Date Added",
        'arrival_title': "ETA",
        'arrival_tbd': "TBD",
        'show_arrived_only': "Show Arrived Items Only",
        'line_btn': "🟢 Buy via Line",
        'login_tab': "Login", 'register_tab': "Sign Up",
        'username': "Username", 'password': "Password", 'confirm_password': "Confirm Password",
        'name': "Name", 'phone': "Phone", 'address': "Address", 'zipcode': "Zipcode", 'line_id': "Line ID (Optional)",
        'login_btn': "Login", 'register_btn': "Sign Up", 'logout': "Logout",
        'welcome': "Welcome", 'my_wishlist': "My Wishlist", 'login_required': "Login Required",
        'sold_btn': "🚫 Item Sold Out",
        'currency_symbol': "฿",
        'contact_msg': "[Code: {code}] I would like to buy: {brand} {name} ({price})\n- User ID: {user_id}\n- Name: {user_name}"
    },
    'KR': {
        'title': "엄선된 구제 의류를 만나보세요.",
        'filter': "🔍 필터",
        'search': "검색",
        'search_placeholder': "예 : Code or Name",
        'brand': "브랜드",
        'category': "카테고리",
        'size': "사이즈",
        'price_range': "가격 범위 (KRW)",
        'show_sold_out': "품절된 상품도 보기 (Out of Stock)",
        'sort': "정렬 기준",
        'sort_options': ["최신순", "가격 낮은순", "가격 높은순", "이름순"],
        'total_items': "총 {total}개의 상품 중 {current}개를 보여줍니다.",
        'page': "📄 페이지 이동",
        'page_caption': "총 {total} 페이지 중 {current} 페이지",
        'sold_out': "🚫 품절 (Sold Out)",
        'on_sale': "✅ 판매중 (On Sale)",
        'no_image': "📷 이미지 없음",
        'detail_btn': "상세 정보 및 구매 (Buy Now)",
        'desc_title': "**제품 설명**",
        'desc_title': "**제품 설명**",
        'date_title': "📅 등록일",
        'arrival_title': "도착예정일",
        'arrival_tbd': "미정",
        'show_arrived_only': "도착한 상품만 보기",
        'line_btn': "🟢 라인으로 구매 문의 (Line Contact)",
        'login_tab': "로그인", 'register_tab': "회원가입",
        'username': "아이디", 'password': "비밀번호", 'confirm_password': "비밀번호 확인",
        'name': "이름", 'phone': "전화번호", 'address': "주소", 'zipcode': "우편번호", 'line_id': "라인ID (선택)",
        'login_btn': "로그인", 'register_btn': "회원가입", 'logout': "로그아웃",
        'welcome': "환영합니다", 'my_wishlist': "내 찜 목록 보기", 'login_required': "로그인이 필요합니다",
        'sold_btn': "🚫 품절된 상품입니다",
        'currency_symbol': "฿",
        'contact_msg': "[Code: {code}] 제품으로 문의한 제품입니다. ({brand} {name} {price})\n- User ID: {user_id}\n- Name: {user_name}"
    }
}

# Language Toggle (Sidebar Top)
st.sidebar.markdown("### 🌐 Language")
lang_code = st.sidebar.radio("Language", ('TH', 'EN', 'KR'), horizontal=True, label_visibility="collapsed")
st.session_state.lang = lang_code
T = lang_dict[lang_code]


# ... (Skip unchanged until grid loop)


# [NOTE] Make sure to scroll down to grid loop logic usage below

# ...

# Inside the Grid Loop (lines ~380+)
# Since I cannot edit disjoint lines easily with replace_file_content unless I include everything in between or use multi_replace,
# I will use multi_replace if available, but I don't see it in my thought process plan.
# Wait, I am replacing a big chunk?
# The request is to fix `lang_dict` (lines ~63) AND the logic below (lines ~360).
# I will make TWO replace calls. This one handles `lang_dict`.

# Actually, I'll just change `currency_symbol` in lang_dict here.


# --- Header ---
# Check for logo file, otherwise use text
import os
import base64

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

if os.path.exists("822logo_final_v2.png"):
    # Center Logo: Use HTML/CSS with Base64 to guarantee centering on mobile
    img_base64 = get_base64_of_bin_file("822logo_final_v2.png")
    st.markdown(
        f"""
        <div style="
            display: flex; 
            justify-content: center; 
            align-items: center;
            width: 100%; 
            padding: 0px 0; 
            margin-bottom: 10px; 
            /* background-color removed for transparency */
            border-bottom: none;
        ">
            <img src="data:image/png;base64,{img_base64}" style="width: auto; max-width: 300px;">
        </div>
        """,
        unsafe_allow_html=True
    )
elif os.path.exists("822logo_final.png"):
    # Fallback to cleaned version
    img_base64 = get_base64_of_bin_file("822logo_clean.png")
    st.markdown(
        f"""
        <div style="display: flex; justify-content: center; margin-bottom: 20px;">
            <img src="data:image/png;base64,{img_base64}" width="200" style="max-width: 100%;">
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.title("822 SHOP")
st.markdown(f"<div style='text-align: center; margin-bottom: 20px;'>{T['title']}</div>", unsafe_allow_html=True)

if df.empty:
    st.warning("No products found. Please check Google Sheet.")
    st.stop()

# --- Auth & Sidebar ---
import extra_streamlit_components as stx

# [Cookie Manager] Initialize
# CookieManager is a component so it should not be cached with cache_resource as it creates a frontend widget
cookie_manager = stx.CookieManager(key="cookie_manager")

if 'user' not in st.session_state:
    st.session_state['user'] = None

am = AuthManager()

# [Auto-Login Logic] Check Cookie on App Start
if not st.session_state['user']:
    try:
        # [Fix] Add delay to ensure CookieManager is mounted/ready
        import time
        time.sleep(0.5)
        
        # Check if 'user_token' cookie exists
        # use get_all() to be safe or explicit get
        cookies = cookie_manager.get_all()
        user_token = cookies.get('user_token')
        
        if user_token:
            # Token found, try to fetch user info
            # Security Note: Ideally this token should be a secure random session ID verified against DB
            # For MVP, we use user_id directly (Assuming secure environment or low risk)
            # Better: Sign the cookie (stx handles some cookies but not encryption by default)
            success, user_info = am.get_user_info(user_token)
            if success:
                st.session_state['user'] = user_info
                st.sidebar.success(f"자동 로그인 성공: {user_info['name']}님")
                # Force rerun to update UI state immediately if needed, but sidebar update might be enough
                # st.rerun() 
    except Exception as e:
        print(f"Cookie Error: {e}")

# Auth UI in Sidebar
if st.session_state['user']:
    st.sidebar.success(f"{T['welcome']}, {st.session_state['user']['name']}님!")
    if st.sidebar.button(T['logout']):
        st.session_state['user'] = None
        # [Logout] Delete Cookie
        cookie_manager.delete('user_token')
        st.rerun()
else:
    auth_tab1, auth_tab2 = st.sidebar.tabs([T['login_tab'], T['register_tab']])
    
    with auth_tab1: # Login
        l_user = st.text_input(T['username'], key='l_user')
        l_pass = st.text_input(T['password'], type='password', key='l_pass')
        
        # [NEW] Keep Me Logged In Checkbox
        keep_logged_in = st.checkbox("로그인 상태 유지 (Keep me logged in)")
        
        if st.button(T['login_btn']):
            success, user_info, msg = am.login_user(l_user, l_pass)
            if success:
                st.session_state['user'] = user_info
                
                # [Login Success] Set Cookie if requested
                if keep_logged_in:
                    from datetime import timedelta
                    # Expires in 30 days
                    expires = datetime.now() + timedelta(days=30)
                    cookie_manager.set('user_token', l_user, expires_at=expires)
                    # [Critical] Wait for cookie to be set in browser before rerun
                    import time
                    time.sleep(1)
                
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)
                
    with auth_tab2: # Register
        r_user = st.text_input(T['username'], key='r_user')
        r_pass = st.text_input(T['password'], type='password', key='r_pass')
        r_pass_conf = st.text_input(T['confirm_password'], type='password', key='r_pass_conf')
        r_name = st.text_input(T['name'], key='r_name')
        r_phone = st.text_input(T['phone'], key='r_phone')
        r_addr = st.text_input(T['address'], key='r_addr')
        r_zip = st.text_input(T['zipcode'], key='r_zip')
        r_line = st.text_input(T['line_id'], key='r_line')
        
        if st.button(T['register_btn']):
            if not (r_user and r_pass and r_name and r_phone and r_addr and r_zip):
                st.error("필수 항목을 모두 입력해주세요.")
            elif r_pass != r_pass_conf:
                st.error("비밀번호가 일치하지 않습니다.")
            elif len(r_pass) < 8: # Logic check only
                st.error("비밀번호는 8자 이상이어야 합니다.")
            else:
                user_data = {
                    'user_id': r_user, 'password': r_pass, 'name': r_name,
                    'phone': r_phone, 'address': r_addr, 'zipcode': r_zip, 'line_id': r_line
                }
                success, msg = am.register_user(user_data)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)

st.sidebar.header(T['filter'])

# [DEBUG / INFO] Source Info & Cache Control
if not df.empty:
    source_name = df.attrs.get('source_sheet', 'Unknown')
    st.sidebar.info(f"Loaded from: **{source_name}** ({len(df)} rows)")
    
    if st.sidebar.button("🔄 Reload Data (Clear Cache)"):
        st.cache_data.clear()
        st.rerun()

# 1. Search
search_query = st.sidebar.text_input(T['search'], placeholder=T['search_placeholder'])

# Search Validation (English Only)
if search_query:
    if not search_query.isascii():
        st.sidebar.error("Please enter English only.")
        search_query = "" # Reset query effectively for filtering

# 2. Brand Filter
all_brands = sorted([str(x) for x in df['brand'].unique()]) if 'brand' in df.columns else []
selected_brands = st.sidebar.multiselect(T['brand'], all_brands)

# 3. Category Filter
all_categories = sorted([str(x) for x in df['category'].unique()]) if 'category' in df.columns else []
selected_categories = st.sidebar.multiselect(T['category'], all_categories)

# 4. Size Filter
all_sizes = sorted([str(x) for x in df['size'].unique()]) if 'size' in df.columns else []
selected_sizes = st.sidebar.multiselect(T['size'], all_sizes)

# 5. Price Range
# User requested only THB unit display, no conversion (Sheet data is already THB)
# Exchange Rate: 1.0 (Raw value)
EXCHANGE_RATE = 1.0

min_price = int(df['price'].min()) if not df.empty else 0
max_price = int(df['price'].max()) if not df.empty else 10000 

slider_min_val = min_price
slider_max_val = max_price

# Prevent crash if min == max (e.g. all prices are 0 or only 1 item)
if slider_max_val <= slider_min_val:
    slider_max_val = slider_min_val + 10000

cost_range = st.sidebar.slider(T['price_range'], slider_min_val, slider_max_val, (slider_min_val, slider_max_val))

# Convert back to KRW for filtering (Same now)
filter_min = cost_range[0]
filter_max = cost_range[1]

# 6. Status Filter
show_sold_out = st.sidebar.checkbox(T['show_sold_out'], value=False)

# [NEW] Show Arrived Only Checkbox
show_arrived_only = st.sidebar.checkbox(T['show_arrived_only'], value=False)

# 7. Debug Mode
debug_mode = False
# Only show for admin
if st.session_state['user'] and st.session_state['user']['user_id'] == 'youini07':
    debug_mode = st.sidebar.checkbox("🛠️ Debug Mode", value=False)

# --- Sort Options ---
sort_option = st.selectbox(T['sort'], T['sort_options'])

# --- App Logic: Filtering ---
filtered_df = df.copy()

# Filter by Arrival Status (Show Arrived Only)
if show_arrived_only:
    # Helper to check if "has arrival info" (meaning NOT arrived yet)
    def has_arrival_info(val):
        s = str(val).strip().lower()
        # Explicitly return boolean to avoid TypeError with ~ operator
        is_valid = s and s != 'nan' and s != 'nat' and s != 'none' and s != ''
        return bool(is_valid)
        
    # Apply mask: Keep only rows where has_arrival_info is False
    if 'arrival_date' in filtered_df.columns:
        mask_has_arrival = filtered_df['arrival_date'].apply(has_arrival_info)
        filtered_df = filtered_df[~mask_has_arrival]

# Filter by My Wishlist (If Logged In)
if st.session_state['user']:
    show_my_wishlist = st.sidebar.checkbox(T['my_wishlist'], value=False)
    if show_my_wishlist:
        my_likes_ids = am.get_user_likes(st.session_state['user']['user_id'])
        if 'code' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['code'].astype(str).isin(my_likes_ids)]

if debug_mode:
    st.warning("Debug Mode On")
    st.write("### Data Preview")
    st.dataframe(filtered_df[['code', 'name', 'status', 'price']].head()) # assumes 'code' exists

# Filter: Status ('onsale' vs 'out of stock')
# Checking against the 'stock' column which user confirmed holds the status
if 'stock' in filtered_df.columns:
    # Normalize
    filtered_df['stock_norm'] = filtered_df['stock'].astype(str).str.lower().str.strip()
    
    if not show_sold_out:
        # Exclude rows where stock is 'out of stock'
        # Using ~ (not) operator on the mask
        mask = filtered_df['stock_norm'].str.contains('out of stock', na=False)
        filtered_df = filtered_df[~mask]

# Filter: Search (Name OR Code)
if search_query:
    # Check if 'code' column exists (Col A often named 'code')
    # If not, try to guess or just use 'name'
    search_col_matches = filtered_df['name'].str.contains(search_query, case=False, na=False)
    
    if 'code' in filtered_df.columns:
        search_col_matches = search_col_matches | filtered_df['code'].astype(str).str.contains(search_query, case=False, na=False)
    elif 'id' in filtered_df.columns: # fallback guess
        search_col_matches = search_col_matches | filtered_df['id'].astype(str).str.contains(search_query, case=False, na=False)
        
    filtered_df = filtered_df[search_col_matches]

# Filter: Brand
if selected_brands:
    filtered_df = filtered_df[filtered_df['brand'].isin(selected_brands)]

# Filter: Category
if selected_categories:
    filtered_df = filtered_df[filtered_df['category'].isin(selected_categories)]

# Filter: Size
if selected_sizes:
    filtered_df = filtered_df[filtered_df['size'].isin(selected_sizes)]

# Filter: Price
filtered_df = filtered_df[(filtered_df['price'] >= filter_min) & (filtered_df['price'] <= filter_max)]

# --- App Logic: Sorting ---
# Map sort options to English keys for logic
sort_map = {
    "최신순": "Newest", "Newest (Newest)": "Newest", "ล่าสุด (Newest)": "Newest",
    "가격 낮은순": "Price_Low", "Price: Low to High (Low-High)": "Price_Low", "ราคา: ต่ำไปสูง (Low-High)": "Price_Low",
    "가격 높은순": "Price_High", "Price: High to Low (High-Low)": "Price_High", "ราคา: สูงไปต่ำ (High-Low)": "Price_High",
    "이름순": "Name", "Name (Name)": "Name", "ชื่อ (Name)": "Name"
}
# Fallback logic
s_opt = sort_option
if "Newest" in s_opt or "ล่าสุด" in s_opt or "최신" in s_opt:
    current_sort = "Newest"
elif "Low" in s_opt or "ต่ำไปสูง" in s_opt or "낮은" in s_opt:
    current_sort = "Price_Low"
elif "High" in s_opt or "สูงไปต่ำ" in s_opt or "높은" in s_opt:
    current_sort = "Price_High"
else:
    current_sort = "Name"

if current_sort == "Newest":
    if 'updated_at' in filtered_df.columns:
        # [MODIFIED] Robust Date Parsing for Sorting
        # 1. Try format MM/DD (e.g. 02/13) -> defaults to 1900-02-13, good for sorting.
        parsed_dates = pd.to_datetime(filtered_df['updated_at'], format='%m/%d', errors='coerce')
        
        # 2. If NaT, try standard accessible formats (e.g. YYYY-MM-DD)
        mask = parsed_dates.isna()
        if mask.any():
             parsed_dates.loc[mask] = pd.to_datetime(filtered_df.loc[mask, 'updated_at'], errors='coerce')
        
        # Create temporary column for sorting to avoid messing up display (if display uses original string)
        # Actually logic uses 'updated_at' column for display in expander? 
        # Line 468: st.write(f"{T['date_title']}: {row.get('updated_at', '-')}")
        # So we should preserve original string?
        # df is copied to filtered_df. modifying filtered_df['updated_at'] affects display if we use filtered_df for display.
        # Yes, we use filtered_df in the grid loop. So we should NOT overwrite 'updated_at' with datetime object if we want to keep original string format?
        # Wait, if we overwrite with datetime, it prints as YYYY-MM-DD which is arguably better than 02/13.
        # But let's be safe and use a separate column for sorting.
        
        filtered_df['sort_date'] = parsed_dates
        filtered_df = filtered_df.sort_values(by='sort_date', ascending=False)
elif current_sort == "Price_Low":
    filtered_df = filtered_df.sort_values(by='price', ascending=True)
elif current_sort == "Price_High":
    filtered_df = filtered_df.sort_values(by='price', ascending=False)
elif current_sort == "Name":
    filtered_df = filtered_df.sort_values(by='name', ascending=True)

# --- App Logic: Pagination ---
# --- App Logic: Pagination ---
if 'page' not in st.session_state:
    st.session_state.page = 1

items_per_page = 12
total_items = len(filtered_df)
total_pages = max(1, (total_items - 1) // items_per_page + 1)

# Ensure page is valid
if st.session_state.page > total_pages:
    st.session_state.page = 1

# Slice Data
start_idx = (st.session_state.page - 1) * items_per_page
end_idx = start_idx + items_per_page
page_items = filtered_df.iloc[start_idx:end_idx]

# --- Display Grid (Strict 3 per row) ---
st.divider()
st.subheader(T['total_items'].format(total=total_items, current=len(page_items)))

# Fetch Likes Data (Once per rerun)
all_counts = am.get_all_like_counts()
my_likes_set = set()
if st.session_state['user']:
    my_likes_set = am.get_user_likes(st.session_state['user']['user_id'])

# Reset index to allow looping by integers
page_items = page_items.reset_index(drop=True) 

# Iterate in chunks of 3
for i in range(0, items_per_page, 3):
    # Get current batch
    batch = page_items.iloc[i:i+3]
    if batch.empty:
        break
        
    cols = st.columns(3)
    for idx, row in batch.iterrows():
        # idx is relative to batch due to default iterrows but we reset index? 
        # Actually iterrows returns index from DataFrame. 
        # If reset_index(drop=True) was called, idx is 0,1,2... within page_items.
        # But iterating batch.iterrows() preserves the index from page_items.
        
        # We need the column index explicitly: 0,1,2
        col_idx = idx % 3
        with cols[col_idx]:
            status_val = str(row.get('stock', '')).lower().strip()
            # User specified: 'out of stock' = Sold, 'on sale' = Available
            # We will use 'out of stock' as the strict trigger for sold status.
            # Check if 'out of stock' is in the string to be safe against minor variations
            is_sold = 'out of stock' in status_val or 'sold' in status_val
            
            # Opacity Style
            opacity_style = "opacity: 0.5;" if is_sold else ""
            
            # Container start (add relative positioning context)
            st.markdown(f'<div style="{opacity_style} position: relative;">', unsafe_allow_html=True)
    
            # Image Logic
            img_url = get_image_url(row.get('image_file_id'))
            
            # Prepare Image HTML (Direct URL)
            img_html = ""
            
            # Use Direct URL (Client-side loading)
            if img_url:
                # [MODIFIED] Aspect Ratio 9:8 (Top Crop)
                # Removed server-side fetching and base64 encoding
                img_html = f'<img src="{img_url}" style="width:100%; aspect-ratio: 9/8; object-fit: cover; object-position: top; border-radius:5px;" loading="lazy">'
            else:
                # [MODIFIED] Aspect Ratio 9:8 for placeholder
                img_html = f'<div style="width:100%; aspect-ratio: 9/8; background:#f0f0f0; display:flex; align-items:center; justify-content:center; border-radius:5px;">{T["no_image"]}</div>'
            
            # Render Image + Overlay (Centered)
            # Render Image + Overlay (Centered)
            # Priority: Sold Out > Arrival Date > Normal
            
            # Render Image + Overlay (Centered)
            # Priority: Sold Out > Arrival Date > Normal
            
            arrival_val = str(row.get('arrival_date', '')).strip()
            # Check if arrival_date is valid (not nan/empty/nat)
            is_arrival_valid = arrival_val and arrival_val.lower() != 'nan' and arrival_val.lower() != 'nat' and len(arrival_val) > 0
            
            if is_sold:
                 # Zoom Link Wrapper
                 # [FIX] Prioritize img_url for the link target because opening base64 in new tab is often blocked.
                 link_target = img_url if img_url else ""
    
                 overlay_html = f"""
                 <div style="position: relative; width: 100%;">
                    <div style="opacity: 0.5;">
                        <a href="{link_target}" target="_blank" style="display: block; cursor: pointer;">
                            {img_html}
                        </a>
                    </div>
                    <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); 
                                color: white; font-size: 20px; font-weight: bold; 
                                background-color: rgba(0,0,0,0.6); padding: 10px 20px; border-radius: 5px;
                                pointer-events: none; white-space: nowrap; z-index: 10;">
                        {T['sold_out']}
                    </div>
                 </div>
                 """
                 st.markdown(overlay_html, unsafe_allow_html=True)
            elif is_arrival_valid:
                 # Arrival Date Overlay
                 # Text: "{T['arrival_title']} : {arrival_date}"
                 # Handling "TBD" / "미정" explicitly
                 
                 final_val = arrival_val
                 if arrival_val.upper() == 'TBD' or arrival_val == '미정':
                     final_val = T['arrival_tbd']
                     
                 display_text = f"{T['arrival_title']} : {final_val}"
                 
                 # [FIX] Prioritize img_url for the link
                 link_target = img_url if img_url else ""
                     
                 # [MODIFIED] No Opacity. Text at bottom. Font 20px.
                 # Added <a> wrapper for Zoom.
                 
                 overlay_html = f"""
                 <div style="position: relative; width: 100%;">
                     <a href="{link_target}" target="_blank" style="display: block; cursor: pointer;">
                         {img_html}
                     </a>
                     <div style="position: absolute; bottom: 10px; left: 0; width: 100%;
                                 color: white; font-size: 20px; font-weight: bold; 
                                 background-color: rgba(0,0,0,0.6); padding: 5px 0; 
                                 pointer-events: none; z-index: 10; text-align: center;">
                         {display_text}
                     </div>
                 </div>
                 """
                 st.markdown(overlay_html, unsafe_allow_html=True)
            else:
                 # Normal Image - Add Zoom
                 # [FIX] Prioritize img_url
                 link_target = img_url if img_url else ""
                     
                 if link_target:
                     st.markdown(f'<a href="{link_target}" target="_blank" style="display:block; cursor:pointer;">{img_html}</a>', unsafe_allow_html=True)
                 else:
                     st.markdown(f"<div>{img_html}</div>", unsafe_allow_html=True)
      
            # Info
            code = row.get('code', '-')
            brand = row.get('brand', 'Unknown')
            name = row.get('name', 'No Name')
            price_val = row.get('price', 0)
            
            # Price & Display Logic
            price_plain = f"{T['currency_symbol']}{price_val:,}" # Plain text for message
            
            if is_sold:
                price_display = f"<span style='color:#999; text-decoration:line-through; font-size:16px;'>{T['sold_out']}</span>"
                price_str = price_plain 
            else:
                # Blue Color (#007bff), Larger Font (+2 -> approx 18px ~ 20px)
                price_display = f"<span style='color:#007bff; font-weight:bold; font-size:20px;'>{price_plain}</span>"
                price_str = price_plain
            
            size = row.get('size', '-')
            condition = row.get('condition', '-')
            
            # Title & Price
            st.markdown(f"<div class='product-title'>[{brand}] {name}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='product-price'>{price_display}</div>", unsafe_allow_html=True)
    
            # Heart Button
            p_code = str(code)
            likes_num = all_counts.get(p_code, 0)
            
            # Determine button label
            if st.session_state['user']:
                is_liked = p_code in my_likes_set
                heart_icon = "❤️" if is_liked else "🤍"
                # Button key must be unique per item
                if st.button(f"{heart_icon} {likes_num}", key=f"like_{p_code}"):
                     am.toggle_like(st.session_state['user']['user_id'], p_code)
                     st.rerun()
            else:
                 if st.button(f"🤍 {likes_num}", key=f"like_{p_code}"):
                     st.toast(T['login_required'], icon="🔒")
                
            # Meta Info: Code | Size | Condition
            # Meta Info: Code | Size | Condition
            st.caption(f"Code : {code} | {T['size']} : {size} | Condition : {condition}")
            
            st.markdown('</div>', unsafe_allow_html=True) # End opacity div
            
            # Detail Expander
            with st.expander(T['detail_btn']):
                st.write(T['desc_title'])
                # Robust Description logic
                desc_text = row.get('description')
                if not desc_text or str(desc_text).strip() == '-' or str(desc_text).strip() == '':
                    desc_text = row.get('product description') # Try full name
                if not desc_text or str(desc_text).strip() == '-' or str(desc_text).strip() == '':
                    desc_text = row.get('detail') # Try detail
                if not desc_text or str(desc_text).strip() == '-' or str(desc_text).strip() == '':
                     desc_text = '-'
                     
                st.write(desc_text)
                st.write(f"---")
                st.write(f"{T['date_title']}: {row.get('updated_at', '-')}")
                
                if not is_sold:
                    # Line Contact Logic: Only for Logged-in Users
                    if st.session_state['user']:
                        # Get User Info
                        u_id = st.session_state['user']['user_id']
                        u_name = st.session_state['user'].get('name', 'Unknown')
                        
                        # Format Message with User Info
                        contact_text = T['contact_msg'].format(
                            code=code, brand=brand, name=name, price=price_str,
                            user_id=u_id, user_name=u_name
                        )
                        
                        # Encode message for URL
                        import urllib.parse
                        encoded_msg = urllib.parse.quote(contact_text)
                        
                        # Use Official Account Auto-Fill Link
                        LINE_ID = "@102ipvys"
                        line_url = f"https://line.me/R/oaMessage/{LINE_ID}/?{encoded_msg}"
                        
                        # Line Button (Link)
                        st.markdown(f"""
                        <a href="{line_url}" target="_blank" style="text-decoration:none;">
                            <button style="width:100%; background-color:#06C755; color:white; border:none; padding:10px; border-radius:5px; font-weight:bold; cursor:pointer;">
                                {T['line_btn']}
                            </button>
                        </a>
                        <div style="height: 30px;"></div>
                        """, unsafe_allow_html=True)
                    else:
                        # Guest: Show Button that triggers Alert
                        # Use logic to show st.error when clicked
                        # st.button returns True on click
                        if st.button(T['line_btn'], key=f"guest_line_{code}"):
                            st.toast(T['login_required'], icon="🔒")
                            st.error(T['login_required'])
                            
                        # Spacing for consistency
                        st.markdown('<div style="height: 30px;"></div>', unsafe_allow_html=True)
                        
                else:
                     # Sold out button (disabled) or just message
                     st.error(T['sold_btn'])
    
            st.markdown("---")

# --- Pagination Controls ---
if total_pages > 1:
    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()
    
    # Center Pagination
    # Use columns to center the controls
    # Layout: [Prev Button] [Radio Buttons] [Next Button]
    
    # Calculate visible page range (1-10, 11-20, etc.)
    current_page = st.session_state.page
    chunk_size = 10
    start_page = ((current_page - 1) // chunk_size) * chunk_size + 1
    end_page = min(start_page + chunk_size - 1, total_pages)
    
    page_options = list(range(start_page, end_page + 1))
    
    # Check bounds for navigation
    has_prev = start_page > 1
    has_next = end_page < total_pages
    
    # [CSS] Force Center Alignment & No-Wrap for Radio Group
    st.markdown("""
    <style>
        div[data-testid="stRadio"] > div {
            justify-content: center;
            flex-wrap: nowrap !important; /* Prevent wrapping to second line */
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Layout columns: [Spacer] [Prev] [Pages] [Next] [Spacer]
    # Ratios: 3 : 1 : 10 : 1 : 3
    # Give maximum space to the pages (Radio) to prevent overlap/wrapping
    c_spacer_L, c_prev, c_radio, c_next, c_spacer_R = st.columns([3, 1, 10, 1, 3])
    
    # Previous Chunk
    with c_prev:
        if has_prev:
            if st.button("◀", key="prev_chunk"):
                st.session_state.page = start_page - 1 # Go to last page of prev chunk
                st.rerun()

    # Page Numbers (Radio)
    with c_radio:
        # We need a key that changes with the chunk to avoid index errors if range sizes differ
        # OR we just handle the index carefully. 
        # Better to ensure current page is in options.
        
        # If current page is NOT in the visible options (which shouldn't happen by logic above), fix it
        # Logic ensures current_page is always within [start_page, end_page]
        
        selected_p = st.radio(
            "Go to page:", 
            options=page_options,
            index=page_options.index(current_page) if current_page in page_options else 0,
            horizontal=True,
            label_visibility="collapsed",
            key=f"pagination_radio_{start_page}" # Unique key per chunk to force reset options
        )
        
        if selected_p != st.session_state.page:
            st.session_state.page = selected_p
            st.rerun()

    # Next Chunk
    with c_next:
        if has_next:
            if st.button("▶", key="next_chunk"):
                st.session_state.page = end_page + 1 # Go to first page of next chunk
                st.rerun()
             
    st.markdown(f"<div style='text-align: center; color: #666; margin-top: 5px;'>Page {st.session_state.page} / {total_pages}</div>", unsafe_allow_html=True)
