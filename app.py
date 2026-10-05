import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
import json

st.set_page_config(page_title="CheckIn Room", layout="wide", initial_sidebar_state="collapsed")

DB_FILE = Path("db.json")

def load_db():
    if DB_FILE.exists():
        try:
            return json.loads(DB_FILE.read_text(encoding="utf-8"))
        except:
            pass
    return {"users": {}, "rooms": {}}

def save_db(data):
    DB_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

# โหลดข้อมูลกลางจากไฟล์
db = load_db()

# รับ-ส่งข้อมูลกับ HTML (ผ่าน Query Params หรือส่งเป็น JSON ไปให้หน้าเว็บ)
# เพื่อความชัวร์และง่ายที่สุด วางโครงสร้างนี้เพื่อให้ทุกเครื่องอ่านไฟล์เดียวกัน