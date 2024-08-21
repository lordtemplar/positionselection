import pandas as pd
import streamlit as st

# Updated URLs for your Google Sheets
positions_url = 'https://docs.google.com/spreadsheets/d/1mflUv6jyOqTXplPGiSxCOp7wJ1HHd4lQ4BSIzvuBgoQ/export?format=csv'
students_url = 'https://docs.google.com/spreadsheets/d/1lwfcVb8GwSLN9RSZyiyzaCjS8jywgaNS5Oj8k7Lhemw/export?format=csv'

# Read the data into pandas DataFrames
positions_df = pd.read_csv(positions_url)
students_df = pd.read_csv(students_url)

# Streamlit UI
st.title("Army Staff Officer Position Selection System")

# Display Students and Positions Data
if st.checkbox("Show Students Data"):
    st.dataframe(students_df)

if st.checkbox("Show Positions Data"):
    st.dataframe(positions_df)

# Example function: Select a student and assign a position
st.header("Assign Position to Student")

selected_student_id = st.selectbox("Select Student ID", students_df['StudentID'])
selected_position_id = st.selectbox("Select Position ID", positions_df[positions_df['Status'] == 'ว่าง']['PositionID'])

if st.button("Assign Position"):
    # Find the selected student and position
    student_index = students_df[students_df['StudentID'] == selected_student_id].index[0]
    position_index = positions_df[positions_df['PositionID'] == selected_position_id].index[0]

    # Assign the position
    positions_df.at[position_index, 'Status'] = 'ไม่ว่าง'
    positions_df.at[position_index, 'SelectedByStudentID'] = selected_student_id

    st.success(f"Position {selected_position_id} assigned to student {selected_student_id}")

# Display the updated positions
if st.button("Refresh Positions Data"):
    st.dataframe(positions_df)
