import streamlit as st
import pandas as pd
from data_loader import load_data, get_image_url, fetch_image_from_url

# ... (Previous code)

# --- Page Config ---
st.set_page_config(
    page_title="Vintage Catalog",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS ---
st.markdown("""
<style>
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
with st.spinner('상품 정보를 불러오는 중입니다...'):
    df = load_data()

# --- Localization ---
if 'lang' not in st.session_state:
    st.session_state.lang = 'TH' # Default to Thai

lang_dict = {
    'TH': {
        'title': "ร้านเสื้อผ้าวินเทจคัดเกรด (822 Shop)",
        'filter': "🔍 ตัวกรอง (Filter)",
        'search': "ค้นหาสินค้า",
        'search_placeholder': "เช่น: แจ็คเก็ต Nike",
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
        'date_title': "📅 วันที่ลงขาย",
        'line_btn': "🟢 ติดต่อซื้อทาง Line (คลิก)",
        'sold_btn': "🚫 สินค้าหมดแล้วค่ะ",
        'currency_symbol': "฿",
        'contact_msg': "สวัสดีค่ะ สนใจสั่งซื้อ [{brand}] {name} ({price}) ค่ะ"
    },
    'EN': {
        'title': "Curated Vintage Clothing Shop",
        'filter': "🔍 Filter",
        'search': "Search Product",
        'search_placeholder': "Ex: Nike Jacket",
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
        'date_title': "📅 Date Added",
        'line_btn': "🟢 Buy via Line",
        'sold_btn': "🚫 Item Sold Out",
        'currency_symbol': "฿",
        'contact_msg': "Hello, I want to buy [{brand}] {name} ({price})."
    },
    'KR': {
        'title': "엄선된 구제 의류를 만나보세요.",
        'filter': "🔍 필터",
        'search': "상품명 검색",
        'search_placeholder': "예: 나이키 자켓",
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
        'date_title': "📅 등록일",
        'line_btn': "🟢 라인으로 구매 문의 (Line Contact)",
        'sold_btn': "🚫 품절된 상품입니다",
        'currency_symbol': "₩",
        'contact_msg': "안녕하세요, [{brand}] {name} ({price}) 구매하고 싶습니다."
    }
}

# Language Toggle (Sidebar Top)
st.sidebar.markdown("### 🌐 Language")
lang_code = st.sidebar.radio("Language", ('TH', 'EN', 'KR'), horizontal=True, label_visibility="collapsed")
st.session_state.lang = lang_code
T = lang_dict[lang_code]

# --- Header ---
# Check for logo file, otherwise use text
import os
if os.path.exists("822logo.png"):
    # Center Logo: Use columns
    left_co, cent_co, last_co = st.columns(3)
    with cent_co:
        st.image("822logo.png", width=200)
else:
    st.title("822 SHOP")
st.markdown(T['title'])

if df.empty:
    st.warning("No products found. Please check Google Sheet.")
    st.stop()

# --- Sidebar Filters ---
st.sidebar.header(T['filter'])

# 1. Search
search_query = st.sidebar.text_input(T['search'], placeholder=T['search_placeholder'])

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
cost_range = st.sidebar.slider(T['price_range'], slider_min_val, slider_max_val, (slider_min_val, slider_max_val))

# Convert back to KRW for filtering (Same now)
filter_min = cost_range[0]
filter_max = cost_range[1]

# 6. Status Filter
show_sold_out = st.sidebar.checkbox(T['show_sold_out'], value=False)

# 7. Debug Mode
debug_mode = st.sidebar.checkbox("🛠️ Debug Mode", value=False)

# --- Sort Options ---
sort_option = st.selectbox(T['sort'], T['sort_options'])

# --- App Logic: Filtering ---
filtered_df = df.copy()

if debug_mode:
    st.warning("Debug Mode On")
    st.write("### Data Preview")
    st.dataframe(filtered_df[['name', 'image_file_id', 'status', 'price']].head())

# Filter: Status ('onsale' vs 'out of stock')
if 'status' in filtered_df.columns:
    # Normalize
    filtered_df['status_norm'] = filtered_df['status'].astype(str).str.lower().str.strip()
    if not show_sold_out:
        filtered_df = filtered_df[filtered_df['status_norm'] != 'out of stock']

# Filter: Search
if search_query:
    filtered_df = filtered_df[filtered_df['name'].str.contains(search_query, case=False, na=False)]

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
        filtered_df['updated_at'] = pd.to_datetime(filtered_df['updated_at'], errors='coerce')
        filtered_df = filtered_df.sort_values(by='updated_at', ascending=False)
elif current_sort == "Price_Low":
    filtered_df = filtered_df.sort_values(by='price', ascending=True)
elif current_sort == "Price_High":
    filtered_df = filtered_df.sort_values(by='price', ascending=False)
elif current_sort == "Name":
    filtered_df = filtered_df.sort_values(by='name', ascending=True)

# --- App Logic: Pagination ---
items_per_page = 12
total_items = len(filtered_df)
total_pages = max(1, (total_items - 1) // items_per_page + 1)

if total_pages > 1:
    st.sidebar.markdown("---")
    st.sidebar.subheader(T['page'])
    page = st.sidebar.number_input(T['page'], min_value=1, max_value=total_pages, value=1, label_visibility="collapsed")
    st.sidebar.caption(T['page_caption'].format(total=total_pages, current=page))
else:
    page = 1

# Slice Data
start_idx = (page - 1) * items_per_page
end_idx = start_idx + items_per_page
page_items = filtered_df.iloc[start_idx:end_idx]

# --- Display Grid ---
st.divider()
st.subheader(T['total_items'].format(total=total_items, current=len(page_items)))

# Responsive Grid
cols = st.columns(3) 

for idx, row in page_items.iterrows():
    col = cols[idx % 3]
    
    with col:
        # Status
        status_raw = str(row.get('status', '')).lower().strip()
        is_sold = status_raw == 'out of stock'
        
        # Opacity Style
        opacity_style = "opacity: 0.5;" if is_sold else ""
        
        # Container start
        st.markdown(f'<div style="{opacity_style}">', unsafe_allow_html=True)

        # Image
        img_url = get_image_url(row.get('image_file_id'))
        image_data = fetch_image_from_url(img_url)
        
        if image_data:
            st.image(image_data, use_container_width=True)
        else:
            if img_url:
                st.image(img_url, use_container_width=True)
            else:
                st.write(T['no_image'])
        
        # Sold Out Overlay
        if is_sold:
             st.markdown(f"<div style='background-color:rgba(0,0,0,0.7); color:white; padding:5px; text-align:center; font-weight:bold; margin-top:-30px; position:relative; z-index:100;'>SOLD OUT</div>", unsafe_allow_html=True)
  
        # Info
        brand = row.get('brand', 'Unknown')
        name = row.get('name', 'No Name')
        price_val = row.get('price', 0)
        
        # Currency: Raw value (THB directly)
        price_str = f"{T['currency_symbol']}{price_val:,}"
        
        size = row.get('size', '-')
        condition = row.get('condition', '-')
        
        # Title & Price
        st.markdown(f"<div class='product-title'>[{brand}] {name}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='product-price'>{price_str}</div>", unsafe_allow_html=True)
            
        # Meta Info
        st.caption(f"{T['size']}: {size} | Ref: {condition}")
        
        st.markdown('</div>', unsafe_allow_html=True) # End opacity div
        
        # Detail Expander
        with st.expander(T['detail_btn']):
            st.write(T['desc_title'])
            st.write(row.get('description', '-'))
            st.write(f"---")
            st.write(f"{T['date_title']}: {row.get('updated_at', '-')}")
            
            if not is_sold:
                # Line Contact
                contact_text = T['contact_msg'].format(brand=brand, name=name, price=price_str)
                LINE_LINK_ID = "주소입력" # Placeholder
                PHONE_NUMBER = "+66838688685"
                
                # Line Button
                st.markdown(f"""
                <a href="{LINE_LINK_ID}" target="_blank" style="text-decoration:none;">
                    <button style="width:100%; background-color:#06C755; color:white; border:none; padding:10px; border-radius:5px; font-weight:bold; cursor:pointer;">
                        {T['line_btn']}
                    </button>
                </a>
                <br><br>
                <a href="tel:{PHONE_NUMBER}" style="text-decoration:none;">
                    <button style="width:100%; background-color:#f8f9fa; color:black; border:1px solid #ccc; padding:10px; border-radius:5px; font-weight:bold; cursor:pointer;">
                        📞 Call {PHONE_NUMBER}
                    </button>
                </a>
                """, unsafe_allow_html=True)
            else:
                 st.button(T['sold_btn'], disabled=True, key=f"sold_{idx}")

        st.markdown("---")
