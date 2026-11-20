import base64
from pathlib import Path
import streamlit as st

# 1. إعدادات الصفحة الأساسية
st.set_page_config(
    page_title="عقارات العقبة",
    page_icon="🏢",
    layout="centered"
)

# 2. تنسيق CSS للهوية الكحلية والذهبية ودعم اللغة العربية (RTL)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Cairo', sans-serif !important;
    direction: rtl;
}

.stApp {
    background-color: #f8f6f0;
}

.block-container {
    padding-top: 1.2rem !important;
    padding-bottom: 2rem !important;
    max-width: 720px !important;
}

/* إبقاء 3 أعمدة متجاورة حتى على شاشة الجوال */
div[data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    gap: 8px !important;
}

div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
    flex: 1 1 0% !important;
    min-width: 0 !important;
    width: auto !important;
}

/* بطاقة قسم مدمجة */
.category-card {
    background-color: #ffffff;
    border: 1.2px solid #d4af37;
    border-radius: 12px;
    padding: 10px 4px 8px 4px;
    text-align: center;
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.04);
    margin-bottom: 6px;
    min-height: 92px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

.category-icon {
    font-size: 22px;
    line-height: 1.2;
    margin-bottom: 4px;
}

.category-name {
    color: #0b2239 !important;
    font-size: 11.5px;
    font-weight: 700;
    line-height: 1.25;
}

.gold-divider {
    height: 2px;
    width: 55%;
    background: linear-gradient(90deg, transparent, #d4af37, transparent);
    margin: 5px auto 0 auto;
}

/* زر اختيار واضح وممتد */
div.stButton > button {
    width: 100% !important;
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
    border-color: #0b2239 !important;
}
</style>
""", unsafe_allow_html=True)

# 3. حفظ القسم المختار في الذاكرة المؤقتة
if "selected_category" not in st.session_state:
    st.session_state.selected_category = "الكل"

# 4. تحميل وعرض صورة البانر من المستودع
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
        box-shadow: 0 4px 14px rgba(11, 34, 57, 0.15);
        margin-bottom: 14px;
    ">
        <img src="data:image/jpeg;base64,{img_b64}"
             style="width: 100%; height: auto; display: block;"
             alt="عقارات العقبة" />
    </div>
    """, unsafe_allow_html=True)
else:
    st.warning("لم يتم العثور على banner.jpg في المجلد الرئيسي للمستودع.")

# 5. بيانات البطاقات الستة (نفس ترتيب الصورة)
categories = [
    {"id": "أرض للبيع", "icon": "🌱", "title": "أرض للبيع"},
    {"id": "شقق للبيع", "icon": "🏢", "title": "شقق للبيع"},
    {"id": "محلات تجارية للبيع", "icon": "🏪", "title": "محلات للبيع"},
    {"id": "إضافة إعلان", "icon": "📢", "title": "إضافة إعلان"},
    {"id": "شقق للإيجار", "icon": "🏘️", "title": "شقق للإيجار"},
    {"id": "محلات تجارية للإيجار", "icon": "🔑", "title": "محلات للإيجار"},
]

# 6. رسم الشبكة (صفين × 3 أعمدة)
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

# 7. شريط تأكيد يوضح القسم النشط حالياً
st.markdown("---")
st.info(f"📌 القسم المختار حالياً: **{st.session_state.selected_category}**")
