import streamlit as st
from db_connections import firebase_apps  # Import initialized Firebase apps
from firebase_admin import db

# Set the title of the Streamlit app
st.set_page_config(page_title="Position Confirm")

# Function to fetch student data by rank from the first Firebase database
def fetch_student_by_rank(rank):
    try:
        ref = db.reference('/', firebase_apps['firebase1'])
        data = ref.get()
        if data:
            for key, value in data.items():
                if 'Rank' in value and str(value['Rank']) == str(rank):
                    return key, value  # Return both the key and the student data
        return None, None
    except Exception as e:
        st.error(f"Error fetching student data: {e}")
        return None, None

# Function to update student data in the first Firebase database
def update_student_data(student_key, update_data):
    try:
        ref = db.reference(f"/{student_key}", firebase_apps['firebase1'])
        ref.update(update_data)
    except Exception as e:
        st.error(f"Error updating student data: {e}")

# Function to fetch position data from the second Firebase database
def fetch_position_data(position_ids):
    try:
        ref = db.reference('/', app=firebase_apps['firebase2'])
        data = ref.get()
        matching_positions = {}

        # Check if data is a list or dictionary and process accordingly
        if isinstance(data, dict):
            for key, value in data.items():
                if 'PositionID' in value and int(value['PositionID']) in position_ids:
                    matching_positions[int(value['PositionID'])] = value['PositionName']
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and 'PositionID' in item and int(item['PositionID']) in position_ids:
                    matching_positions[int(item['PositionID'])] = item['PositionName']

        return matching_positions

    except Exception as e:
        st.error(f"Error fetching position data: {e}")
        return {}

# Layout of the Streamlit app
st.title("ระบบเลือกที่ลง CGSC102")

# Initialize session state for storing student data
if 'student_data' not in st.session_state:
    st.session_state['student_data'] = None
if 'last_search_query' not in st.session_state:
    st.session_state['last_search_query'] = ""

# Input box for searching by rank
rank_query = st.text_input("กรุณาใส่ลำดับผลการเรียน:")

# Check if the search query has changed
if rank_query and rank_query != st.session_state['last_search_query']:
    st.session_state['student_data'] = None
    st.session_state['last_search_query'] = rank_query

if rank_query:
    if st.session_state['student_data'] is None:
        # Fetch student data from Firebase
        student_key, student_data = fetch_student_by_rank(rank_query)
        if student_data:
            st.session_state['student_data'] = student_data
            st.session_state['student_key'] = student_key
        else:
            st.error("ไม่พบข้อมูลที่ค้นหา")
            st.session_state['student_data'] = None

    if st.session_state['student_data'] is not None:
        student_info = st.session_state['student_data']
        st.session_state.update({
            'rank_name': student_info['RankName'],
            'branch': student_info['Branch'],
            'officer_type': student_info['OfficerType'],
            'other': student_info['Other'],
            'rank': str(student_info['Rank']),
            'position1': int(student_info['Position1']),
            'position2': int(student_info['Position2']),
            'position3': int(student_info['Position3'])
        })

        # Function to refresh position data
        def refresh_position_data():
            position_ids = [st.session_state['position1'], st.session_state['position2'], st.session_state['position3']]
            return fetch_position_data(position_ids)

        # Fetch and refresh position data
        matching_positions = refresh_position_data()

        # Placeholder for the table to dynamically update
        table_placeholder = st.empty()

        def display_student_info():
            # Display student information with position names in a table format
            table_placeholder.markdown(f"""
            <table>
                <tr><th>รหัสนักเรียน</th><td>{student_info['StudentID']}</td></tr>
                <tr><th>ยศ ชื่อ สกุล</th><td>{st.session_state['rank_name']}</td></tr>
                <tr><th>ลำดับ</th><td>{st.session_state['rank']}</td></tr>
                <tr><th>เหล่า</th><td>{st.session_state['branch']}</td></tr>
                <tr><th>กำเนิด</th><td>{st.session_state['officer_type']}</td></tr>
                <tr><th>อื่นๆ</th><td>{st.session_state['other']}</td></tr>
                <tr><th>ตำแหน่งลำดับ 1</th><td>{st.session_state['position1']} - {matching_positions.get(st.session_state['position1'], 'N/A')}</td></tr>
                <tr><th>ตำแหน่งลำดับ 2</th><td>{st.session_state['position2']} - {matching_positions.get(st.session_state['position2'], 'N/A')}</td></tr>
                <tr><th>ตำแหน่งลำดับ 3</th><td>{st.session_state['position3']} - {matching_positions.get(st.session_state['position3'], 'N/A')}</td></tr>
            </table>
            """, unsafe_allow_html=True)

        # Display the initial student information
        display_student_info()

        # Input field for confirming the selected position
        st.write("### ยืนยัน 'รหัสตำแหน่ง' ที่เลือก")
        confirmed_position_input = st.text_input("ยืนยันตำแหน่งที่เลือก", "")

        # Validate and update positions
        if confirmed_position_input:
            if not confirmed_position_input.isdigit():
                st.error("กรุณากรอกรหัสด้วยตัวเลขสำหรับตำแหน่งที่เลือก")
            else:
                confirmed_position = int(confirmed_position_input)
                if confirmed_position not in [st.session_state['position1'], st.session_state['position2'], st.session_state['position3']]:
                    st.error("ตำแหน่งที่เลือกไม่ถูกต้อง กรุณาเลือกจากตำแหน่งที่ระบุไว้")
                else:
                    # Submit button to confirm selection
                    if st.button("Confirm Selection"):
                        try:
                            update_data = {
                                'ConfirmedPosition': confirmed_position
                            }
                            update_student_data(st.session_state['student_key'], update_data)
                            st.success(f"ยืนยันข้อมูลตำแหน่งที่เลือกของรหัสนายทหารนักเรียน {student_info['StudentID']} สำเร็จแล้ว")

                            # Refresh the existing table with new data
                            display_student_info()

                        except Exception as e:
                            st.error(f"ไม่สามารถยืนยันข้อมูลได้: {e}")
