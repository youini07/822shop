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
    st.session_state.lang = 'KR'

lang_dict = {
    'KR': {
        'title': "엄선된 구제 의류를 만나보세요.",
        'filter': "🔍 필터",
        'search': "상품명 검색",
        'search_placeholder': "예: 나이키 자켓",
        'brand': "브랜드",
        'category': "카테고리",
        'size': "사이즈",
        'price_range': "가격 범위",
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
    },
    'TH': {
        'title': "Curation Vintage Clothing Shop",
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
        'line_btn': "🟢 Contact via Line",
        'sold_btn': "🚫 Item Sold Out",
        'currency_symbol': "฿",
        'contact_msg': "Hello, I want to buy [{brand}] {name} ({price})."
    }
}

# Language Toggle (Sidebar Top)
st.sidebar.markdown("### 🌐 Language")
lang_code = st.sidebar.radio("언어 선택 (Language)", ('KR', 'TH'), horizontal=True, label_visibility="collapsed")
st.session_state.lang = lang_code
T = lang_dict[lang_code]

# --- Header ---
# Check for logo file, otherwise use text
import os
if os.path.exists("822logo.png"):
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

# 5. Price Range (Convert to THB for display slider if TH selected? 
# For MVP simplicity, slider keeps underlying integer value (KRW usually), but labels might be confusing.
# Let's assume underlying data is KRW.
# Exchange Rate: 1 KRW = 0.026 THB (approx) / 1 THB = 38 KRW
EXCHANGE_RATE = 0.026 if lang_code == 'TH' else 1.0

min_price = int(df['price'].min() * EXCHANGE_RATE) if not df.empty else 0
max_price = int(df['price'].max() * EXCHANGE_RATE) if not df.empty else 10000 
# Note: Slider logic is tricky with conversion. We'll filter based on raw KRW, but show THB to user?
# Easier: Filter strictly on data values (KRW). Display THB in UI only.
# But slider range should visually match.
# Let's keep slider raw (KRW) for now to avoid complexity in logic, or convert limits.
# To do it right: Slider returns THB, we convert back to KRW for filtering.
slider_min_val = int(df['price'].min() * EXCHANGE_RATE)
slider_max_val = int(df['price'].max() * EXCHANGE_RATE)
cost_range = st.sidebar.slider(T['price_range'], slider_min_val, slider_max_val, (slider_min_val, slider_max_val))

# Convert back to KRW for filtering
filter_min = cost_range[0] / EXCHANGE_RATE
filter_max = cost_range[1] / EXCHANGE_RATE

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
# Map 'out of stock', 'sold', etc to normalized status if needed
# Assuming sheet uses 'onsale' and 'out of stock' exactly.
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
    "최신순": "Newest", "Newest": "Newest",
    "가격 낮은순": "Price_Low", "Price: Low to High": "Price_Low",
    "가격 높은순": "Price_High", "Price: High to Low": "Price_High",
    "이름순": "Name", "Name": "Name"
}
current_sort = sort_map.get(sort_option, "Newest")

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
        
        # Opacity Style for Sold Items
        opacity_style = "opacity: 0.5;" if is_sold else ""
        
        # Container start
        st.markdown(f'<div style="{opacity_style}">', unsafe_allow_html=True)

        # Image
        img_url = get_image_url(row.get('image_file_id'))
        # Try fetching image bytes
        image_data = fetch_image_from_url(img_url)
        
        if image_data:
            st.image(image_data, use_container_width=True)
        else:
            if img_url:
                st.image(img_url, use_container_width=True)
            else:
                st.write(T['no_image'])
        
        # Sold Out Overlay (Text on top or just badge below?)
        # User requested: "이미지 위에 품절이라고 보여줘"
        # Since standard st.image doesn't support overlay easily without complex HTML/CSS or image processing,
        # we will add a visible badge immediately under/above or use a caption. 
        # For true overlay, we'd need PIL to draw on image or CSS hacking. 
        # Let's use a strong visual badge first. CSS hacking in Streamlit is brittle.
        # But wait, user asked "이미지 위에". I will try to use a negative margin text or just a big red header above it.
        if is_sold:
             st.markdown(f"<div style='background-color:rgba(0,0,0,0.7); color:white; padding:5px; text-align:center; font-weight:bold; margin-top:-30px; position:relative; z-index:100;'>SOLD OUT</div>", unsafe_allow_html=True)
  
        # Info
        brand = row.get('brand', 'Unknown')
        name = row.get('name', 'No Name')
        price_val = row.get('price', 0)
        
        # Currency Convert
        display_price = int(price_val * EXCHANGE_RATE)
        price_str = f"{T['currency_symbol']}{display_price:,}"
        
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
                # URL Encode ?? Line doesn't support pre-filled text in `ti/p/` usually, only `line.me/R/msg/text/?`
                # But user said "connecting address is 주소입력". I will just put the link.
                # NOTE: line.me/ti/p/ID is purely add friend. line.me/R/oaMessage/ID? is message.
                # I will use a placeholder variable.
                LINE_LINK_ID = "주소입력" # Placeholder requested by user
                
                # If it's a direct ID link (https://line.me/...) we use it. 
                # If user puts just ID, we frame it. 
                # "연결되는 주소는 '주소입력'야" -> I'll stick to href="주소입력"
                
                st.markdown(f"""
                <a href="{LINE_LINK_ID}" target="_blank" style="text-decoration:none;">
                    <button style="width:100%; background-color:#06C755; color:white; border:none; padding:10px; border-radius:5px; font-weight:bold; cursor:pointer;">
                        {T['line_btn']}
                    </button>
                </a>
                """, unsafe_allow_html=True)
            else:
                 st.button(T['sold_btn'], disabled=True, key=f"sold_{idx}")

        st.markdown("---")
