import pandas as pd
import streamlit as st
import requests

# URLs for your Google Sheets (CSV format)
positions_url = 'https://docs.google.com/spreadsheets/d/1mflUv6jyOqTXplPGiSxCOp7wJ1HHd4lQ4BSIzvuBgoQ/export?format=csv'
students_url = 'https://docs.google.com/spreadsheets/d/1lwfcVb8GwSLN9RSZyiyzaCjS8jywgaNS5Oj8k7Lhemw/export?format=csv'

# URLs for your Google Sheets (Edit format)
positions_edit_url = 'https://docs.google.com/spreadsheets/d/1mflUv6jyOqTXplPGiSxCOp7wJ1HHd4lQ4BSIzvuBgoQ'
students_edit_url = 'https://docs.google.com/spreadsheets/d/1lwfcVb8GwSLN9RSZyiyzaCjS8jywgaNS5Oj8k7Lhemw'

# Read the data into pandas DataFrames
positions_df = pd.read_csv(positions_url, dtype={'PositionID': str, 'SelectedByStudentID': str})
students_df = pd.read_csv(students_url, dtype={'StudentID': str})

# Replace any NaN values in SelectedByStudentID and Other columns with "ไม่มี"
positions_df['SelectedByStudentID'] = positions_df['SelectedByStudentID'].fillna("ไม่มี")
students_df['Other'] = students_df['Other'].fillna("ไม่มี")

# Streamlit UI
st.title("Army Staff Officer Position Selection System")

# Navigation Sidebar
st.sidebar.title("Navigation")
section = st.sidebar.radio("Go to", ["Student Information", "Position Information", "Edit Student Information", "Assign Position", "Edit Assigned Position"])

# Section 1: Student Information
if section == "Student Information":
    st.header("Student Information")
    student_id = st.text_input("Enter Student ID")
    
    if st.button("Search"):
        if student_id:
            student_data = students_df[students_df['StudentID'] == student_id]
            if not student_data.empty:
                st.table(student_data.set_index('StudentID'))
            else:
                st.warning("Student ID not found.")
        else:
            st.warning("Please enter a Student ID.")
    
    if st.button("Show All"):
        st.table(students_df.set_index('StudentID'))

# Section 2: Position Information
elif section == "Position Information":
    st.header("Position Information")
    position_id = st.text_input("Enter Position ID")
    
    if st.button("Search"):
        if position_id:
            position_data = positions_df[positions_df['PositionID'] == position_id]
            if not position_data.empty:
                st.table(position_data.set_index('PositionID'))
            else:
                st.warning("Position ID not found.")
        else:
            st.warning("Please enter a Position ID.")
    
    if st.button("Show All"):
        st.table(positions_df.set_index('PositionID'))

# Section 3: Edit Student Information
elif section == "Edit Student Information":
    st.header("Edit Student Information")
    
    student_id = st.text_input("Enter Student ID to Edit")
    
    if st.button("Search Student"):
        student_data = students_df[students_df['StudentID'] == student_id]
        if not student_data.empty:
            # Display fields for editing
            student_data = student_data.iloc[0]  # Get the first row as a Series
            rank_name = st.text_input("Rank Name", student_data['RankName'])
            branch = st.selectbox("Branch", ["ร.", "ม.", "ป."], index=["ร.", "ม.", "ป."].index(student_data['Branch']))
            officer_type = st.selectbox("Officer Type", ["นร.", "นป.", "ปริญญา", "พิเศษ"], index=["นร.", "นป.", "ปริญญา", "พิเศษ"].index(student_data['OfficerType']))
            score = st.number_input("Score", value=student_data['Score'], step=1)
            other = st.text_input("Other", value=student_data['Other'])  # "Other" condition
            
            if st.button("Update"):
                # Update the DataFrame
                students_df.loc[students_df['StudentID'] == student_id, ['RankName', 'Branch', 'OfficerType', 'Score', 'Other']] = [rank_name, branch, officer_type, score, other]
                
                # Convert DataFrame back to CSV and post to Google Sheets
                students_df.to_csv('updated_students.csv', index=False)
                
                # Read the updated CSV file
                with open('updated_students.csv', 'r') as file:
                    updated_data = file.read()
                
                # Update Google Sheets by uploading the CSV
                url = f'{students_edit_url}/gviz/tq?tqx=out:csv'
                headers = {"Content-Type": "text/csv"}
                response = requests.post(url, data=updated_data, headers=headers)
                
                if response.status_code == 200:
                    st.success("Student information updated successfully!")
                else:
                    st.error(f"Failed to update Google Sheets. Status code: {response.status_code}")
        else:
            st.warning("Student ID not found.")

# Section 4: Assign Position
elif section == "Assign Position":
    st.header("Assign Position to Student")

    student_id = st.selectbox("Select Student ID", students_df['StudentID'])
    selected_student = students_df[students_df['StudentID'] == student_id].iloc[0]
    
    position1 = st.selectbox("1st Choice", positions_df[positions_df['Status'] == 'ว่าง']['PositionID'])
    position2 = st.selectbox("2nd Choice", positions_df[positions_df['Status'] == 'ว่าง']['PositionID'])
    position3 = st.selectbox("3rd Choice", positions_df[positions_df['Status'] == 'ว่าง']['PositionID'])
    
    if st.button("Assign Positions"):
        students_df.loc[students_df['StudentID'] == student_id, ['Position1', 'Position2', 'Position3']] = [position1, position2, position3]
        positions_df.loc[positions_df['PositionID'].isin([position1, position2, position3]), 'Status'] = 'ไม่ว่าง'
        positions_df.loc[positions_df['PositionID'].isin([position1, position2, position3]), 'SelectedByStudentID'] = student_id
        
        st.success(f"Positions assigned to student {student_id}")

# Section 5: Edit Assigned Position
elif section == "Edit Assigned Position":
    st.header("Edit Assigned Position")
    
    student_id = st.selectbox("Select Student ID to Edit Assigned Position", students_df['StudentID'])
    selected_student = students_df[students_df['StudentID'] == student_id].iloc[0]
    
    position1 = st.selectbox("1st Choice", positions_df['PositionID'], index=positions_df[positions_df['PositionID'] == selected_student['Position1']].index[0])
    position2 = st.selectbox("2nd Choice", positions_df['PositionID'], index=positions_df[positions_df['PositionID'] == selected_student['Position2']].index[0])
    position3 = st.selectbox("3rd Choice", positions_df['PositionID'], index=positions_df[positions_df['PositionID'] == selected_student['Position3']].index[0])
    
    if st.button("Update Assigned Positions"):
        students_df.loc[students_df['StudentID'] == student_id, ['Position1', 'Position2', 'Position3']] = [position1, position2, position3]
        positions_df.loc[positions_df['PositionID'].isin([position1, position2, position3]), 'SelectedByStudentID'] = student_id
        st.success(f"Assigned positions updated for student {student_id}")

# Optional: Refresh the data if needed
if st.sidebar.button("Refresh Data"):
    positions_df = pd.read_csv(positions_url, dtype={'PositionID': str, 'SelectedByStudentID': str})
    students_df = pd.read_csv(students_url, dtype={'StudentID': str})
    positions_df['SelectedByStudentID'] = positions_df['SelectedByStudentID'].fillna("ไม่มี")
    students_df['Other'] = students_df['Other'].fillna("ไม่มี")
    st.experimental_rerun()
