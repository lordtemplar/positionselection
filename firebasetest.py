import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import pandas as pd

# ตรวจสอบว่ามี Secret ที่จำเป็นครบถ้วน
try:
    # ตรวจสอบว่ามีการเรียกใช้ Firebase app แล้วหรือยัง
    if not firebase_admin._apps:
        # โหลด Credential จาก Secrets
        firebase_config = {
            "type": st.secrets["firebase"]["type"],
            "project_id": st.secrets["firebase"]["project_id"],
            "private_key_id": st.secrets["firebase"]["private_key_id"],
            "private_key": st.secrets["firebase"]["private_key"].replace('\\n', '\n'),
            "client_email": st.secrets["firebase"]["client_email"],
            "client_id": st.secrets["firebase"]["client_id"],
            "auth_uri": st.secrets["firebase"]["auth_uri"],
            "token_uri": st.secrets["firebase"]["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["firebase"]["auth_provider_x509_cert_url"],
            "client_x509_cert_url": st.secrets["firebase"]["client_x509_cert_url"],
            "universe_domain": st.secrets["firebase"]["universe_domain"]
        }

        # ใช้ Credential ที่ถูกต้องในการเชื่อมต่อ
        cred = credentials.Certificate(firebase_config)
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://positionchoosing-default-rtdb.asia-southeast1.firebasedatabase.app/'
        })

except ValueError as e:
    st.error(f"Firebase initialization error: {e}")
    st.stop()
except Exception as e:
    st.error(f"Unexpected error: {e}")
    st.stop()

# ฟังก์ชันการอ่านข้อมูลจาก Firebase
def get_data(path='/'):
    ref = db.reference(path)  # เส้นทางไปยังตำแหน่งข้อมูล
    data = ref.get()
    return data

# ดึงข้อมูลจาก Firebase
data = get_data('/')

# ตรวจสอบว่ามีข้อมูลหรือไม่
if data:
    # ตรวจสอบว่าข้อมูลเป็น dictionary หรือไม่
    if isinstance(data, dict):
        # สร้าง DataFrame จากข้อมูล
        df = pd.DataFrame.from_dict(data, orient='index')
    else:
        st.write("Data from Firebase is not in the expected dictionary format.")
        st.stop()

    # กรองค่า NaN และค่าไม่ใช่ตัวเลขในคอลัมน์ PositionID
    df['PositionID'] = pd.to_numeric(df['PositionID'], errors='coerce').fillna(0).astype(int).apply(lambda x: f"{x:03d}")

    # เรียงลำดับคอลัมน์ตามที่ต้องการ
    df = df[["PositionID", "PositionName", "Unit", "Specialist", "Branch", "Rank", "Other", "Status"]]

    # ฟังก์ชันการเปลี่ยนสีพื้นหลังทั้งแถวตามเงื่อนไข
    def highlight_status(row):
        color = 'green' if row['Status'] == 'ว่าง' else 'darkred'
        return ['background-color: {}'.format(color)] * len(row)

    # ใช้ Styler เพื่อเปลี่ยนสีพื้นหลังทั้งแถว
    styled_df = df.style.apply(highlight_status, axis=1)

    # แสดงผลข้อมูลในรูปแบบตารางที่สามารถขยายขนาดได้และซ่อน column แรกที่เป็น index
    st.write("Data from Firebase:")
    st.dataframe(styled_df, use_container_width=True, hide_index=True)
else:
    st.write("No data found in Firebase.")
