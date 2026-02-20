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
    page_icon="822logo_final_v2.png",
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
    footer {display: none !important;}
    #MainMenu {visibility: hidden;}
    .stDeployButton {display: none !important;}
    header[data-testid="stHeader"] {background: rgba(0,0,0,0) !important;}
    
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

<script>
    // 브라우저 탭 제목에서 " · Streamlit" 제거
    function fixTitle() {
        var title = window.parent.document.querySelector('title');
        if (title && title.innerText.includes('Streamlit')) {
            title.innerText = "822 SHOP";
        }
    }
    
    // 페이지 로드 및 업데이트 시 제목 강제 고정
    const observer = new MutationObserver(fixTitle);
    const titleNode = window.parent.document.querySelector('title');
    if (titleNode) {
        observer.observe(titleNode, { subtree: true, characterData: true, childList: true });
        fixTitle();
    }
</script>
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
        'filter': "ตัวกรอง (Filter)", # Removed icon
        'search': "Search",
        'search_placeholder': "Ex : Code or Name",
        'brand': "แบรนด์",
        'upper_category': "หมวดหมู่หลัก (Upper Category)", # [NEW]
        'category': "หมวดหมู่",
        'size': "ขนาด (Size)",
        'price_range': "ช่วงราคา (บาท)",
        'show_sold_out': "แสดงสินค้าที่หมดแล้ว",
        'sort': "เรียงตาม",
        'sort_options': ["ล่าสุด (Newest)", "ราคา: ต่ำไปสูง (Low-High)", "ราคา: สูงไปต่ำ (High-Low)", "ชื่อ (Name)"],
        'total_items': "แสดง {current} จาก {total} รายการ",
        'total_simple': "ทั้งหมด {total} รายการ", # New simple count
        'page': "หน้า",
        'page_caption': "หน้า {current} จาก {total}",
        'sold_out': "🚫 สินค้าหมด (Sold Out)",
        'on_sale': "✅ มีสินค้า (In Stock)",
        'no_image': "📷 ไม่มีรูปภาพ",
        'detail_btn': "ดูรายละเอียด & สั่งซื้อ",
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
        'contact_msg': "[Code: {code}] สนใจสั่งซื้อสินค้า: {brand} {name} ({price})\n- User ID: {user_id}\n- Name: {user_name}",
        'measured_size': "ขนาดวัดจริง"
    },
    'EN': {
        'title': "Curated Vintage Clothing Shop",
        'filter': "Filter", # Removed icon
        'search': "Search",
        'search_placeholder': "Ex : Code or Name",
        'brand': "Brand",
        'upper_category': "Upper Category", # [NEW]
        'category': "Category",
        'size': "Size",
        'price_range': "Price Range (THB)",
        'show_sold_out': "Show Sold Out Items",
        'sort': "Sort By",
        'sort_options': ["Newest", "Price: Low to High", "Price: High to Low", "Name"],
        'total_items': "Showing {current} of {total} items",
        'total_simple': "Total {total} items", # New simple count
        'page': "Page",
        'page_caption': "Page {current} of {total}",
        'sold_out': "🚫 Sold Out",
        'on_sale': "✅ On Sale",
        'no_image': "📷 No Image",
        'detail_btn': "Details & Buy",
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
        'contact_msg': "[Code: {code}] I would like to buy: {brand} {name} ({price})\n- User ID: {user_id}\n- Name: {user_name}",
        'measured_size': "Meas."
    },
    'KR': {
        'title': "엄선된 구제 의류를 만나보세요.",
        'filter': "필터", # Removed icon
        'search': "검색",
        'search_placeholder': "예 : Code or Name",
        'brand': "브랜드",
        'upper_category': "상위 카테고리", # [NEW]
        'category': "카테고리",
        'size': "사이즈",
        'price_range': "가격 범위 (KRW)",
        'show_sold_out': "품절된 상품도 보기 (Out of Stock)",
        'sort': "정렬 기준",
        'sort_options': ["최신순", "가격 낮은순", "가격 높은순", "이름순"],
        'total_items': "총 {total}개의 상품 중 {current}개를 보여줍니다.",
        'total_simple': "총 {total}개 상품", # New simple count
        'page': "📄 페이지 이동",
        'page_caption': "총 {total} 페이지 중 {current} 페이지",
        'sold_out': "🚫 품절 (Sold Out)",
        'on_sale': "✅ 판매중 (On Sale)",
        'no_image': "📷 이미지 없음",
        'detail_btn': "상세 정보 및 구매 (Buy Now)",
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
        'contact_msg': "[Code: {code}] 제품으로 문의한 제품입니다. ({brand} {name} {price})\n- User ID: {user_id}\n- Name: {user_name}",
        'measured_size': "실측사이즈"
    }
}

# Language Toggle (Sidebar Top)
st.sidebar.markdown("### Language") # Removed globe icon
lang_code = st.sidebar.radio("Language", ('TH', 'EN', 'KR'), horizontal=True, label_visibility="collapsed")
st.session_state.lang = lang_code
T = lang_dict[lang_code]

# ─────────────────────────────────────────
# [페이지 전환] 사이드바 상단 - 소개 / 카탈로그
# ─────────────────────────────────────────
if 'sidebar_page' not in st.session_state:
    st.session_state.sidebar_page = 'catalog'  # 기본: 카탈로그

st.sidebar.markdown("---")

# [Fix] st.sidebar.columns() 안에서 st.button()을 쓰면 메인 화면에 렌더되는 Streamlit 버그
# → st.sidebar.button()을 직접 사용하고, CSS로 나란히 배치
st.sidebar.markdown("""
<style>
/* 소개/카탈로그 버튼 2개를 나란히 배치 */
div[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] {
    gap: 6px;
}
</style>
""", unsafe_allow_html=True)

# 실제로는 순차 배치 (버튼이 좁아 두 줄이 되면 가독성이 더 좋음)
_about_label  = "📖 소개" if lang_code == 'KR' else ("📖 About" if lang_code == 'EN' else "📖 เกี่ยวกับ")
_catalog_label = "🛍️ 카탈로그" if lang_code == 'KR' else ("🛍️ Catalog" if lang_code == 'EN' else "🛍️ สินค้า")

if st.sidebar.button(
    _about_label,
    use_container_width=True,
    type="primary" if st.session_state.sidebar_page == 'about' else "secondary",
    key="btn_about"
):
    st.session_state.sidebar_page = 'about'
    st.rerun()

if st.sidebar.button(
    _catalog_label,
    use_container_width=True,
    type="primary" if st.session_state.sidebar_page == 'catalog' else "secondary",
    key="btn_catalog"
):
    st.session_state.sidebar_page = 'catalog'
    st.rerun()

st.sidebar.markdown("---")


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

# ─────────────────────────────────────────
# [소개 페이지] sidebar_page == 'about' 일 때 렌더링
# ─────────────────────────────────────────
if st.session_state.get('sidebar_page', 'catalog') == 'about':
    import sys
    import os
    _shipping_dir = os.path.join(os.path.dirname(__file__), 'shipping')
    if _shipping_dir not in sys.path:
        sys.path.insert(0, _shipping_dir)

    from ship_tracker_web import get_ship_tracker_html
    import streamlit.components.v1 as components

    # ── 도착 예정일 데이터: arrival_date 컬럼에서 추출 ──
    _arrival_col = 'arrival_date'
    if _arrival_col in df.columns:
        _raw_arrivals = df[_arrival_col].dropna().astype(str).tolist()
        _arrivals = [v for v in _raw_arrivals if v.strip() and v.lower() not in ('nan', 'none', 'nat', '')]
    else:
        _arrivals = []

    # ── 선박 트래커: 현재 언어(lang_code) 전달 ──
    # [방어 코드] ship_tracker_web.py 구버전(lang 파라미터 없음) 배포 시에도 크래시 없이 동작
    try:
        _tracker_html = get_ship_tracker_html(arrival_dates=_arrivals, lang=lang_code)
    except TypeError:
        _tracker_html = get_ship_tracker_html(arrival_dates=_arrivals)
    components.html(_tracker_html, height=290, scrolling=False)


    st.markdown("---")

    # ── 소개 텍스트: 사이트 언어(lang_code) 에 따라 자동 표시 ──
    # 다크모드에서도 확실히 보이도록 흰 카드 배경 + 진한 글자색 고정

    _about_texts = {
        'KR': {
            'headline': '우리가 이 옷들을 선택한 이유가 있습니다.',
            'body': """저희는 단순히 구제 의류를 판매하는 곳이 아닙니다.<br>
수많은 제품 중에서 <strong>트렌드, 희소성, 그리고 소장 가치</strong>를 기준으로
셀러가 직접 한 벌 한 벌 엄선한 <strong>프리미엄 세컨핸드 숍</strong>입니다.
<br><br>
한국에서 태국으로 해상 운송되는 구제 의류는 무게 기준으로 운임이 책정됩니다.<br>
저렴한 제품도, 고가의 제품도 무게는 크게 다르지 않습니다.<br>
그렇기 때문에 저희는 처음부터 <strong>가치 있는 것만</strong> 담기로 했습니다.
<br><br>
모든 제품은 의류가 손상되지 않도록 <strong>개별 비닐 포장 후 박스로 안전하게 배송</strong>됩니다.<br>
압축 포장이나 마대 포장은 절대 사용하지 않습니다.
<br><br>
✅ <strong>100% 정품만 취급합니다.</strong><br>
저희 제품은 모두 브랜드가 확인된 진품이며, 셀러의 안목으로 직접 선별된 특별한 한 벌입니다."""
        },
        'EN': {
            'headline': 'Every piece here was chosen for a reason.',
            'body': """We're not your average secondhand shop.<br>
We specialize in <strong>premium pre-loved fashion</strong> — carefully handpicked by our in-house seller
for their trend relevance, rarity, and collectible value.
<br><br>
Shipping secondhand clothing from Korea to Thailand by sea means paying freight by weight.<br>
Since price doesn't affect weight, we made a deliberate choice: <strong>only bring what's truly worth it.</strong>
<br><br>
Every item is <strong>individually wrapped and shipped in boxes</strong> to ensure it arrives in pristine condition.<br>
We never use compression packing or bulk baling — because quality deserves to be treated that way.
<br><br>
✅ <strong>100% authentic, always.</strong><br>
Every piece in our store is a verified genuine item, personally sourced and selected by our seller."""
        },
        'TH': {
            'headline': 'ทุกชิ้นที่เราเลือก มีเหตุผลเสมอ',
            'body': """เราไม่ใช่ร้านเสื้อผ้ามือสองทั่วไป<br>
เราคัดสรร <strong>เสื้อผ้าพรีเมียมมือสอง</strong> จากเกาหลีโดยเฉพาะ
ทุกชิ้นผ่านการคัดเลือกด้วยตัวเองจากเซลเลอร์ของเรา โดยพิจารณาจากเทรนด์ ความหายาก และคุณค่าในการสะสม
<br><br>
การขนส่งเสื้อผ้ามือสองจากเกาหลีมาไทยทางเรือนั้นคิดราคาตามน้ำหนัก<br>
เสื้อราคาถูกหรือแพงก็หนักพอๆ กัน เราจึงเลือกที่จะ <strong>นำเข้าเฉพาะสิ่งที่คุ้มค่าจริงๆ</strong> เท่านั้น
<br><br>
ทุกชิ้น<strong>ถูกห่อด้วยพลาสติกแยกชิ้น และจัดส่งในกล่อง</strong>เพื่อให้เสื้อผ้าถึงมือคุณในสภาพสมบูรณ์<br>
เราไม่ใช้การอัดแน่นหรือบรรจุกระสอบ เพราะเราใส่ใจในคุณภาพของสินค้าทุกชิ้น
<br><br>
✅ <strong>สินค้าของเราเป็นของแท้ 100% ทุกชิ้น</strong><br>
คัดมาเองโดยเซลเลอร์ผู้มีประสบการณ์ ตรวจสอบแล้วว่าเป็นของแท้ทุกชิ้น"""
        }
    }

    _content = _about_texts.get(lang_code, _about_texts['EN'])

    # 다크모드에서도 확실히 보이도록 흰 배경 카드로 감쌈
    st.markdown(f"""
<div style="
    background: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 14px;
    padding: 28px 32px;
    margin: 0 auto;
    max-width: 860px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.08);
">
  <p style="font-size:20px; font-weight:800; margin-bottom:16px; color:#1a1a2e; line-height:1.4;">
    {_content['headline']}
  </p>
  <div style="font-size:17px; line-height:2.1; color:#2c2c3a;">
    {_content['body']}
  </div>
</div>
    """, unsafe_allow_html=True)

    # 소개 페이지 콘텐츠 끝 (st.stop() 없이 계속 진행 → 사이드바 필터가 항상 렌더됨)
    pass  # 이어서 사이드바 auth/필터 코드 실행

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
    # 4. Remove green block effect (Use markdown instead of success)
    st.sidebar.markdown(f"{T['welcome']}, **{st.session_state['user']['name']}**님!")
    
    # 2. Logout as text click (Styled via CSS below or just a clean button)
    # To make it look like text, we can use a custom style or just a minimal button.
    # Here we stick to button for functionality but add a class or style if needed.
    # For now, we'll keep it as a button but we can inject CSS to make sidebar buttons look flat if requested.
    # User asked for "Text click way". 
    # We will wrap it in a container and inject CSS *specifically* for this button if possible, 
    # OR we can assume it's the only button here.
    
    # CSS to make the logout button look like a red text link
    st.sidebar.markdown("""
        <style>
            /* Target the logout button in sidebar */
            div[data-testid="stSidebar"] .stButton > button {
                background-color: transparent;
                border: none;
                color: #ff4b4b; /* Red text */
                text-decoration: underline;
                padding: 0;
            }
            div[data-testid="stSidebar"] .stButton > button:hover {
                color: #ff0000;
                text-decoration: none;
            }
        </style>
    """, unsafe_allow_html=True)
    
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

# [Logic] Handle Query Params for Liking (Mobile Fix)
# We use query params to trigger likes from HTML links to ensure layout control.
try:
    # Attempt to get query params (Streamlit 1.30+)
    q_params = st.query_params
    if 'toggle_like' in q_params:
        target_code = q_params['toggle_like']
        
        if st.session_state['user']:
            # Perform Like
            am.toggle_like(st.session_state['user']['user_id'], target_code)
            # Notify user nicely (optional, or just rerun)
            # st.toast(f"Wishlist Updated!", icon="❤️")
        else:
            st.toast(T['login_required'], icon="🔒")
            
        # Clear param to prevent loop
        if 'toggle_like' in st.query_params:
            del st.query_params['toggle_like']
            
        # Rerun to refresh state
        st.rerun()
except Exception as e:
    # Fallback or older streamlit version handling could go here
    pass

# st.sidebar.header(T['filter']) # Removed as requested

# ... (Previous Code for Sidebar Status / Search) ...

# [DEBUG / INFO] Status
if not df.empty:
    # Removed "Loaded from..." info and Reload button as requested
    # Added simple total count
    count_text = T['total_simple'].format(total=len(df))
    st.sidebar.markdown(f"**{count_text}**")
    
# [Moved] Filter by My Wishlist (If Logged In) - Moved ABOVE search
if st.session_state['user']:
    # [NEW] Toggle Button Logic (Instead of Checkbox)
    # 1. Initialize logic state
    if 'show_wishlist' not in st.session_state:
        st.session_state.show_wishlist = False
        
    # 2. Toggle Function
    def toggle_wishlist_view():
        st.session_state.show_wishlist = not st.session_state.show_wishlist
        
    # 3. Determine Button Label/Style
    if st.session_state.show_wishlist:
        btn_label = f"❤️ {T['my_wishlist']} (ON)"
        # You could use type="primary" for active state if supported by theme, or just text
        btn_type = "primary"
    else:
        btn_label = f"🤍 {T['my_wishlist']} (OFF)"
        btn_type = "secondary"
        
    # 4. Render Button
    # Full width button for better mobile touch target
    # Use on_click callback to handle state toggling cleanly
    st.sidebar.button(btn_label, type=btn_type, on_click=toggle_wishlist_view, use_container_width=True)
    
    # 5. Set the flag for downstream filtering logic
    show_my_wishlist = st.session_state.show_wishlist


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

# [NEW] 2.5 Upper Category Filter
# Sort by count (descending)
if 'upper_category' in df.columns:
    upper_counts = df['upper_category'].value_counts()
    all_upper = upper_counts.index.tolist()
else:
    all_upper = []
    
selected_upper = st.sidebar.multiselect(T['upper_category'], all_upper)

# 3. Category Filter
# Sort by count (descending)
if 'category' in df.columns:
    if selected_upper and 'upper_category' in df.columns:
        filtered_sub = df[df['upper_category'].isin(selected_upper)]
        cat_counts = filtered_sub['category'].value_counts()
    else:
        cat_counts = df['category'].value_counts()
        
    all_categories = cat_counts.index.tolist()
else:
    all_categories = []
    
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

# --- Sort + 카탈로그 그리드: 소개 페이지일 때는 건너뜀 ---
if st.session_state.get('sidebar_page', 'catalog') == 'catalog':
    sort_option = st.selectbox(T['sort'], T['sort_options'])

    # ─── 인기 브랜드 Top 10 바 ───────────────────────────────────────────────
    # 브랜드 컬럼에서 갯수 내림차순으로 10개 추출
    if 'brand' in df.columns and not df.empty:
        top_brands = (
            df['brand']
            .dropna()
            .astype(str)
            .str.strip()
            .replace('', float('nan'))
            .dropna()
        )
        top_brands = top_brands[top_brands != 'Unknown']
        top_brands = top_brands.value_counts().head(10).index.tolist()
        if top_brands:
            # ── query_params 기반 브랜드 바 ──────────────────────────────────
            # 클릭 시 ?bb=브랜드명 파라미터를 URL에 반영 → Streamlit 리로드 시 읽음
            # st.button 일절 사용 안 함 → 버튼 박스 없음

            # 현재 선택된 브랜드 (query_param 우선, 없으면 session_state)
            _qb = st.query_params.get('bb', '')
            if _qb:
                # URL 파라미터가 있으면 session_state에 동기화
                st.session_state['selected_brands_bar'] = [_qb]
            _bar_selected = st.session_state.get('selected_brands_bar', [])

            # 라벨
            _brand_bar_label = {
                'KO': '🔥 인기 브랜드',
                'EN': '🔥 Popular Brands',
                'TH': '🔥 แบรนด์ยอดนิยม'
            }.get(lang_code, '🔥 Popular Brands')

            # ── st.button 부활 (기능 보장) + JS 스타일링 ───────────────────
            # window.top 접근 불가 이슈 해결을 위해 Native st.button 사용
            # 버튼 박스 제거는 JS로 해당 버튼(라벨에 식별자 포함)을 찾아 스타일 클래스 적용

            # 식별용 Zero Width Space (\u200b)
            # 버튼 라벨에 이걸 넣어서 JS가 이 버튼만 찾아서 스타일을 바꾸게 함
            import streamlit.components.v1 as components_v1
            
            # 1. CSS 정의 (브랜드 버튼용 클래스)
            st.markdown("""
            <style>
            .brand-text-btn {
                border: none !important;
                background: transparent !important;
                box-shadow: none !important;
                padding: 0 !important;
                color: #333 !important;
                font-size: 17px !important;
                font-weight: 800 !important;
                cursor: pointer !important;
                line-height: 1.5 !important;
                text-transform: uppercase !important;
                letter-spacing: 0.02em !important;
                min-height: 0 !important;
                height: auto !important;
                margin: 0 !important;
            }
            .brand-text-btn:hover {
                color: #e63946 !important;
                text-decoration: underline !important;
                background: transparent !important;
            }
            .brand-text-btn:focus, .brand-text-btn:active {
                color: #e63946 !important;
                background: transparent !important;
                border: none !important;
                outline: none !important;
            }
            .brand-text-btn p {
                font-size: 17px !important;
                font-weight: 800 !important;
                margin: 0 !important;
                padding: 0 !important;
            }
            /* 선택된 상태 (JS로 클래스 추가 예정) */
            .brand-text-btn-active {
                color: #e63946 !important;
                text-decoration: underline !important;
            }
            .brand-text-btn-active p {
                color: #e63946 !important;
            }
            </style>
            """, unsafe_allow_html=True)

            # 2. JS 주입 (버튼 찾아서 클래스 부여)
            # \u200b 가 포함된 버튼을 찾아 .brand-text-btn 클래스 추가
            _js_script = """
            <script>
            function styleBrandButtons() {
                try {
                    const buttons = window.parent.document.querySelectorAll('button');
                    buttons.forEach(btn => {
                        if (btn.innerText.includes('\\u200b')) {
                            btn.classList.add('brand-text-btn');
                            // 선택된 버튼(active) 처리 확인 (빨간색)
                            // st.button은 클릭 후 리로드되므로 상태 유지는 Python -> 재렌더링 시 적용
                            // 다만 :focus 상태 등이 남을 수 있으므로 강제 스타일링
                            
                            // 텍스트에서 \u200b 제거된 것처럼 보이게? (이미 안보임)
                        }
                    });
                } catch (e) { console.log(e); }
            }
            // 0.5초 간격으로 시도 (Streamlit 렌더링 타이밍 이슈 대응)
            setTimeout(styleBrandButtons, 50);
            setTimeout(styleBrandButtons, 300);
            setTimeout(styleBrandButtons, 1000);
            </script>
            """
            components_v1.html(_js_script, height=0)

            st.markdown(
                f"<div style='font-size:11px; font-weight:700; color:#888; letter-spacing:0.08em; margin-bottom:5px; text-transform:uppercase;'>{_brand_bar_label}</div>",
                unsafe_allow_html=True
            )

            # 3. 버튼 배치 (구분자 포함하여 컬럼 나누기)
            # n개 브랜드 -> 2n-1개 컬럼 (브랜드, 구분자, 브랜드, 구분자...)
            # 비율: 브랜드(auto) 구분자(작게)
            # Streamlit 컬럼 비율은 list로 전달
            _col_specs = []
            for _i in range(len(top_brands)):
                _col_specs.append(1) # 브랜드
                if _i < len(top_brands) - 1:
                    _col_specs.append(0.05) # 구분자

            _cols = st.columns(_col_specs)
            
            for _i, _bname in enumerate(top_brands):
                _idx_col = _i * 2
                with _cols[_idx_col]:
                    _is_active = _bname in _bar_selected
                    # 버튼 생성 (\u200b 포함)
                    # 선택된 경우 빨간색 스타일을 위해 JS가 아닌 Python 로직 필요하지만
                    # st.button 자체 스타일 한계로 CSS 클래스 주입 방식 사용
                    # 활성 상태면 CSS에서 색상 처리를 위해 별도 마킹이 필요하나,
                    # 단순하게 선택 상태면 ★ 같은 마커를 붙이거나 색상을 다르게? 
                    # -> JS가 텍스트 내용을 보고 active 클래스 추가하도록 텍스트 변형
                    
                    # 선택된 경우 텍스트 뒤에 또다른 식별자(Zero Width Joiner \u200d) 추가하여 JS가 인식하게 함
                    _label = f"\u200b{_bname}" + ("\u200d" if _is_active else "")
                    
                    if st.button(_label, key=f"btn_brand_{_bname}", use_container_width=True):
                        # 토글 로직
                        if _bname in st.session_state.get('selected_brands_bar', []):
                            st.session_state['selected_brands_bar'] = []
                        else:
                            st.session_state['selected_brands_bar'] = [_bname]
                        st.rerun()

                    # 선택된 버튼이면 JS로 active 클래스 추가 ( script 재활용 )
                    if _is_active:
                         # 이 부분은 위의 JS가 \u200d 를 감지해서 처리하도록 함
                         pass

                # 구분자
                if _i < len(top_brands) - 1:
                    _idx_sep = _i * 2 + 1
                    with _cols[_idx_sep]:
                         st.markdown("<div style='text-align:center;color:#ccc;line-height:2.0;font-size:14px;user-select:none;'>|</div>", unsafe_allow_html=True)
            
            # JS 업데이트: \u200d가 있으면 active 클래스 추가
            _js_active_script = """
            <script>
            function markActiveButtons() {
                try {
                    const buttons = window.parent.document.querySelectorAll('button');
                    buttons.forEach(btn => {
                        if (btn.innerText.includes('\\u200d')) {
                            btn.classList.add('brand-text-btn-active');
                        }
                    });
                } catch(e) {}
            }
            setTimeout(markActiveButtons, 100);
            setTimeout(markActiveButtons, 500);
            </script>
            """
            components_v1.html(_js_active_script, height=0)



            # 브랜드 바 선택값을 기존 사이드바 브랜드 필터에 반영
            if _bar_selected and not selected_brands:
                selected_brands = _bar_selected
            elif _bar_selected and selected_brands:
                selected_brands = list(set(selected_brands) & set(_bar_selected)) or _bar_selected


    # ─── 카탈로그 필터링 / 정렬 / 그리드 ───────────────────────────────────
    # 소개 페이지일 때는 이 블록 전체가 실행되지 않음
    filtered_df = df.copy()

    # Filter by Arrival Status (Show Arrived Only)
    if show_arrived_only:
        def has_arrival_info(val):
            s = str(val).strip().lower()
            return bool(s and s != 'nan' and s != 'nat' and s != 'none' and s != '')
        if 'arrival_date' in filtered_df.columns:
            mask_has_arrival = filtered_df['arrival_date'].apply(has_arrival_info)
            filtered_df = filtered_df[~mask_has_arrival]

    # Filter by My Wishlist (Logic updated to use the checkbox defined earlier)
    if st.session_state['user']:
        if show_my_wishlist:
            my_likes_ids = am.get_user_likes(st.session_state['user']['user_id'])
            if 'code' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['code'].astype(str).isin(my_likes_ids)]

    if debug_mode:
        st.warning("Debug Mode On")
        st.write("### Data Preview")
        preview_cols = [c for c in ['code', 'name', 'stock', 'price'] if c in filtered_df.columns]
        st.dataframe(filtered_df[preview_cols].head())

    # Filter: Status ('onsale' vs 'out of stock')
    if 'stock' in filtered_df.columns:
        filtered_df['stock_norm'] = filtered_df['stock'].astype(str).str.lower().str.strip()
        if not show_sold_out:
            mask = filtered_df['stock_norm'].str.contains('out of stock', na=False)
            filtered_df = filtered_df[~mask]

    # Filter: Search (Name OR Code)
    if search_query:
        search_col_matches = filtered_df['name'].str.contains(search_query, case=False, na=False)
        if 'code' in filtered_df.columns:
            search_col_matches = search_col_matches | filtered_df['code'].astype(str).str.contains(search_query, case=False, na=False)
        if 'id' in filtered_df.columns:
            search_col_matches = search_col_matches | filtered_df['id'].astype(str).str.contains(search_query, case=False, na=False)
        filtered_df = filtered_df[search_col_matches]

    # Filter: Brand
    if selected_brands:
        filtered_df = filtered_df[filtered_df['brand'].isin(selected_brands)]

    # Filter: Upper Category
    if selected_upper:
        if 'upper_category' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['upper_category'].isin(selected_upper)]

    # Filter: Category
    if selected_categories:
        filtered_df = filtered_df[filtered_df['category'].isin(selected_categories)]

    # Filter: Size
    if selected_sizes:
        filtered_df = filtered_df[filtered_df['size'].isin(selected_sizes)]

    # Filter: Price
    filtered_df = filtered_df[(filtered_df['price'] >= filter_min) & (filtered_df['price'] <= filter_max)]

    # --- Sorting ---
    sort_map = {
        "최신순": "Newest", "Newest (Newest)": "Newest", "ล่าสุด (Newest)": "Newest",
        "가격 낮은순": "Price_Low", "Price: Low to High (Low-High)": "Price_Low", "ราคา: ต่ำไปสูง (Low-High)": "Price_Low",
        "가격 높은순": "Price_High", "Price: High to Low (High-Low)": "Price_High", "ราคา: สูงไปต่ำ (High-Low)": "Price_High",
        "이름순": "Name", "Name (Name)": "Name", "ชื่อ (Name)": "Name"
    }
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
            parsed_dates = pd.to_datetime(filtered_df['updated_at'], format='%m/%d', errors='coerce')
            mask = parsed_dates.isna()
            if mask.any():
                parsed_dates.loc[mask] = pd.to_datetime(filtered_df.loc[mask, 'updated_at'], errors='coerce')
            filtered_df['sort_date'] = parsed_dates
            filtered_df = filtered_df.sort_values(by='sort_date', ascending=False)
    elif current_sort == "Price_Low":
        filtered_df = filtered_df.sort_values(by='price', ascending=True)
    elif current_sort == "Price_High":
        filtered_df = filtered_df.sort_values(by='price', ascending=False)
    elif current_sort == "Name":
        filtered_df = filtered_df.sort_values(by='name', ascending=True)

    # --- Pagination ---
    if 'page' not in st.session_state:
        st.session_state.page = 1

    items_per_page = 12
    total_items = len(filtered_df)
    total_pages = max(1, (total_items - 1) // items_per_page + 1)

    if st.session_state.page > total_pages:
        st.session_state.page = 1

    start_idx = (st.session_state.page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    page_items = filtered_df.iloc[start_idx:end_idx]

    # --- Display Grid (3 per row) ---
    st.divider()
    st.subheader(T['total_items'].format(total=total_items, current=len(page_items)))

    all_counts = am.get_all_like_counts()
    my_likes_set = set()
    if st.session_state['user']:
        my_likes_set = am.get_user_likes(st.session_state['user']['user_id'])

    page_items = page_items.reset_index(drop=True)

    for i in range(0, items_per_page, 3):
        batch = page_items.iloc[i:i+3]
        if batch.empty:
            break

        cols = st.columns(3)
        for idx, row in batch.iterrows():
            col_idx = idx % 3
            with cols[col_idx]:
                status_val = str(row.get('stock', '')).lower().strip()
                is_sold = 'out of stock' in status_val or 'sold' in status_val

                opacity_style = "opacity: 0.5;" if is_sold else ""
                st.markdown(f'<div style="{opacity_style} position: relative;">', unsafe_allow_html=True)

                img_url = get_image_url(row.get('image_file_id'))
                img_html = ""
                if img_url:
                    img_html = f'<img src="{img_url}" style="width:100%; aspect-ratio: 9/8; object-fit: cover; object-position: top; border-radius:5px;" loading="lazy">'
                else:
                    img_html = f'<div style="width:100%; aspect-ratio: 9/8; background:#f0f0f0; display:flex; align-items:center; justify-content:center; border-radius:5px;">{T["no_image"]}</div>'

                arrival_val = str(row.get('arrival_date', '')).strip()
                is_arrival_valid = arrival_val and arrival_val.lower() != 'nan' and arrival_val.lower() != 'nat' and len(arrival_val) > 0

                # ─── 가격 / 할인율 계산 (이미지 오버레이보다 먼저 계산) ─────────────
                import math
                price_val = row.get('price', 0)
                price_plain = f"{T['currency_symbol']}{price_val:,}"  # type: ignore

                _orig_price = row.get('original_price', float('nan'))
                try:
                    _orig_price = float(_orig_price)
                    _has_discount = not math.isnan(_orig_price) and _orig_price > 0 and _orig_price > price_val
                except (TypeError, ValueError):
                    _has_discount = False


                if _has_discount:
                    _discount_pct = round((1 - price_val / _orig_price) * 100)
                    _discount_badge = f'<div style="position:absolute; top:8px; right:8px; background:rgba(30,30,30,0.82); color:#fff; font-size:14px; font-weight:900; border-radius:6px; padding:4px 9px; z-index:20; letter-spacing:0.5px;">{_discount_pct}%</div>'
                else:
                    _discount_badge = ''

                link_target = img_url if img_url else ""

                if is_sold:
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
                        {_discount_badge}
                    </div>
                    """
                    st.markdown(overlay_html, unsafe_allow_html=True)
                elif is_arrival_valid:
                    final_val = arrival_val
                    if arrival_val.upper() == 'TBD' or arrival_val == '미정':
                        final_val = T['arrival_tbd']
                    display_text = f"{T['arrival_title']} : {final_val}"
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
                        {_discount_badge}
                    </div>
                    """
                    st.markdown(overlay_html, unsafe_allow_html=True)
                else:
                    if link_target:
                        overlay_html = f"""
                        <div style="position: relative; width: 100%;">
                            <a href="{link_target}" target="_blank" style="display:block; cursor:pointer;">{img_html}</a>
                            {_discount_badge}
                        </div>
                        """
                        st.markdown(overlay_html, unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div>{img_html}</div>", unsafe_allow_html=True)

                code = row.get('code', '-')
                brand = row.get('brand', 'Unknown')
                name = row.get('name', 'No Name')
                # price_val, price_plain은 이미 위 할인율 계산 블록에서 정의됨

                # ─── 가격 표시: 출고가 취소선 + 판매가 파란색 ───────────────────
                if is_sold:
                    price_display = f"<span style='color:#999; text-decoration:line-through; font-size:16px;'>{T['sold_out']}</span>"
                    price_str = price_plain
                elif _has_discount:
                    # 출고가(취소선 회색) + 판매가(파란색 굵게)
                    _orig_plain = f"{T['currency_symbol']}{int(_orig_price):,}"
                    price_display = (
                        f"<span style='color:#aaa; text-decoration:line-through; font-size:14px; margin-right:5px;'>{_orig_plain}</span>"
                        f"<span style='color:#007bff; font-weight:900; font-size:20px;'>{price_plain}</span>"
                    )
                    price_str = price_plain
                else:
                    price_display = f"<span style='color:#007bff; font-weight:bold; font-size:20px;'>{price_plain}</span>"
                    price_str = price_plain

                size = row.get('size', '-')
                condition = row.get('condition', '-')

                st.markdown(f"<div class='product-title'>[{brand}] {name}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='product-price'>{price_display}</div>", unsafe_allow_html=True)

                m_col1, m_col2 = st.columns([7, 3])
                with m_col1:
                    st.markdown(f"""
                    <div style="font-size: 13px; color: #666; margin-top: 5px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                        Code : {code} | {T['size']} : {size} | Cond : {condition}
                    </div>
                    """, unsafe_allow_html=True)

                    measured = row.get('measured_size', '-')
                    if measured and str(measured).lower() != 'nan' and str(measured).strip() != '':
                        st.markdown(f"""
                        <div style="font-size: 15px; color: #333; margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-weight: bold;">
                            {T['measured_size']} : {measured}
                        </div>
                        """, unsafe_allow_html=True)

                with m_col2:
                    p_code = str(code)
                    likes_num = all_counts.get(p_code, 0)
                    if st.session_state.get('user'):
                        is_liked = p_code in my_likes_set
                        heart_icon = "❤️" if is_liked else "🤍"
                        if st.button(f"{heart_icon} {likes_num}", key=f"like_{p_code}", help="Add to Wishlist"):
                            am.toggle_like(st.session_state['user']['user_id'], p_code)
                            st.rerun()
                    else:
                        if st.button(f"🤍 {likes_num}", key=f"like_{p_code}"):
                            st.toast(T['login_required'], icon="🔒")

                st.markdown('</div>', unsafe_allow_html=True)

                with st.expander(T['detail_btn']):
                    st.write(T['desc_title'])
                    desc_text = row.get('description')
                    if not desc_text or str(desc_text).strip() == '-' or str(desc_text).strip() == '':
                        desc_text = row.get('product description')
                    if not desc_text or str(desc_text).strip() == '-' or str(desc_text).strip() == '':
                        desc_text = row.get('detail')
                    if not desc_text or str(desc_text).strip() == '-' or str(desc_text).strip() == '':
                        desc_text = '-'
                    st.write(desc_text)
                    st.write(f"---")
                    st.write(f"{T['date_title']}: {row.get('updated_at', '-')}")

                    if not is_sold:
                        if st.session_state['user']:
                            u_id = st.session_state['user']['user_id']
                            u_name = st.session_state['user'].get('name', 'Unknown')
                            contact_text = T['contact_msg'].format(
                                code=code, brand=brand, name=name, price=price_str,
                                user_id=u_id, user_name=u_name
                            )
                            import urllib.parse
                            encoded_msg = urllib.parse.quote(contact_text)
                            LINE_ID = "@102ipvys"
                            line_url = f"https://line.me/R/oaMessage/{LINE_ID}/?{encoded_msg}"
                            st.markdown(f"""
                            <a href="{line_url}" target="_blank" style="text-decoration:none;">
                                <button style="width:100%; background-color:#06C755; color:white; border:none; padding:10px; border-radius:5px; font-weight:bold; cursor:pointer;">
                                    {T['line_btn']}
                                </button>
                            </a>
                            <div style="height: 30px;"></div>
                            """, unsafe_allow_html=True)
                        else:
                            if st.button(T['line_btn'], key=f"guest_line_{code}"):
                                st.toast(T['login_required'], icon="🔒")
                                st.error(T['login_required'])
                            st.markdown('<div style="height: 30px;"></div>', unsafe_allow_html=True)
                    else:
                        st.error(T['sold_btn'])

                st.markdown("---")

    # --- Pagination Controls ---
    if total_pages > 1:
        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

        current_page = st.session_state.page
        chunk_size = 8
        start_page = ((current_page - 1) // chunk_size) * chunk_size + 1
        end_page = min(start_page + chunk_size - 1, total_pages)

        page_options = []
        if start_page > 1:
            page_options.append("◀")
        page_options.extend(range(start_page, end_page + 1))
        if end_page < total_pages:
            page_options.append("▶")

        st.markdown("""
        <style>
            div[data-testid="stRadio"] {
                display: flex !important;
                justify-content: center !important;
                align-items: center !important;
                width: 100% !important;
            }
            div[data-testid="stRadio"] div[role="radiogroup"] {
                display: flex !important;
                justify-content: center !important;
                align-items: center !important;
                flex-wrap: nowrap !important;
                margin: 0 auto !important;
                width: fit-content !important;
            }
            div[data-testid="stRadio"] label > div:first-child {
                display: none !important;
            }
            div[data-testid="stRadio"] label {
                margin-right: 0px !important;
                padding: 0 5px !important;
                border: none !important;
                background-color: transparent !important;
                cursor: pointer !important;
                min-width: 25px;
                text-align: center;
            }
            div[data-testid="stRadio"] label:hover {
                background-color: transparent !important;
                text-decoration: underline;
                color: #ff4b4b;
            }
        </style>
        """, unsafe_allow_html=True)

        try:
            current_index = page_options.index(current_page)
        except ValueError:
            current_index = 0

        col_left, col_center, col_right = st.columns([1, 1, 1])
        with col_center:
            selected_p = st.radio(
                "Go to page:",
                options=page_options,
                index=current_index,
                horizontal=True,
                label_visibility="collapsed",
                key=f"pagination_unified_{start_page}"
            )

        if selected_p == "◀":
            st.session_state.page = start_page - 1
            st.rerun()
        elif selected_p == "▶":
            st.session_state.page = end_page + 1
            st.rerun()
        elif selected_p != st.session_state.page:
            st.session_state.page = selected_p
            st.rerun()

        st.markdown(f"<div style='text-align: center; color: #666; margin-top: 5px;'>Page {st.session_state.page} / {total_pages}</div>", unsafe_allow_html=True)


