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

# --- Header ---
st.title("🛍️ Vintage Collection")
st.markdown("엄선된 구제 의류를 만나보세요.")

if df.empty:
    st.warning("등록된 상품이 없습니다. 구글 시트를 확인해주세요.")
    st.stop()

# --- Sidebar Filters ---
st.sidebar.header("🔍 필터")

# 1. Search
search_query = st.sidebar.text_input("상품명 검색", placeholder="예: 나이키 자켓")

# 2. Brand Filter
all_brands = sorted([str(x) for x in df['brand'].unique()]) if 'brand' in df.columns else []
selected_brands = st.sidebar.multiselect("브랜드", all_brands)

# 3. Category Filter
all_categories = sorted([str(x) for x in df['category'].unique()]) if 'category' in df.columns else []
selected_categories = st.sidebar.multiselect("카테고리", all_categories)

# 4. Size Filter
all_sizes = sorted([str(x) for x in df['size'].unique()]) if 'size' in df.columns else []
selected_sizes = st.sidebar.multiselect("사이즈", all_sizes)

# 5. Price Range
min_price = int(df['price'].min()) if not df.empty else 0
max_price = int(df['price'].max()) if not df.empty else 100000
price_range = st.sidebar.slider("가격 범위", min_price, max_price, (min_price, max_price))

# 6. Status Filter
show_sold_out = st.sidebar.checkbox("품절된 상품도 보기", value=False)

# 7. Debug Mode
debug_mode = st.sidebar.checkbox("🛠️ 디버그 모드 (안 될 때 켜보세요)", value=False)

# --- Sort Options ---
sort_option = st.selectbox("정렬 기준", ["최신순", "가격 낮은순", "가격 높은순", "이름순"])

# --- App Logic: Filtering ---
filtered_df = df.copy()

if debug_mode:
    st.warning("🛠️ 디버그 모드 활성화됨")
    st.write("### 📊 데이터 미리보기 (상위 5개)")
    st.dataframe(filtered_df[['name', 'image_file_id', 'brand']].head())

# Filter: Status
if not show_sold_out and 'status' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['status'] != 'SOLD']

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
filtered_df = filtered_df[(filtered_df['price'] >= price_range[0]) & (filtered_df['price'] <= price_range[1])]

# --- App Logic: Sorting ---
if sort_option == "최신순":
    if 'updated_at' in filtered_df.columns:
        filtered_df['updated_at'] = pd.to_datetime(filtered_df['updated_at'], errors='coerce')
        filtered_df = filtered_df.sort_values(by='updated_at', ascending=False)
elif sort_option == "가격 낮은순":
    filtered_df = filtered_df.sort_values(by='price', ascending=True)
elif sort_option == "가격 높은순":
    filtered_df = filtered_df.sort_values(by='price', ascending=False)
elif sort_option == "이름순":
    filtered_df = filtered_df.sort_values(by='name', ascending=True)

# --- App Logic: Pagination ---
items_per_page = 12
total_items = len(filtered_df)
total_pages = max(1, (total_items - 1) // items_per_page + 1)

if total_pages > 1:
    st.sidebar.markdown("---")
    st.sidebar.subheader("📄 페이지 이동")
    page = st.sidebar.number_input("현재 페이지", min_value=1, max_value=total_pages, value=1)
    st.sidebar.caption(f"총 {total_pages} 페이지 중 {page} 페이지")
else:
    page = 1

# Slice Data for current page
start_idx = (page - 1) * items_per_page
end_idx = start_idx + items_per_page
page_items = filtered_df.iloc[start_idx:end_idx]

# --- Display Grid ---
st.divider()
st.subheader(f"총 {total_items}개의 상품 중 {len(page_items)}개를 보여줍니다. ({page}/{total_pages} 페이지)")

# Responsive Grid
cols = st.columns(3) 

for idx, row in page_items.iterrows():
    col = cols[idx % 3]
    
    with col:
        # Status Badge
        is_sold = row.get('status') == 'SOLD'
        status_text = "🚫 품절" if is_sold else "✅ 판매중"
        
        # Image
        img_url = get_image_url(row.get('image_file_id'))
        
        # Try fetching image bytes (Server-side proxy)
        image_data = fetch_image_from_url(img_url)
        
        if image_data:
            st.image(image_data, use_container_width=True)
            if debug_mode:
                st.caption(f"🆔 {row.get('image_file_id')}")
        else:
             # Fallback to URL if bytes fetch fails (or display placeholder)
            if img_url:
                st.image(img_url, use_container_width=True) # Try client-side fallback
            else:
                st.write("📷 이미지 없음")
            
        # Info
        brand = row.get('brand', 'Unknown')
        name = row.get('name', 'No Name')
        price = row.get('price', 0)
        size = row.get('size', '-')
        condition = row.get('condition', '-')
        
        # Title & Price
        st.markdown(f"<div class='product-title'>[{brand}] {name}</div>", unsafe_allow_html=True)
        if is_sold:
            st.markdown(f"<span class='sold-out'>{price:,}원</span> <span class='sold-out-badge'>SOLDOUT</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='product-price'>{price:,}원</div>", unsafe_allow_html=True)
            
        # Meta Info
        st.caption(f"사이즈: {size} | 상태: {condition}")
        
        # Detail Expander
        with st.expander("상세 정보 및 구매"):
            st.write(f"**제품 설명**")
            st.write(row.get('description', '설명 없음'))
            st.write(f"---")
            st.write(f"📅 등록일: {row.get('updated_at', '-')}")
            
            if not is_sold:
                # Contact Links
                # Replace with actual contact info in production
                contact_msg = f"안녕하세요, [{brand}] {name} ({price:,}원) 구매하고 싶습니다."
                st.markdown(f"""
                <a href="kakaoopen://join?l=..." target="_blank" style="text-decoration:none;">
                    <button style="width:100%; background-color:#FAE100; color:#3C1E1E; border:none; padding:10px; border-radius:5px; font-weight:bold; cursor:pointer;">
                        🟡 카카오톡으로 구매 문의
                    </button>
                </a>
                <br><br>
                <a href="tel:010-0000-0000" style="text-decoration:none;">
                    <button style="width:100%; background-color:#f1f3f5; color:black; border:1px solid #ccc; padding:10px; border-radius:5px; font-weight:bold; cursor:pointer;">
                        📞 전화로 문의하기
                    </button>
                </a>
                """, unsafe_allow_html=True)
            else:
                 st.button("🚫 품절된 상품입니다", disabled=True, key=f"sold_{idx}")

        st.markdown("---")
