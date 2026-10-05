import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
import json

st.set_page_config(page_title="CheckIn Room", layout="wide", initial_sidebar_state="collapsed")

# 1. สร้างฐานข้อมูลกลางบนเซิร์ฟเวอร์ Streamlit
if "global_db" not in st.session_state:
    st.session_state.global_db = {
        "users": {},
        "rooms": {}
    }

# ดึงข้อมูลมาแปลงเป็น JSON เพื่อส่งให้ HTML ของคุณอ่านและเขียนร่วมกัน
db_json = json.dumps(st.session_state.global_db, ensure_ascii=False)

# 2. โหลดไฟล์ HTML ดั้งเดิมของคุณ
html_path = Path(__file__).parent.joinpath("CompanyEmloyeeCheckin.html")
if html_path.exists():
    html_content = html_path.read_text(encoding="utf-8")

    # แทรกข้อมูลกลางลงไปใน HTML เพื่อให้ JavaScript ในหน้าเว็บซิงก์กันผ่าน Streamlit
    bridge_script = f"""
    <script>
        // บังคับใช้ฐานข้อมูลกลางจาก Streamlit
        window.SHARED_DB = {db_json};
    </script>
    """

    # รวมโค้ดบริดจ์กับ HTML เดิม
    full_html = html_content.replace("<head>", f"<head>{bridge_script}")

    components.html(full_html, height=900, scrolling=True)
else:
    st.error("ไม่พบไฟล์ CompanyEmloyeeCheckin.html กรุณาตรวจสอบชื่อไฟล์")