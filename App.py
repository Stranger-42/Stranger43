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
    text-align: right;
}

/* خلفية التطبيق العامة */
.stApp {
    background-color: #f8f6f0;
}

/* تصميم الهيدر العلوي */
.aqaba-header {
    background: linear-gradient(135deg, #0b2239 0%, #163a5f 100%);
    padding: 28px 20px;
    border-radius: 18px;
    border-bottom: 4px solid #d4af37;
    text-align: center;
    box-shadow: 0 6px 18px rgba(11, 34, 57, 0.15);
    margin-bottom: 24px;
}

.aqaba-tagline {
    color: #e6c667;
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 4px;
}

.aqaba-title {
    color: #ffffff;
    font-size: 34px;
    font-weight: 800;
    margin: 0;
    letter-spacing: 0.5px;
}

.aqaba-subtitle {
    display: inline-block;
    background-color: #091a2c;
    color: #f3d27a;
    border: 1px solid #d4af37;
    padding: 6px 22px;
    border-radius: 50px;
    font-size: 15px;
    font-weight: 600;
    margin-top: 10px;
}

/* تصميم بطاقات الأقسام */
.category-card {
    background-color: #ffffff;
    border: 1.5px solid #d4af37;
    border-radius: 16px;
    padding: 18px 10px 12px 10px;
    text-align: center;
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.04);
    margin-bottom: 6px;
}

.category-icon {
    font-size: 34px;
    margin-bottom: 6px;
}

.category-name {
    color: #0b2239;
    font-size: 16px;
    font-weight: 700;
    margin-bottom: 6px;
}

.gold-divider {
    height: 2px;
    width: 55%;
    background: linear-gradient(90deg, transparent, #d4af37, transparent);
    margin: 6px auto 0 auto;
}

/* تخصيص أزرار الاختيار أسفل كل بطاقة */
div.stButton > button {
    width: 100%;
    background-color: #0b2239;
    color: #f3d27a;
    border: 1px solid #d4af37;
    border-radius: 10px;
    font-weight: 700;
    padding: 6px 0;
    transition: 0.2s;
}

div.stButton > button:hover {
    background-color: #d4af37;
    color: #0b2239;
    border-color: #0b2239;
}
</style>
""", unsafe_allow_html=True)

# 3. حفظ القسم المختار في الذاكرة المؤقتة
if "selected_category" not in st.session_state:
    st.session_state.selected_category = "الكل"

# 4. عرض الهيدر العلوي
st.markdown("""
<div class="aqaba-header">
    <div class="aqaba-tagline">إبحث .. إكتشف .. إمتلك</div>
    <h1 class="aqaba-title">🏛️ عقارات العقبة</h1>
    <div class="aqaba-subtitle">لخدمات وبيع العقارات</div>
</div>
""", unsafe_allow_html=True)

# 5. بيانات البطاقات الستة (نفس ترتيب الصورة)
categories = [
    {"id": "أرض للبيع", "icon": "🌱", "title": "أرض للبيع"},
    {"id": "شقق للبيع", "icon": "🏢", "title": "شقق للبيع"},
    {"id": "محلات تجارية للبيع", "icon": "🏪", "title": "محلات تجارية للبيع"},
    {"id": "إضافة إعلان", "icon": "📢", "title": "إضافة إعلان"},
    {"id": "شقق للإيجار", "icon": "🏘️", "title": "شقق للإيجار"},
    {"id": "محلات تجارية للإيجار", "icon": "🔑", "title": "محلات تجارية للإيجار"},
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
