import streamlit as st
import random
import string
from datetime import datetime

st.set_page_config(page_title="CheckIn Room – เช็คอินพนักงาน", layout="wide", initial_sidebar_state="collapsed")

# --- GLOBAL SHARED DATABASE (แชร์ข้อมูลข้ามเครื่องบนเซิร์ฟเวอร์เดียวกัน) ---
if "global_db" not in st.session_state:
    st.session_state.global_db = {
        "users": {},  # email -> {name, email}
        "rooms": {}  # code -> room_data
    }

db = st.session_state.global_db

# จัดการ Session ส่วนตัวของผู้ใช้คนนั้นๆ
if "me" not in st.session_state:
    st.session_state.me = None
if "current_room" not in st.session_state:
    st.session_state.current_room = None
if "tab" not in st.session_state:
    st.session_state.tab = "home"


def gen_code():
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    while True:
        code = "".join(random.choices(chars, k=6))
        if code not in db["rooms"]:
            return code


def today_key():
    return datetime.now().strftime("%Y-%m-%d")


# --- 1. หน้า Login ---
if not st.session_state.me:
    st.title("CheckIn Room")
    st.write("เช็คอินเข้างานตามพื้นที่ที่กำหนด")

    with st.form("login_form"):
        name_input = st.text_input("ชื่อของคุณ")
        email_input = st.text_input("อีเมล (เช่น you@gmail.com)").strip().lower()
        submitted = st.form_submit_button("เข้าสู่ระบบ")
        if submitted:
            if name_input and "@" in email_input:
                db["users"][email_input] = {"name": name_input, "email": email_input}
                st.session_state.me = email_input
                st.rerun()
            else:
                st.error("กรุณากรอกชื่อและอีเมลให้ถูกต้อง")
    st.stop()

me = st.session_state.me
user_info = db["users"].get(me, {"name": me})

# --- 2. หน้า Lobby (เลือกห้อง / สร้างห้อง) ---
if not st.session_state.current_room:
    st.subheader(f"สวัสดี, {user_info['name']} ({me})")
    if st.button("ออกจากระบบ"):
        st.session_state.me = None
        st.rerun()

    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### เข้าร่วมห้อง")
        join_code = st.text_input("รหัสห้อง 6 หลัก", max_chars=6).upper()
        if st.button("เข้าร่วม"):
            if join_code in db["rooms"]:
                room = db["rooms"][join_code]
                if me not in room["members"]:
                    room["members"].append(me)
                    room["joined"][me] = today_key()
                st.session_state.current_room = join_code
                st.rerun()
            else:
                st.error("ไม่พบรหัสห้องนี้")

        st.markdown("### ห้องที่คุณอยู่")
        my_rooms = [r for r in db["rooms"].values() if me in r["members"]]
        if my_rooms:
            for r in my_rooms:
                host_label = " (Host)" if r["host"] == me else ""
                if st.button(f"{r['name']} ({r['code']}){host_label}", key=f"room_{r['code']}"):
                    st.session_state.current_room = r["code"]
                    st.rerun()
        else:
            st.info("ยังไม่มีห้องที่เข้าร่วม")

    with col2:
        st.markdown("### สร้างห้องบริษัท")
        with st.form("create_room_form"):
            r_name = st.text_input("ชื่อบริษัท / ห้อง", placeholder="เช่น บริษัท ตัวอย่าง จำกัด")
            r_place = st.text_input("ชื่อสถานที่", placeholder="เช่น สำนักงานใหญ่")
            r_lat = st.number_input("ละติจูด", value=13.7563, format="%.6f")
            r_lng = st.number_input("ลองจิจูด", value=100.5018, format="%.6f")
            r_rad = st.number_input("รัศมีเช็คอิน (เมตร)", value=100, min_value=10)
            r_start = st.text_input("เวลาเข้างาน (HH:MM)", value="09:00")
            r_grace = st.number_input("ผ่อนผันสาย (นาที)", value=15, min_value=0)

            create_btn = st.form_submit_button("สร้างห้อง")
            if create_btn:
                if r_name and r_place:
                    code = gen_code()
                    db["rooms"][code] = {
                        "code": code,
                        "name": r_name,
                        "place": r_place,
                        "lat": r_lat,
                        "lng": r_lng,
                        "radius": r_rad,
                        "start": r_start,
                        "grace": r_grace,
                        "host": me,
                        "members": [me],
                        "joined": {me: today_key()},
                        "checkins": [],  # list of dict: {email, day, ts, status}
                        "test": True  # เปิดโหมดเทสไว้ก่อนเพื่อความง่าย
                    }
                    st.session_state.current_room = code
                    st.rerun()
                else:
                    st.error("กรุณากรอกชื่อบริษัทและสถานที่")
    st.stop()

# --- 3. หน้าภายในห้อง (Room View) ---
room_code = st.session_state.current_room
room = db["rooms"].get(room_code)

if not room or me not in room["members"]:
    st.session_state.current_room = None
    st.rerun()

if st.button("← กลับไปหน้าห้องทั้งหมด"):
    st.session_state.current_room = None
    st.rerun()

st.title(room["name"])
st.markdown(
    f"📍 **สถานที่:** {room['place']} | 🔑 **รหัสห้อง:** `{room['code']}` | 👥 **สมาชิก:** {len(room['members'])} คน")

# แท็บเมนูในห้อง
tabs = ["หน้าหลัก (เช็คอิน)", "สมาชิก"]
if room["host"] == me:
    tabs.append("ตั้งค่าห้อง")

selected_tab = st.radio("เมนู", tabs, horizontal=True)
st.divider()

t_key = today_key()

if selected_tab == "หน้าหลัก (เช็คอิน)":
    st.subheader("ระบบเช็คอินเข้างาน")

    # เช็คว่าวันนี้เช็คอินยัง
    already_checked = next((c for c in room["checkins"] if c["email"] == me and c["day"] == t_key), None)

    st.write(f"⏰ เวลาเข้างาน: {room['start']} น. (สายได้ไม่เกิน {room['grace']} นาที)")

    if already_checked:
        st.success(
            f"✅ วันนี้คุณเช็คอินเรียบร้อยแล้ว เมื่อเวลา {datetime.fromtimestamp(already_checked['ts'] / 1000).strftime('%H:%M:%S')}")
    else:
        if st.button("📍 กดปุ่มเพื่อ Check-in", use_container_width=True):
            ts = int(datetime.now().timestamp() * 1000)
            # เช็คเวลาสาย/ปกติ
            now_time = datetime.now()
            sh, sm = map(int, room["start"].split(":"))
            limit_mins = sh * 60 + sm + room["grace"]
            current_mins = now_time.hour * 60 + now_time.minute

            status = "late" if current_mins > limit_mins else "ok"

            room["checkins"].append({
                "email": me,
                "day": t_key,
                "ts": ts,
                "status": status
            })
            st.success("เช็คอินสำเร็จ!")
            st.rerun()

    st.markdown("### 📊 ประวัติการเช็คอินของคุณ")
    my_history = [c for c in room["checkins"] if c["email"] == me]
    if my_history:
        for h in sorted(my_history, key=lambda x: x["day"], reverse=True):
            time_str = datetime.fromtimestamp(h["ts"] / 1000).strftime('%H:%M')
            status_text = "✅ ปกติ" if h["status"] == "ok" else "⏳ มาสาย"
            st.write(f"- วันที่ {h['day']} | เวลา {time_str} น. | สถานะ: {status_text}")
    else:
        st.info("ยังไม่มีประวัติการเช็คอิน")

elif selected_tab == "สมาชิก":
    st.subheader(f"รายชื่อสมาชิกวันนี้ ({t_key})")
    for m in room["members"]:
        m_info = db["users"].get(m, {"name": m})
        check = next((c for c in room["checkins"] if c["email"] == m and c["day"] == t_key), None)

        status_str = "❌ ยังไม่เช็คอิน"
        if check:
            time_str = datetime.fromtimestamp(check["ts"] / 1000).strftime('%H:%M')
            status_str = f"✅ เช็คอินแล้ว ({time_str})"

        is_h = " (👑 Host)" if m == room["host"] else ""
        col_m1, col_m2 = st.columns([3, 1])
        with col_m1:
            st.write(f"**{m_info['name']}**{is_h} — *{m}* : {status_str}")
        with col_m2:
            if room["host"] == me and m != me:
                if st.button("เตะออก", key=f"kick_{m}"):
                    room["members"].remove(m)
                    st.rerun()

elif selected_tab == "ตั้งค่าห้อง" and room["host"] == me:
    st.subheader("ตั้งค่าห้อง (สำหรับ Host)")
    with st.form("settings_form"):
        new_name = st.text_input("ชื่อบริษัท / ห้อง", value=room["name"])
        new_place = st.text_input("ชื่อสถานที่", value=room["place"])
        new_rad = st.number_input("รัศมี (เมตร)", value=room["radius"])
        new_start = st.text_input("เวลาเข้างาน", value=room["start"])
        new_grace = st.number_input("ผ่อนผันสาย (นาที)", value=room["grace"])

        save_btn = st.form_submit_button("บันทึกการตั้งค่า")
        if save_btn:
            room["name"] = new_name
            room["place"] = new_place
            room["radius"] = new_rad
            room["start"] = new_start
            room["grace"] = new_grace
            st.success("บันทึกเรียบร้อย!")
            st.rerun()

    if st.button("🗑️ ลบห้องนี้ถาวร", type="primary"):
        del db["rooms"][room_code]
        st.session_state.current_room = None
        st.rerun()