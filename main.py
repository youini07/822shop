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
        'line_btn': "🟢 ติดต่อซื้อทาง Line (คลิก)",
        'sold_btn': "🚫 สินค้าหมดแล้วค่ะ",
        'currency_symbol': "฿",
        'contact_msg': "[Code: {code}] สนใจสั่งซื้อสินค้า: {brand} {name} ({price})"
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
        'line_btn': "🟢 Buy via Line",
        'sold_btn': "🚫 Item Sold Out",
        'currency_symbol': "฿",
        'contact_msg': "[Code: {code}] I would like to buy: {brand} {name} ({price})"
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
        'line_btn': "🟢 라인으로 구매 문의 (Line Contact)",
        'sold_btn': "🚫 품절된 상품입니다",
        'currency_symbol': "฿",
        'contact_msg': "[Code: {code}] 제품으로 문의한 제품입니다. ({brand} {name} {price})"
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

if os.path.exists("822logo.png"):
    # Center Logo: Use HTML/CSS with Base64 to guarantee centering on mobile
    img_base64 = get_base64_of_bin_file("822logo.png")
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

# --- Sidebar Filters ---
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

# 7. Debug Mode
debug_mode = st.sidebar.checkbox("🛠️ Debug Mode", value=False)

# --- Sort Options ---
sort_option = st.selectbox(T['sort'], T['sort_options'])

# --- App Logic: Filtering ---
filtered_df = df.copy()

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
        image_data = fetch_image_from_url(img_url)
        
        # Prepare Image HTML (Base64 for exact overlay control)
        img_html = ""
        if image_data:
            # Convert bytes to base64
            b64_img = base64.b64encode(image_data.getvalue()).decode()
            img_src = f"data:image/jpeg;base64,{b64_img}"
            img_html = f'<img src="{img_src}" style="width:100%; border-radius:5px;">'
        elif img_url:
            img_html = f'<img src="{img_url}" style="width:100%; border-radius:5px;">'
        else:
            img_html = f'<div style="width:100%; height:200px; background:#f0f0f0; display:flex; align-items:center; justify-content:center; border-radius:5px;">{T["no_image"]}</div>'
        
        # Render Image + Overlay (Centered)
        # Render Image + Overlay (Centered)
        # Priority: Sold Out > Arrival Date > Normal
        
        # Render Image + Overlay (Centered)
        # Priority: Sold Out > Arrival Date > Normal
        
        arrival_val = str(row.get('arrival_date', '')).strip()
        # Check if arrival_date is valid (not nan/empty/nat)
        is_arrival_valid = arrival_val and arrival_val.lower() != 'nan' and arrival_val.lower() != 'nat' and len(arrival_val) > 0
        
        if is_sold:
             st.markdown(f"""
             <div style="position: relative; width: 100%;">
                <div style="opacity: 0.5;">
                    {img_html}
                </div>
                <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); 
                            color: white; font-size: 20px; font-weight: bold; 
                            background-color: rgba(0,0,0,0.6); padding: 10px 20px; border-radius: 5px;
                            pointer-events: none; white-space: nowrap; z-index: 10;">
                    {T['sold_out']}
                </div>
             </div>
             """, unsafe_allow_html=True)
        elif is_arrival_valid:
             # Arrival Date Overlay
             # Text: "{T['arrival_title']} : {arrival_date}"
             # Handling "TBD" / "미정" explicitly
             
             final_val = arrival_val
             if arrival_val.upper() == 'TBD' or arrival_val == '미정':
                 final_val = T['arrival_tbd']
                 
             display_text = f"{T['arrival_title']} : {final_val}"
             
             # Icon URL (Google Drive direct link)
             icon_url = "https://drive.google.com/uc?id=1r4Yz3siSebPAp20uRbjBDyDA0x07BKFx"
             
             st.markdown(f"""
             <div style="position: relative; width: 100%;">
                <div style="opacity: 0.5;">
                    {img_html}
                </div>
                <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); 
                            color: white; font-size: 22px; font-weight: bold; 
                            background-color: rgba(0,0,0,0.7); padding: 15px 30px; border-radius: 10px;
                            pointer-events: none; z-index: 10; text-align: center; display: flex; flex-direction: column; align-items: center;">
                    <img src="{icon_url}" style="width: 40px; height: 40px; margin-bottom: 8px;">
                    <span style="white-space: nowrap;">{display_text}</span>
                </div>
             </div>
             """, unsafe_allow_html=True)
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
                # Line Contact
                contact_text = T['contact_msg'].format(code=code, brand=brand, name=name, price=price_str)
                
                # Encode message for URL
                import urllib.parse
                encoded_msg = urllib.parse.quote(contact_text)
                
                # USER PROVIDED BASIC ID: @102ipvys
                # Use Official Account Auto-Fill Link
                LINE_ID = "@102ipvys"
                line_url = f"https://line.me/R/oaMessage/{LINE_ID}/?{encoded_msg}"
                
                # Line Button (Direct Auto-fill)
                # Added vertical spacing margin below button as requested so it doesn't touch the edge
                st.markdown(f"""
                <a href="{line_url}" target="_blank" style="text-decoration:none;">
                    <button style="width:100%; background-color:#06C755; color:white; border:none; padding:10px; border-radius:5px; font-weight:bold; cursor:pointer;">
                        {T['line_btn']}
                    </button>
                </a>
                <div style="height: 30px;"></div>
                """, unsafe_allow_html=True)
            else:
                 # Sold out button (disabled) or just message
                 st.error(T['sold_btn'])

        st.markdown("---")
