import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

st.set_page_config(page_title="CheckIn Room", layout="wide", initial_sidebar_state="collapsed")

# โหลดไฟล์ HTML ดั้งเดิมของคุณ
html_path = Path(__file__).parent.joinpath("CompanyEmloyeeCheckin.html")
if html_path.exists():
    html_content = html_path.read_text(encoding="utf-8")

    # แสดงผลหน้าเว็บผ่าน Streamlit components
    components.html(html_content, height=900, scrolling=True)
else:
    st.error("ไม่พบไฟล์ CompanyEmloyeeCheckin.html กรุณาตรวจสอบชื่อไฟล์")