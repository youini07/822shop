import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
import re

# --- Configuration ---
SERVICE_ACCOUNT_FILE = '../credentials.json'
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1qPfxy3ZF6ZISgPxRwNVYvHC9Qj57lgMeTd_FjN8cdF8/edit?gid=0#gid=0"
SHEET_NAME = "상품목록" # Attempt to find this, or use first sheet
START_ROW = 4
END_ROW = 459

# --- Category Logic ---
def classify_product(product_name):
    name = str(product_name).upper().replace(" ", "")
    
    # Priority: Specific -> General
    
def classify_product(product_name):
    name = str(product_name).upper().replace(" ", "")
    
    # Priority: Specific -> General
    
    # [Tops]
    if any(x in name for x in ['후드집업', 'ZIPUP', '집업']): return 'Zip-up Hoodie', 'Tops'
    if any(x in name for x in ['후드', 'HOOD', 'HOODIE']): return 'Hoodie', 'Tops'
    if any(x in name for x in ['맨투맨', 'MTM', 'SWEATSHIRT', '스웻']): return 'Sweatshirt', 'Tops'
    if any(x in name for x in ['니트', 'KNIT', 'SWEATER', '스웨터', '가디건', 'CARDIGAN']): return 'Knit/Sweater', 'Tops'
    if any(x in name for x in ['반팔', 'SHORT', 'TEE']): return 'T-Shirt (Short)', 'Tops'
    if any(x in name for x in ['긴팔', 'LONGSLEEVE', 'LONGTEE']): return 'T-Shirt (Long)', 'Tops'
    if any(x in name for x in ['셔츠', 'SHIRT', '남방', 'CHECK', 'STRIPE']): return 'Shirt', 'Tops'
    if any(x in name for x in ['카라', 'PK', 'POLO', '피케']): return 'Pique Shirt', 'Tops'
    if any(x in name for x in ['조끼', 'VEST', '베스트']): return 'Vest', 'Tops'
    if '티셔츠' in name or 'T-SHIRT' in name: return 'T-Shirt (Short)', 'Tops'
    
    # [Tops]
    # No change needed for Tops

    # [Outer] - Update output to 'Outerwear'
    if any(x in name for x in ['바람막이', 'WINDBREAKER', '윈드브레이커']): return 'Windbreaker', 'Outerwear'
    if any(x in name for x in ['패딩', 'PADDING', 'DOWN', 'PUFFER', '다운']): return 'Padding/Down', 'Outerwear'
    if any(x in name for x in ['코트', 'COAT', 'TRENCH']): return 'Coat', 'Outerwear'
    if any(x in name for x in ['플리스', 'FLEECE', '후리스', '뽀글이']): return 'Fleece', 'Outerwear'
    if any(x in name for x in ['가죽', 'LEATHER', '라이더']): return 'Leather', 'Outerwear'
    if any(x in name for x in ['자켓', 'JACKET', '점퍼', 'JUMPER', '블루종', 'BLOUSON']): return 'Jacket', 'Outerwear'
    
    # [Bottoms] - Update output to 'Bottoms'
    if any(x in name for x in ['반바지', 'SHORTS', '쇼츠']): return 'Shorts', 'Bottoms'
    if any(x in name for x in ['청바지', 'JEANS', 'DENIM', '데님']): return 'Denim/Jeans', 'Bottoms'
    if any(x in name for x in ['슬랙스', 'SLACKS']): return 'Slacks', 'Bottoms'
    if any(x in name for x in ['트레이닝', 'TRAINING', 'JOGGER', '조거', '츄리닝', 'SWEATPANTS']): return 'Sweatpants/Jogger', 'Bottoms'
    if any(x in name for x in ['면바지', 'CHINO', 'COTTON', '치노']): return 'Chino/Cotton', 'Bottoms'
    if any(x in name for x in ['치마', 'SKIRT', '스커트']): return 'Skirt', 'Bottoms'
    if any(x in name for x in ['바지', 'PANTS']): return 'Chino/Cotton', 'Bottoms' 
    
    # [Others]
    # No change needed for Others
 

    # [Others]
    if any(x in name for x in ['모자', 'CAP', 'HAT', 'BEANIE', '비니']): return 'Cap/Hat', 'Others'
    if any(x in name for x in ['가방', 'BAG', 'BACKPACK', '백팩']): return 'Bag', 'Others'
    if any(x in name for x in ['신발', 'SHOES', 'SNEAKERS']): return 'Shoes', 'Others'
    if any(x in name for x in ['원피스', 'DRESS', 'OPS']): return 'Dress', 'Others'
    if any(x in name for x in ['벨트', 'BELT', '넥타이', 'SCARF', 'ACC']): return 'Accessory', 'Others'
    
    return 'Etc', 'Others'

def main():
    print("🚀 Connecting to Google Sheets...")
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
    client = gspread.authorize(creds)
    
    try:
        sheet = client.open_by_url(SPREADSHEET_URL).sheet1
        print(f"✅ Sheet Open: {sheet.title}")
    except Exception as e:
        print(f"❌ Error opening sheet: {e}")
        return

    # Read G Column (Product Name)
    # Range G{START}:G{END}
    print(f"📖 Reading Product Names from G{START_ROW}:G{END_ROW}...")
    name_cells = sheet.range(f"G{START_ROW}:G{END_ROW}")
    product_names = [cell.value for cell in name_cells]
    
    updates = []
    
    print("🔄 Processing Categories...")
    for i, name in enumerate(product_names):
        code, upper = classify_product(name)
        row_num = START_ROW + i
        
        # We need to update E and F
        # E is Col 5, F is Col 6
        # Construct cells for batch update?
        # gspread.range can be used to set values? 
        # Easier: Create list of lists for update [[E, F], [E, F]...]
        # Then update range E{start}:F{end}
        
        updates.append([upper, code])
        # print(f"Row {row_num}: {name} -> [{upper}, {code}]")

    # Batch Update
    print(f"💾 Writing {len(updates)} rows to E{START_ROW}:F{END_ROW}...")
    
    # Update logic:
    # sheet.update(range_name, values)
    range_str = f"E{START_ROW}:F{END_ROW}"
    sheet.update(range_name=range_str, values=updates)
    
    print("✅ Update Complete!")

if __name__ == "__main__":
    main()
