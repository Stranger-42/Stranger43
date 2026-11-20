import sqlite3
from datetime import datetime
import streamlit as st

st.set_page_config(
    page_title="عقارات العقبة | مقارنة وقيمة سوقية",
    page_icon="🏢",
    layout="wide",
)

st.markdown(
    """
    <style>
        .main { direction: rtl; text-align: right; background-color: #FFFFFF; }
        div[data-testid="stSidebar"] { direction: rtl; text-align: right; background-color: #F4F7FA; }
        .stMarkdown, .stText, p, h1, h2, h3, h4, label { direction: rtl; text-align: right; }
        .hero-box {
            background: linear-gradient(135deg, #0F2942 0%, #163A5F 100%);
            color: #FFFFFF;
            padding: 20px 24px;
            border-radius: 12px;
            border-right: 6px solid #C59B27;
            margin-bottom: 18px;
        }
        .hero-sub {
            color: #F3D98B;
            font-size: 1.08rem;
            font-weight: 600;
            margin-top: 6px;
        }
        .land-card-banner {
            background-color: #0F2942;
            color: #FFFFFF;
            padding: 28px 16px;
            border-radius: 10px;
            text-align: center !important;
            border: 2px solid #C59B27;
            font-size: 1.25rem;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .price-below-table {
            font-size: 1.45rem;
            font-weight: 800;
            color: #0F2942;
            background-color: #FDF8E8;
            border: 1px solid #C59B27;
            padding: 12px 18px;
            border-radius: 8px;
            margin-top: 12px;
            margin-bottom: 14px;
        }
        .verified-badge {
            background-color: #1E7E5A;
            color: #FFFFFF;
            padding: 3px 10px;
            border-radius: 999px;
            font-size: 0.82rem;
            font-weight: bold;
            display: inline-block;
        }
        .unverified-badge {
            background-color: #E2E8F0;
            color: #334155;
            padding: 3px 10px;
            border-radius: 999px;
            font-size: 0.82rem;
            display: inline-block;
        }
        .office-card {
            background-color: #F8FAFC;
            border: 1px solid #CBD5E1;
            border-top: 4px solid #0F2942;
            border-radius: 10px;
            padding: 14px;
            margin-bottom: 12px;
        }
        .relay-box {
            background-color: #F4F7FA;
            border: 1px solid #CBD5E1;
            border-right: 5px solid #1E7E5A;
            border-radius: 10px;
            padding: 12px 14px;
            margin-bottom: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

DB_PATH = "aqaba_real_estate.db"
BASE_URL = "https://aqaba-estates.local"
PLATFORM_WHATSAPP = "رقم المنصة المركزي (الوسيط)"


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db_and_seed():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS agents_and_owners (
            agent_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            phone_whatsapp TEXT NOT NULL UNIQUE,
            agent_role TEXT NOT NULL DEFAULT 'office',
            is_verified INTEGER NOT NULL DEFAULT 0,
            is_featured_office INTEGER NOT NULL DEFAULT 0,
            commission_terms TEXT,
            license_number TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS properties (
            property_id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id INTEGER NOT NULL,
            listing_type TEXT NOT NULL,
            property_category TEXT NOT NULL,
            title TEXT NOT NULL,
            zone_area TEXT NOT NULL,
            street_address TEXT NOT NULL,
            hide_unit_number INTEGER NOT NULL DEFAULT 0,
            location_url TEXT,
            price_jod REAL NOT NULL,
            area_sqm REAL NOT NULL,
            floor_number TEXT,
            rooms_count INTEGER,
            bathrooms_count INTEGER,
            living_rooms_count INTEGER,
            view_description TEXT,
            image_url TEXT,
            is_featured_deal INTEGER NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'published',
            whatsapp_notified INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            FOREIGN KEY (agent_id) REFERENCES agents_and_owners(agent_id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS whatsapp_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_whatsapp TEXT NOT NULL,
            message_in TEXT NOT NULL,
            reply_out TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS lead_inquiries (
            inquiry_id INTEGER PRIMARY KEY AUTOINCREMENT,
            property_id INTEGER NOT NULL,
            agent_id INTEGER NOT NULL,
            referral_code TEXT NOT NULL,
            buyer_phone TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (property_id) REFERENCES properties(property_id),
            FOREIGN KEY (agent_id) REFERENCES agents_and_owners(agent_id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS relay_messages (
            relay_id INTEGER PRIMARY KEY AUTOINCREMENT,
            property_id INTEGER NOT NULL,
            referral_code TEXT NOT NULL,
            direction TEXT NOT NULL,
            sender_alias TEXT NOT NULL,
            recipient_alias TEXT NOT NULL,
            original_message TEXT NOT NULL,
            relayed_message TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (property_id) REFERENCES properties(property_id)
        )
    """)

    count = cur.execute("SELECT COUNT(*) AS cnt FROM properties").fetchone()["cnt"]
    if count == 0:
        agents = [
            ("أحمد الخطيب", "962790000001", "office", 1, 1, "عمولة متفق عليها + رعاية", "AQB-104"),
            ("مكتب البحر الأحمر للعقارات", "962790000002", "office", 1, 1, "عمولة إحالة موثقة 60 يوماً", "AQB-219"),
            ("سامر الطراونة", "962770000003", "broker", 0, 0, "عمولة حسب الصفقة", None),
            ("ليث المجالي", "962780000004", "owner", 0, 0, "بيع مباشر", None),
        ]
        cur.executemany(
            """
            INSERT INTO agents_and_owners
            (full_name, phone_whatsapp, agent_role, is_verified, is_featured_office, commission_terms, license_number)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            agents,
        )

        sample_props = [
            (
                1, "sale", "apartment", "شقة للبيع في المنطقة الخامسة - العقبة",
                "المنطقة الخامسة", "شارع الفاروق، عمارة 14، شقة 2", 0,
                "https://maps.google.com/?q=29.5321,35.0063", 120000, 150,
                "أرضي", 3, 3, 1, "إطلالة شارع وحديقة",
                "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800",
                1, "published", 1, "2026-11-20 15:10:00",
            ),
            (
                2, "sale", "land", "قطعة أرض للبيع",
                "المنطقة الثامنة", "شارع الجامعة، حوض 7، قطعة 42", 0,
                "https://maps.google.com/?q=29.5450,35.0120", 88000, 400,
                "غير منطبق", 0, 0, 0, "إطلالة مفتوحة على حي سكني",
                None, 1, "published", 1, "2026-11-20 14:40:00",
            ),
            (
                1, "rent_annual", "commercial", "محل تجاري للإيجار السنوي في الشلالة - العقبة",
                "الشلالة", "شارع الكورنيش الداخلي، مجمع النخيل، محل 3", 0,
                "https://maps.google.com/?q=29.5265,35.0015", 14000, 65,
                "أرضي", 1, 1, 0, "واجهة شارع حيوي",
                "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=800",
                0, "published", 1, "2026-11-20 13:20:00",
            ),
            (
                3, "rent_annual", "apartment", "شقة للإيجار السنوي في المنطقة السابعة - العقبة",
                "المنطقة السابعة", "شارع مكة، عمارة 9، شقة 8", 1,
                "https://maps.google.com/?q=29.5380,35.0095", 6500, 125,
                "الثاني", 2, 2, 1, "إطلالة شارع هادئ",
                "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800",
                0, "published", 1, "2026-11-20 11:50:00",
            ),
            (
                4, "sale", "apartment", "شقة للبيع في المنطقة التاسعة - العقبة",
                "المنطقة التاسعة", "شارع اليرموك، عمارة 21، شقة 11", 0,
                "https://maps.google.com/?q=29.5510,35.0180", 95000, 165,
                "الثالث", 3, 2, 1, "إطلالة بحرية جزئية",
                "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800",
                0, "published", 1, "2026-11-20 10:15:00",
            ),
        ]
        cur.executemany(
            """
            INSERT INTO properties (
                agent_id, listing_type, property_category, title, zone_area,
                street_address, hide_unit_number, location_url, price_jod, area_sqm,
                floor_number, rooms_count, bathrooms_count, living_rooms_count,
                view_description, image_url, is_featured_deal, status,
                whatsapp_notified, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            sample_props,
        )

    conn.commit()
    conn.close()


def format_address(row):
    addr = row["street_address"]
    if row["hide_unit_number"] == 1 and "شقة" in addr:
        parts = addr.split("شقة")
        return parts[0].strip().rstrip("،") + " (رقم الشقة يُزوّد عند التواصل)"
    return addr


def register_referral_inquiry(property_id: int, agent_id: int, buyer_phone: str = ""):
    conn = get_conn()
    cur = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ref_code = f"AQB-{property_id}-{datetime.now().strftime('%H%M%S')}"
    cur.execute(
        """
        INSERT INTO lead_inquiries (property_id, agent_id, referral_code, buyer_phone, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (property_id, agent_id, ref_code, buyer_phone.strip(), now_str),
    )
    conn.commit()
    conn.close()
    return ref_code


def relay_whatsapp_message(direction: str, property_id: int, real_party_phone: str, message_text: str):
    conn = get_conn()
    cur = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    prop = cur.execute("SELECT * FROM properties WHERE property_id = ?", (property_id,)).fetchone()
    if not prop:
        conn.close()
        return None, f"لم يتم العثور على عقار بالرقم #{property_id}."

    agent = cur.execute("SELECT * FROM agents_and_owners WHERE agent_id = ?", (prop["agent_id"],)).fetchone()
    ref_code = f"REF-{property_id}-{datetime.now().strftime('%M%S')}"

    if direction == "buyer_to_agent":
        sender_alias = "مشتري عبر المنصة (الرقم محجوب)"
        recipient_alias = f"المعلن ({agent['full_name']}) — عبر رقم المنصة"
        relayed_msg = (
            f"[{PLATFORM_WHATSAPP}] رسالة جديدة بخصوص العقار #{property_id} ({prop['title']}) | رمز المتابعة: {ref_code}:\n"
            f"\"{message_text.strip()}\"\n"
            f"(للرد: أرسل عبر رقم المنصة مرتبطاً بالرمز {ref_code})"
        )
    else:
        sender_alias = f"معلن العقار #{property_id} (الرقم محجوب)"
        recipient_alias = "المشتري المهتم — عبر رقم المنصة"
        relayed_msg = (
            f"[{PLATFORM_WHATSAPP}] رد بخصوص العقار #{property_id} | رمز المتابعة: {ref_code}:\n"
            f"\"{message_text.strip()}\"\n"
            f"(يتم تمرير الرسائل عبر المنصة لضمان المتابعة والخصوصية)"
        )

    cur.execute(
        """
        INSERT INTO relay_messages
        (property_id, referral_code, direction, sender_alias, recipient_alias, original_message, relayed_message, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (property_id, ref_code, direction, sender_alias, recipient_alias, message_text.strip(), relayed_msg, now_str),
    )
    conn.commit()
    conn.close()
    return ref_code, relayed_msg


def process_whatsapp_command(phone: str, message: str):
    conn = get_conn()
    cur = conn.cursor()
    msg = message.strip()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    agent = cur.execute(
        "SELECT * FROM agents_and_owners WHERE phone_whatsapp = ?", (phone.strip(),)
    ).fetchone()
    if not agent:
        cur.execute(
            "INSERT INTO agents_and_owners (full_name, phone_whatsapp, agent_role, is_verified, is_featured_office) VALUES (?, ?, 'broker', 0, 0)",
            (f"معلن ({phone.strip()})", phone.strip()),
        )
        conn.commit()
        agent = cur.execute(
            "SELECT * FROM agents_and_owners WHERE phone_whatsapp = ?", (phone.strip(),)
        ).fetchone()

    reply = ""

    if "تحديث سعر" in msg and "#" in msg:
        try:
            prop_id = int(msg.split("#")[1].split()[0])
            after_id = msg.split("#")[1].strip().split()
            new_price = float("".join(c for c in after_id[-1] if c.isdigit() or c == "."))
            prop = cur.execute("SELECT * FROM properties WHERE property_id = ?", (prop_id,)).fetchone()
            if not prop:
                reply = f"لم يتم العثور على إعلان بالرقم #{prop_id}."
            elif prop["agent_id"] != agent["agent_id"]:
                reply = f"عذراً، الإعلان #{prop_id} مسجل باسم معلن آخر."
            else:
                cur.execute(
                    "UPDATE properties SET price_jod = ?, whatsapp_notified = 1, created_at = ? WHERE property_id = ?",
                    (new_price, now_str, prop_id),
                )
                conn.commit()
                link = f"{BASE_URL}/property/{prop_id}"
                reply = (
                    f"تم تحديث سعر الإعلان #{prop_id} إلى {new_price:,.0f} دينار أردني بنجاح.\n"
                    f"رابط الإعلان المحدث: {link}"
                )
        except Exception:
            reply = "صيغة التحديث مثالها: تحديث سعر #1 إلى 115000"

    elif ("تم بيع" in msg or "تم تأجير" in msg) and "#" in msg:
        try:
            prop_id = int(msg.split("#")[1].split()[0])
            new_status = "sold" if "بيع" in msg else "rented"
            status_ar = "مباع" if new_status == "sold" else "مؤجر"
            prop = cur.execute("SELECT * FROM properties WHERE property_id = ?", (prop_id,)).fetchone()
            if not prop:
                reply = f"لم يتم العثور على إعلان بالرقم #{prop_id}."
            elif prop["agent_id"] != agent["agent_id"]:
                reply = f"عذراً، الإعلان #{prop_id} مسجل باسم معلن آخر."
            else:
                cur.execute(
                    "UPDATE properties SET status = ?, whatsapp_notified = 1 WHERE property_id = ?",
                    (new_status, prop_id),
                )
                conn.commit()
                link = f"{BASE_URL}/property/{prop_id}"
                reply = (
                    f"تم تحديث حالة الإعلان #{prop_id} إلى ({status_ar}).\n"
                    f"رابط الإعلان: {link}"
                )
        except Exception:
            reply = "صيغة تحديث الحالة مثالها: تم بيع #1"

    elif msg.startswith("إضافة"):
        parts = [p.strip() for p in msg.split("|")]
        if len(parts) < 7:
            reply = (
                "البيانات غير مكتملة. أرسل بالصيغة:\n"
                "إضافة | النوع (أرض/شقة/محل) | بيع أو إيجار | المنطقة | العنوان | المساحة | السعر | الطابق | الغرف | الحمامات | الصالونات | الإطلالة"
            )
        else:
            cat_ar = parts[1]
            cat_map = {
                "أرض": "land", "ارض": "land",
                "شقة": "apartment", "شقق": "apartment",
                "محل": "commercial", "محلات": "commercial",
            }
            prop_cat = cat_map.get(cat_ar, "apartment")
            deal_type = "rent_annual" if "إيجار" in parts[2] or "ايجار" in parts[2] else "sale"
            zone = parts[3]
            addr = parts[4]
            area = float("".join(c for c in parts[5] if c.isdigit() or c == "."))
            price = float("".join(c for c in parts[6] if c.isdigit() or c == "."))
            floor_val = parts[7] if len(parts) > 7 and parts[7] else ("غير منطبق" if prop_cat == "land" else "أرضي")
            rooms_val = int(parts[8]) if len(parts) > 8 and parts[8].isdigit() else (0 if prop_cat == "land" else 3)
            baths_val = int(parts[9]) if len(parts) > 9 and parts[9].isdigit() else (0 if prop_cat == "land" else 2)
            liv_val = int(parts[10]) if len(parts) > 10 and parts[10].isdigit() else (0 if prop_cat == "land" else 1)
            view_val = parts[11] if len(parts) > 11 and parts[11] else "إطلالة واضحة"

            if prop_cat == "land":
                title = "قطعة أرض للبيع" if deal_type == "sale" else "قطعة أرض للإيجار"
                img_url = None
            elif prop_cat == "commercial":
                title = f"محل تجاري {'للبيع' if deal_type == 'sale' else 'للإيجار'} في {zone} - العقبة"
                img_url = "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=800"
            else:
                title = f"شقة {'للبيع' if deal_type == 'sale' else 'للإيجار'} في {zone} - العقبة"
                img_url = "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800"

            cur.execute(
                """
                INSERT INTO properties (
                    agent_id, listing_type, property_category, title, zone_area,
                    street_address, hide_unit_number, location_url, price_jod, area_sqm,
                    floor_number, rooms_count, bathrooms_count, living_rooms_count,
                    view_description, image_url, is_featured_deal, status,
                    whatsapp_notified, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, 0, 'https://maps.google.com/?q=29.5321,35.0063', ?, ?, ?, ?, ?, ?, ?, ?, 0, 'published', 1, ?)
                """,
                (
                    agent["agent_id"], deal_type, prop_cat, title, zone,
                    addr, price, area, floor_val, rooms_val, baths_val, liv_val,
                    view_val, img_url, now_str,
                ),
            )
            conn.commit()
            new_id = cur.lastrowid
            link = f"{BASE_URL}/property/{new_id}"
            reply = (
                f"تم نشر إعلانك بنجاح برقم #{new_id}.\n"
                f"تم إرسال رابط الإعلان إلى رقم الواتساب ({phone.strip()}): {link}"
            )
    else:
        reply = (
            "أهلاً بك في منصة عقارات العقبة. يمكنك:\n"
            "1) إرسال إعلان جديد عبر الأمر: إضافة | شقة | بيع | المنطقة الخامسة | شارع كذا | 140 | 98000\n"
            "2) تحديث السعر: تحديث سعر #1 إلى 115000\n"
            "3) تحديث الحالة: تم بيع #1"
        )

    cur.execute(
        "INSERT INTO whatsapp_logs (phone_whatsapp, message_in, reply_out, created_at) VALUES (?, ?, ?, ?)",
        (phone.strip(), msg, reply, now_str),
    )
    conn.commit()
    conn.close()
    return reply


init_db_and_seed()

st.markdown(
    """
    <div class="hero-box">
        <h2 style="margin:0; color:#FFFFFF;">عقارات العقبة — منصة المقارنة، التفضيل، والقيمة السوقية</h2>
        <div class="hero-sub">
            موقعنا يوفر لك ما تحتاجه من معلومات لإيجاد أفضل خيار من خلال المقارنة والتفضيل والقيمة السوقية
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

top_tab = st.radio(
    "التبويب الرئيسي",
    [
        "الكل (أحدث 10 إعلانات)",
        "أراضي للبيع",
        "شقق للبيع والإيجار",
        "محلات تجارية للبيع والإيجار",
        "الصفقات المميزة",
    ],
    horizontal=True,
    label_visibility="collapsed",
)

search_col1, search_col2 = st.columns([3, 1])
with search_col1:
    search_query = st.text_input(
        "بحث شامل (المنطقة، العنوان، أو اسم المعلن)",
        placeholder="ابحث باسم المعلن (مثل: أحمد الخطيب) أو المنطقة أو نوع العقار...",
    )
with search_col2:
    sort_by = st.selectbox(
        "ترتيب حسب",
        [
            "التاريخ (الأحدث أولاً)",
            "السعر (من الأقل للأعلى)",
            "السعر (من الأعلى للأقل)",
            "المساحة (من الأصغر للأكبر)",
            "المساحة (من الأكبر للأصغر)",
            "اسم المعلن (أ - ي)",
        ],
    )

conn = get_conn()
rows = conn.execute(
    """
    SELECT p.*, a.full_name AS agent_name, a.phone_whatsapp, a.is_verified, a.agent_role
    FROM properties p
    JOIN agents_and_owners a ON p.agent_id = a.agent_id
    WHERE p.status = 'published'
    """
).fetchall()
all_props = [dict(r) for r in rows]

offices_rows = conn.execute(
    """
    SELECT * FROM agents_and_owners
    WHERE agent_role IN ('office', 'broker')
    ORDER BY is_featured_office DESC, is_verified DESC, agent_id ASC
    """
).fetchall()
offices_list = [dict(o) for o in offices_rows]

with st.sidebar:
    st.markdown("### 🎛️ فلاتر البحث والتفضيل")
    zones = ["الكل"] + sorted({p["zone_area"] for p in all_props})
    selected_zone = st.selectbox("المنطقة", zones)

    areas = [p["area_sqm"] for p in all_props] if all_props else [50.0, 500.0]
    min_area_val = float(min(areas))
    max_area_val = float(max(areas))
    if min_area_val == max_area_val:
        max_area_val = min_area_val + 100.0
    selected_area_range = st.slider(
        "المساحة (م²)",
        min_value=min_area_val,
        max_value=max_area_val,
        value=(min_area_val, max_area_val),
    )

    prices = [p["price_jod"] for p in all_props] if all_props else [1000.0, 200000.0]
    min_price_val = float(min(prices))
    max_price_val = float(max(prices))
    if min_price_val == max_price_val:
        max_price_val = min_price_val + 50000.0
    st.markdown("**السعر (من - إلى) بالدينار الأردني**")
    p_col1, p_col2 = st.columns(2)
    with p_col1:
        price_from = st.number_input("من", min_value=0.0, value=min_price_val, step=1000.0)
    with p_col2:
        price_to = st.number_input("إلى", min_value=0.0, value=max_price_val, step=1000.0)

    rooms_options = ["الكل", "0 (أرض)", "1", "2", "3", "4+"]
    selected_rooms = st.selectbox("عدد الغرف", rooms_options)

    floors_options = ["الكل"] + sorted({p["floor_number"] for p in all_props if p["floor_number"]})
    selected_floor = st.selectbox("الطابق", floors_options)

filtered = []
for p in all_props:
    if top_tab == "أراضي للبيع" and not (p["property_category"] == "land" and p["listing_type"] == "sale"):
        continue
    if top_tab == "شقق للبيع والإيجار" and p["property_category"] != "apartment":
        continue
    if top_tab == "محلات تجارية للبيع والإيجار" and p["property_category"] != "commercial":
        continue
    if top_tab == "الصفقات المميزة" and p["is_featured_deal"] != 1:
        continue

    if selected_zone != "الكل" and p["zone_area"] != selected_zone:
        continue

    if not (selected_area_range[0] <= p["area_sqm"] <= selected_area_range[1]):
        continue

    if not (price_from <= p["price_jod"] <= price_to):
        continue

    r_cnt = p["rooms_count"] or 0
    if selected_rooms == "0 (أرض)" and r_cnt != 0:
        continue
    elif selected_rooms in ["1", "2", "3"] and r_cnt != int(selected_rooms):
        continue
    elif selected_rooms == "4+" and r_cnt < 4:
        continue

    if selected_floor != "الكل" and p["floor_number"] != selected_floor:
        continue

    if search_query.strip():
        q = search_query.strip().lower()
        haystack = f"{p['title']} {p['zone_area']} {p['street_address']} {p['agent_name']}".lower()
        if q not in haystack:
            continue

    filtered.append(p)

if sort_by == "التاريخ (الأحدث أولاً)":
    filtered.sort(key=lambda x: x["created_at"], reverse=True)
elif sort_by == "السعر (من الأقل للأعلى)":
    filtered.sort(key=lambda x: x["price_jod"])
elif sort_by == "السعر (من الأعلى للأقل)":
    filtered.sort(key=lambda x: x["price_jod"], reverse=True)
elif sort_by == "المساحة (من الأصغر للأكبر)":
    filtered.sort(key=lambda x: x["area_sqm"])
elif sort_by == "المساحة (من الأكبر للأصغر)":
    filtered.sort(key=lambda x: x["area_sqm"], reverse=True)
elif sort_by == "اسم المعلن (أ - ي)":
    filtered.sort(key=lambda x: x["agent_name"])

latest_10 = filtered[:10]

st.markdown(f"### 📋 أحدث 10 إعلانات ({len(latest_10)} معروض من أصل {len(filtered)} مطابق)")

if not latest_10:
    st.info("لا توجد إعلانات مطابقة لخيارات البحث أو الفلترة الحالية.")
else:
    for prop in latest_10:
        price_per_m2 = prop["price_jod"] / prop["area_sqm"] if prop["area_sqm"] > 0 else 0
        zone_peers = [
            x["price_jod"] / x["area_sqm"]
            for x in all_props
            if x["zone_area"] == prop["zone_area"] and x["property_category"] == prop["property_category"] and x["area_sqm"] > 0
        ]
        avg_m2 = sum(zone_peers) / len(zone_peers) if zone_peers else price_per_m2

        with st.container(border=True):
            c_img, c_info = st.columns([1.25, 2.2])

            with c_img:
                if prop["property_category"] == "land":
                    st.markdown('<div class="land-card-banner">قطعة أرض للبيع</div>', unsafe_allow_html=True)
                else:
                    if prop["image_url"]:
                        st.image(prop["image_url"], use_container_width=True)
                    else:
                        st.markdown('<div class="land-card-banner">عقار في العقبة</div>', unsafe_allow_html=True)

            with c_info:
                badge_html = (
                    '<span class="verified-badge">✔ معلن معتمد</span>'
                    if prop["is_verified"] == 1
                    else '<span class="unverified-badge">معلن</span>'
                )
                featured_txt = " ⭐ صفقة مميزة" if prop["is_featured_deal"] == 1 else ""
                st.markdown(f"#### {prop['title']}{featured_txt}")
                st.markdown(
                    f"**المنطقة:** {prop['zone_area']} &nbsp;|&nbsp; "
                    f"**العنوان:** {format_address(prop)} &nbsp;|&nbsp; "
                    f"**المعلن:** {prop['agent_name']} {badge_html}",
                    unsafe_allow_html=True,
                )
                if prop["location_url"]:
                    st.markdown(f"📍 [رابط الموقع الجغرافي (اللوكيشن)]({prop['location_url']})")

                spec_rows = [
                    ("المساحة الإجمالية", f"{prop['area_sqm']:,.0f} م²"),
                    ("الطابق", prop["floor_number"] or "غير محدد"),
                    ("الإطلالة", prop["view_description"] or "غير محدد"),
                ]
                if prop["property_category"] != "land":
                    spec_rows.extend([
                        ("عدد الغرف", str(prop["rooms_count"] or 0)),
                        ("عدد الحمامات", str(prop["bathrooms_count"] or 0)),
                        ("عدد الصالونات", str(prop["living_rooms_count"] or 0)),
                    ])

                table_html = (
                    "<table style='width:100%; border-collapse:collapse; margin-top:8px; font-size:0.95rem;'>"
                )
                for idx, (lbl, val) in enumerate(spec_rows):
                    bg = "#F4F7FA" if idx % 2 == 0 else "#FFFFFF"
                    table_html += (
                        f"<tr style='background-color:{bg}; border-bottom:1px solid #E2E8F0;'>"
                        f"<td style='padding:7px 12px; font-weight:700; color:#0F2942; width:35%;'>{lbl}</td>"
                        f"<td style='padding:7px 12px; color:#1E293B;'>{val}</td>"
                        f"</tr>"
                    )
                table_html += "</table>"
                st.markdown(table_html, unsafe_allow_html=True)

                deal_label = "للبيع" if prop["listing_type"] == "sale" else "للإيجار"
                st.markdown(
                    f"<div class='price-below-table'>السعر ({deal_label}): {prop['price_jod']:,.0f} دينار أردني</div>",
                    unsafe_allow_html=True,
                )

                diff_pct = ((price_per_m2 - avg_m2) / avg_m2 * 100) if avg_m2 > 0 else 0
                if abs(diff_pct) < 5:
                    market_note = f"متوافق مع معدل السوق في {prop['zone_area']} (سعر المتر ~ {price_per_m2:,.0f} د.أ)"
                elif diff_pct < 0:
                    market_note = f"أقل من متوسط {prop['zone_area']} بحوالي {abs(diff_pct):.0f}% (سعر المتر ~ {price_per_m2:,.0f} د.أ)"
                else:
                    market_note = f"أعلى من متوسط {prop['zone_area']} بحوالي {diff_pct:.0f}% (سعر المتر ~ {price_per_m2:,.0f} د.أ)"

                st.caption(f"📊 القيمة السوقية والمقارنة: {market_note}")
                st.caption(f"🔗 رابط الإعلان: {BASE_URL}/property/{prop['property_id']} | التواصل يتم عبر المنصة كوسيط (الأرقام محجوبة)")

st.divider()

st.markdown("### 🛡️ الوساطة الذكية عبر الواتساب (إخفاء الأرقام ونحن في الوسط)")
st.write(
    "تستلم الأداة الرسالة من أحد الطرفين وتمررها للطرف الآخر عبر رقم المنصة بدون إظهار أرقام هواتف المشتري أو المعلن لبعضهما."
)

relay_c1, relay_c2 = st.columns([1.25, 1.75])
prop_choices = {f"#{p['property_id']} — {p['title']} ({p['zone_area']})": p["property_id"] for p in all_props}

with relay_c1:
    relay_dir = st.radio(
        "اتجاه الرسالة عبر الواتساب",
        [
            "من المشتري → إلى المعلن (عبر رقم المنصة، رقم المشتري محجوب)",
            "من المعلن → إلى المشتري (عبر رقم المنصة، رقم المعلن محجوب)",
        ],
    )
    selected_prop_label = st.selectbox("اختر العقار المعني", list(prop_choices.keys())) if prop_choices else None
    sender_real_phone = st.text_input(
        "رقم المرسل الفعلي (يُحفظ سرياً ولا يظهر للطرف الآخر)",
        value="962795551122" if relay_dir.startswith("من المشتري") else "962790000001",
    )
    relay_msg_input = st.text_area(
        "نص الرسالة المرسلة للواتساب",
        value="هل العقار متاح وهل السعر قابل للتفاوض؟ أرغب بترتيب معاينة.",
        height=85,
    )
    if st.button("تمرير الرسالة عبر المنصة (الوسيط)", type="primary"):
        if selected_prop_label:
            pid = prop_choices[selected_prop_label]
            d_code = "buyer_to_agent" if relay_dir.startswith("من المشتري") else "agent_to_buyer"
            ref_c, out_msg = relay_whatsapp_message(d_code, pid, sender_real_phone, relay_msg_input)
            if ref_c:
                st.success(f"تم تمرير الرسالة بنجاح بدون كشف الأرقام (رمز المتابعة: {ref_c}).")
                st.code(out_msg, language="text")
                st.rerun()
            else:
                st.error(out_msg)

with relay_c2:
    st.markdown("**سجل الرسائل الممرّرة عبر المنصة (الأرقام محجوبة بين الطرفين):**")
    r_logs = conn.execute("SELECT * FROM relay_messages ORDER BY relay_id DESC LIMIT 6").fetchall()
    if not r_logs:
        st.info("لم يتم تمرير رسائل وسيطة بعد.")
    else:
        for rl in r_logs:
            st.markdown(
                f"""
                <div class="relay-box">
                    <div style="font-weight:800; color:#0F2942;">العقار #{rl['property_id']} | الرمز: {rl['referral_code']} | {rl['created_at']}</div>
                    <div style="font-size:0.9rem; color:#1E7E5A; margin:4px 0;"><b>المرسل الظاهر:</b> {rl['sender_alias']} ⬅ <b>المستقبل:</b> {rl['recipient_alias']}</div>
                    <div style="color:#1E293B;"><b>الرسالة الممرّرة:</b> {rl['original_message']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

st.divider()

st.markdown("### 🏢 مكاتب عقارية في العقبة")
office_cols = st.columns(2)
for idx, off in enumerate(offices_list):
    with office_cols[idx % 2]:
        v_badge = "✔ مكتب معتمد" if off["is_verified"] == 1 else "جهة عقارية"
        f_tag = " ⭐ مساحة مميزة" if off["is_featured_office"] == 1 else ""
        st.markdown(
            f"""
            <div class="office-card">
                <div style="font-size:1.1rem; font-weight:800; color:#0F2942;">{off['full_name']}{f_tag}</div>
                <div style="margin:6px 0; color:#1E7E5A; font-weight:700;">📞 عبر رقم المنصة الوسيط: {off['phone_whatsapp']}</div>
                <div style="font-size:0.88rem; color:#475569;">الحالة: {v_badge} &nbsp;|&nbsp; آلية التعاون: {off['commission_terms'] or 'اتفاق مباشر'}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.divider()

st.markdown("### 📱 التحديث والإضافة المباشرة عبر الواتساب وإرسال رابط الإعلان")
wa_col1, wa_col2 = st.columns([1.2, 1.8])
with wa_col1:
    wa_phone = st.text_input("رقم واتساب المعلن", value="962790000001")
    quick_preset = st.selectbox(
        "أمثلة أوامر سريعة للتجربة",
        [
            "تحديث سعر #1 إلى 115000",
            "تم بيع #2",
            "إضافة | شقة | بيع | المنطقة الخامسة | شارع الفاروق، عمارة 8، شقة 1 | 145 | 108000 | الأول | 3 | 2 | 1 | إطلالة حديقة",
        ],
    )
    wa_message = st.text_area("نص رسالة الواتساب", value=quick_preset, height=90)
    if st.button("إرسال ومعالجة عبر الواتساب", type="primary"):
        reply_text = process_whatsapp_command(wa_phone, wa_message)
        st.success("تم تنفيذ الأمر وتجهيز الرد والرابط لإرساله على الواتساب:")
        st.code(reply_text, language="text")
        st.rerun()

with wa_col2:
    st.markdown("**سجل رسائل الواتساب والروابط المرسلة للمُرسلين:**")
    logs = conn.execute("SELECT * FROM whatsapp_logs ORDER BY log_id DESC LIMIT 5").fetchall()
    if not logs:
        st.info("لم يتم تنفيذ أوامر واتساب جديدة بعد.")
    else:
        for lg in logs:
            st.markdown(f"- **من ({lg['phone_whatsapp']}):** `{lg['message_in']}`")
            st.markdown(f"  ↳ **رد البوت والرابط المرسل:** {lg['reply_out'].replace(chr(10), ' | ')}")

conn.close()
