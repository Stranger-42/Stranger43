import base64
from pathlib import Path
import streamlit as st

# 1. إعدادات الصفحة الأساسية
st.set_page_config(
    page_title="عقارات العقبة",
    page_icon="🏢",
    layout="centered"
)

# 2. تنسيق CSS للهوية الكحلية والذهبية ودعم RTL وتجاوب الموبايل
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Cairo', sans-serif !important;
    direction: rtl;
    overflow-x: hidden !important;
}

.stApp {
    background-color: #f8f6f0;
    overflow-x: hidden !important;
}

.block-container {
    padding-top: 3.2rem !important;
    padding-bottom: 2.5rem !important;
    padding-left: 0.75rem !important;
    padding-right: 0.75rem !important;
    max-width: 100% !important;
}

/* إبقاء الأعمدة متجاورة داخل عرض الشاشة */
div[data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    gap: 6px !important;
    width: 100% !important;
}

div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"],
div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
    flex: 1 1 0px !important;
    min-width: 0 !important;
}

/* بطاقة قسم مدمجة */
.category-card {
    background-color: #ffffff;
    border: 1.2px solid #d4af37;
    border-radius: 12px;
    padding: 8px 2px 6px 2px;
    text-align: center;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
    margin-bottom: 5px;
    height: 82px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

.category-icon {
    font-size: 20px;
    line-height: 1.1;
    margin-bottom: 4px;
}

.category-name {
    color: #0b2239 !important;
    font-size: 11px;
    font-weight: 700;
    line-height: 1.2;
    white-space: nowrap;
}

.gold-divider {
    height: 1.5px;
    width: 50%;
    background: linear-gradient(90deg, transparent, #d4af37, transparent);
    margin: 4px auto 0 auto;
}

/* أزرار التطبيق بالهوية الكحلية والذهبية */
div[data-testid="stButton"],
div.stButton > button {
    width: 100% !important;
}

div.stButton > button {
    background-color: #0b2239 !important;
    color: #f3d27a !important;
    border: 1px solid #d4af37 !important;
    border-radius: 8px !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    padding: 4px 6px !important;
    min-height: 30px !important;
    transition: 0.2s;
}

div.stButton > button:hover {
    background-color: #d4af37 !important;
    color: #0b2239 !important;
}

/* صندوق الفلاتر الرئيسي */
.filter-box {
    background: linear-gradient(135deg, #0b2239 0%, #143352 100%);
    border: 1.5px solid #d4af37;
    border-radius: 14px;
    padding: 12px;
    margin-top: 12px;
    margin-bottom: 14px;
    box-shadow: 0 4px 12px rgba(11, 34, 57, 0.12);
}

.filter-title {
    color: #f3d27a !important;
    font-size: 14px;
    font-weight: 800;
    margin-bottom: 8px;
}

/* تسميات حقول الإدخال داخل الفلاتر */
.filter-box label,
.filter-box .stMarkdown p {
    color: #ffffff !important;
    font-size: 12px !important;
    font-weight: 700 !important;
}

/* بطاقة عرض العقار */
.property-card {
    background-color: #ffffff;
    border-right: 4px solid #d4af37;
    border-top: 1px solid #e7dec0;
    border-bottom: 1px solid #e7dec0;
    border-left: 1px solid #e7dec0;
    border-radius: 12px;
    padding: 12px 14px;
    margin-bottom: 10px;
    box-shadow: 0 2px 8px rgba(11, 34, 57, 0.05);
}

.property-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 8px;
    margin-bottom: 6px;
}

.property-title {
    color: #0b2239 !important;
    font-size: 15px;
    font-weight: 800;
    margin: 0;
}

.property-price {
    background-color: #0b2239;
    color: #f3d27a !important;
    border: 1px solid #d4af37;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
    white-space: nowrap;
}

.property-meta {
    color: #4b5d6e !important;
    font-size: 12px;
    font-weight: 600;
    margin-bottom: 6px;
}

.property-desc {
    color: #222222 !important;
    font-size: 13px;
    line-height: 1.5;
    margin: 0;
}
</style>
""", unsafe_allow_html=True)

# 3. تهيئة الحالة في الجلسة
if "selected_category" not in st.session_state:
    st.session_state.selected_category = "الكل"

if "sample_listings" not in st.session_state:
    st.session_state.sample_listings = [
        {
            "title": "شقة تشطيب سوبر ديلوكس قرب الكورنيش",
            "category": "شقق للبيع",
            "area": "الكورنيش",
            "floor": 3,
            "price": 85000,
            "desc": "3 غرف نوم، صالة واسعة، إطلالة جميلة ومصعد حديث."
        },
        {
            "title": "شقة للإيجار مفروشة في المنطقة الخامسة",
            "category": "شقق للإيجار",
            "area": "المنطقة الخامسة",
            "floor": 2,
            "price": 450,
            "desc": "غرفتين وصالة، موقع هادئ وقريب من الخدمات."
        },
        {
            "title": "محل تجاري بواجهة مميزة على السوق",
            "category": "محلات تجارية للبيع",
            "area": "السوق",
            "floor": 0,
            "price": 120000,
            "desc": "مناسب لمعرض أو مكتب تجاري بحركة مرور عالية."
        },
        {
            "title": "محل للإيجار في البلد",
            "category": "محلات تجارية للإيجار",
            "area": "البلد",
            "floor": 0,
            "price": 600,
            "desc": "مساحة عملية وواجهة زجاجية جاهزة للاستلام."
        },
        {
            "title": "أرض سكنية منظمة في المنطقة الثامنه",
            "category": "أرض للبيع",
            "area": "المنطقة الثامنه",
            "floor": None,
            "price": 95000,
            "desc": "شارع معبد وجميع الخدمات متوفرة بالقرب من القطعة."
        },
        {
            "title": "شقة طابق أرضي بمدخل مستقل في صلاح الدين",
            "category": "شقق للبيع",
            "area": "صلاح الدين",
            "floor": 0,
            "price": 68000,
            "desc": "مناسبة للعائلات وكبار السن مع ترس صغير."
        },
    ]

# 4. تحميل وعرض صورة البانر
def load_image_base64(image_path: str) -> str | None:
    p = Path(image_path)
    if not p.exists():
        return None
    return base64.b64encode(p.read_bytes()).decode("utf-8")

img_b64 = load_image_base64("banner.jpg")

if img_b64:
    st.markdown(f"""
    <div style="
        border-radius: 14px;
        overflow: hidden;
        border: 2px solid #d4af37;
        box-shadow: 0 4px 12px rgba(11, 34, 57, 0.15);
        margin-bottom: 12px;
        width: 100%;
    ">
        <img src="data:image/jpeg;base64,{img_b64}"
             style="width: 100%; height: auto; display: block;"
             alt="عقارات العقبة" />
    </div>
    """, unsafe_allow_html=True)
else:
    st.warning("لم يتم العثور على banner.jpg في المجلد الرئيسي للمستودع.")

# 5. بيانات البطاقات الستة
categories = [
    {"id": "أرض للبيع", "icon": "🌱", "title": "أرض للبيع"},
    {"id": "شقق للبيع", "icon": "🏢", "title": "شقق للبيع"},
    {"id": "محلات تجارية للبيع", "icon": "🏪", "title": "محلات للبيع"},
    {"id": "إضافة إعلان", "icon": "📢", "title": "إضافة إعلان"},
    {"id": "شقق للإيجار", "icon": "🏘️", "title": "شقق للإيجار"},
    {"id": "محلات تجارية للإيجار", "icon": "🔑", "title": "محلات للإيجار"},
]

for row_start in range(0, len(categories), 3):
    cols = st.columns(3)
    for idx, col in enumerate(cols):
        item = categories[row_start + idx]
        with col:
            st.markdown(f"""
            <div class="category-card">
                <div class="category-icon">{item['icon']}</div>
                <div class="category-name">{item['title']}</div>
                <div class="gold-divider"></div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("اختيار ❮", key=f"btn_{item['id']}"):
                st.session_state.selected_category = item["id"]

# 6. قائمة مناطق العقبة
areas_list = [
    "الكل",
    "المنطقة الرابعة",
    "المنطقة الخامسة",
    "المنطقة السادسة",
    "المنطقة السابعة",
    "المنطقة الثامنه",
    "المنطقة التاسعة",
    "المنطقة العاشرة",
    "المنطقة الحادي عشر",
    "الكرامة",
    "ام ملقان الشمالية",
    "ام ملقان الغربية",
    "المركزية الشمالية",
    "المركزية الجنوبية",
    "منطقة قابوس",
    "المحدود",
    "العالمية",
    "الشرقيه",
    "الغربية",
    "الشاطيء",
    "البلد",
    "صلاح الدين",
    "السهل الشمالي",
    "المهندسين",
    "الكورنيش",
    "السوق",
]

# 7. شريط البحث والفلاتر
st.markdown('<div class="filter-box">', unsafe_allow_html=True)
st.markdown('<div class="filter-title">🔎 البحث وتصفية العقارات</div>', unsafe_allow_html=True)

search_query = st.text_input(
    "ابحث بكلمة مفتاحية",
    placeholder="مثال: إطلالة، أرضي، مفروشة، السوق..."
)

f_col1, f_col2 = st.columns(2)
with f_col1:
    selected_area = st.selectbox("المنطقة", areas_list, index=0)

with f_col2:
    floor_options = ["الكل", "أرضي (0)", "1", "2", "3", "4", "5+"]
    selected_floor = st.selectbox("رقم الطابق", floor_options, index=0)

p_col1, p_col2, p_col3 = st.columns(3)
with p_col1:
    min_price = st.number_input("السعر من (د.أ)", min_value=0, value=0, step=500)
with p_col2:
    max_price = st.number_input("السعر إلى (د.أ)", min_value=0, value=0, step=500)
with p_col3:
    sort_by = st.selectbox("الترتيب", ["الأحدث", "الأقل سعراً", "الأعلى سعراً"], index=0)

b_col1, b_col2 = st.columns(2)
with b_col1:
    if st.button("عرض جميع الأقسام"):
        st.session_state.selected_category = "الكل"
        st.rerun()
with b_col2:
    st.markdown(
        f"<div style='color:#f3d27a; font-size:12px; font-weight:700; padding-top:6px; text-align:center;'>"
        f"القسم: {st.session_state.selected_category}</div>",
        unsafe_allow_html=True
    )

st.markdown('</div>', unsafe_allow_html=True)

# 8. نموذج إضافة إعلان سريع عند اختيار "إضافة إعلان"
if st.session_state.selected_category == "إضافة إعلان":
    with st.expander("📢 إضافة إعلان عقاري جديد", expanded=True):
        with st.form("add_listing_form", clear_on_submit=True):
            new_title = st.text_input("عنوان الإعلان")
            new_cat = st.selectbox(
                "نوع القسم",
                ["أرض للبيع", "شقق للبيع", "محلات تجارية للبيع", "شقق للإيجار", "محلات تجارية للإيجار"]
            )
            new_area = st.selectbox("المنطقة", areas_list[1:])
            new_floor = st.number_input("رقم الطابق (0 للأرضي أو الأراضي)", min_value=0, max_value=30, value=0)
            new_price = st.number_input("السعر (د.أ)", min_value=1, value=50000, step=100)
            new_desc = st.text_area("تفاصيل العقار")
            submitted = st.form_submit_button("نشر الإعلان")
            if submitted and new_title.strip():
                st.session_state.sample_listings.insert(0, {
                    "title": new_title.strip(),
                    "category": new_cat,
                    "area": new_area,
                    "floor": None if new_cat == "أرض للبيع" else int(new_floor),
                    "price": int(new_price),
                    "desc": new_desc.strip() or "عقار مميز في العقبة."
                })
                st.session_state.selected_category = new_cat
                st.success("تمت إضافة الإعلان بنجاح!")
                st.rerun()

# 9. تطبيق التصفية والترتيب
active_cat = st.session_state.selected_category
filtered = []

for item in st.session_state.sample_listings:
    # تصفية القسم (إذا لم يكن الكل أو إضافة إعلان)
    if active_cat not in ("الكل", "إضافة إعلان") and item["category"] != active_cat:
        continue

    # تصفية المنطقة
    if selected_area != "الكل" and item["area"] != selected_area:
        continue

    # تصفية الطابق
    if selected_floor != "الكل":
        if item["floor"] is None:
            continue
        if selected_floor == "أرضي (0)" and item["floor"] != 0:
            continue
        elif selected_floor == "5+" and item["floor"] < 5:
            continue
        elif selected_floor not in ("أرضي (0)", "5+") and item["floor"] != int(selected_floor):
            continue

    # تصفية السعر (من - إلى)
    if min_price > 0 and item["price"] < min_price:
        continue
    if max_price > 0 and item["price"] > max_price:
        continue

    # تصفية البحث النصي
    q = search_query.strip().lower()
    if q:
        haystack = f"{item['title']} {item['desc']} {item['area']} {item['category']}".lower()
        if q not in haystack:
            continue

    filtered.append(item)

if sort_by == "الأقل سعراً":
    filtered.sort(key=lambda x: x["price"])
elif sort_by == "الأعلى سعراً":
    filtered.sort(key=lambda x: x["price"], reverse=True)

# 10. عرض النتائج
st.markdown(f"### 📋 النتائج ({len(filtered)})")

if not filtered:
    st.info("لا توجد عقارات مطابقة للفلاتر الحالية. جرّب تغيير المنطقة أو السعر أو الضغط على «عرض جميع الأقسام».")
else:
    for prop in filtered:
        floor_text = "أرض" if prop["floor"] is None else ("أرضي" if prop["floor"] == 0 else f"طابق {prop['floor']}")
        price_unit = "د.أ / شهر" if "للإيجار" in prop["category"] else "د.أ"
        st.markdown(f"""
        <div class="property-card">
            <div class="property-header">
                <h4 class="property-title">{prop['title']}</h4>
                <span class="property-price">{prop['price']:,} {price_unit}</span>
            </div>
            <div class="property-meta">
                🏷️ {prop['category']} &nbsp;|&nbsp; 📍 {prop['area']} &nbsp;|&nbsp; 🏢 {floor_text}
            </div>
            <p class="property-desc">{prop['desc']}</p>
        </div>
        """, unsafe_allow_html=True)
