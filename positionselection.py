import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st

# Set up the Google Sheets API credentials
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(
    'client_secret_832036772434-ei5ks7v45scnpu4fjhuemsctv3uv4uj8.apps.googleusercontent.com.json', scope)
client = gspread.authorize(creds)

# Open the Google Sheet
sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1lwfcVb8GwSLN9RSZyiyzaCjS8jywgaNS5Oj8k7Lhemw')  # Replace with your Google Sheets URL
worksheet = sheet.sheet1  # or replace with the name of your sheet

# Function to load data into a DataFrame
def load_data():
    records = worksheet.get_all_records()
    df = pd.DataFrame(records)
    return df

# Function to update a specific row in the Google Sheet
def update_row(student_id, updated_data):
    cell = worksheet.find(student_id)
    if cell:
        row = cell.row
        worksheet.update(f'B{row}:F{row}', [updated_data])  # Update columns B to F
        return True
    return False

# Function to filter positions based on student data
def filter_positions(df_positions, branch, officer_type, other_condition):
    filtered_positions = df_positions[(df_positions['BranchCondition'] == branch) &
                                      (df_positions['OfficerTypeCondition'] == officer_type) &
                                      (df_positions['OtherCondition'] == other_condition)]
    return filtered_positions

# Step 1: Input Student ID
st.title("Student Position Selection System")
student_id = st.text_input("Enter Student ID:")

if student_id:
    # Step 2: Show Student Information with "EDIT" and "NEXT" buttons
    df_students = load_data()
    student_data = df_students[df_students['StudentID'] == student_id]
    
    if not student_data.empty:
        st.write("### Student Information")
        st.table(student_data)
        
        if st.button("EDIT"):
            # Step 3: Edit mode
            st.write("### Edit Student Information")
            rank_name = st.text_input("Rank Name", student_data.iloc[0]['RankName'])
            branch = st.selectbox("Branch", ["ร.", "ม.", "ป."], index=["ร.", "ม.", "ป."].index(student_data.iloc[0]['Branch']))
            officer_type = st.selectbox("Officer Type", ["นร.", "นป.", "ปริญญา", "พิเศษ"], index=["นร.", "นป.", "ปริญญา", "พิเศษ"].index(student_data.iloc[0]['OfficerType']))
            rank = st.text_input("Rank", student_data.iloc[0]['Rank'])
            other = st.text_input("Other", student_data.iloc[0]['Other'])
            
            if st.button("SAVE"):
                if update_row(student_id, [rank_name, branch, officer_type, rank, other]):
                    st.success("Student information updated successfully!")
                else:
                    st.error("Failed to update student information.")
        
        if st.button("NEXT"):
            # Step 4: Position Selection Step
            df_positions = pd.read_csv('positions.csv')  # Assume positions data is loaded from a CSV file
            st.write("### Position Selection")
            
            # Filter positions based on the student's branch, officer type, and other condition
            filtered_positions = filter_positions(df_positions, student_data.iloc[0]['Branch'], 
                                                  student_data.iloc[0]['OfficerType'], 
                                                  student_data.iloc[0]['Other'])
            
            if not filtered_positions.empty:
                st.write("#### Available Positions")
                st.table(filtered_positions)
                
                position1 = st.selectbox("1st Choice", filtered_positions['PositionID'].tolist())
                position2 = st.selectbox("2nd Choice", filtered_positions['PositionID'].tolist())
                position3 = st.selectbox("3rd Choice", filtered_positions['PositionID'].tolist())
                
                if st.button("SUBMIT"):
                    # Save the selected positions
                    df_students.loc[df_students['StudentID'] == student_id, ['Position1', 'Position2', 'Position3']] = [position1, position2, position3]
                    st.write("### Review Selected Positions")
                    st.table(df_students[df_students['StudentID'] == student_id][['StudentID', 'RankName', 'Branch', 'OfficerType', 'Position1', 'Position2', 'Position3']])
                    
                    if st.button("CONFIRM"):
                        # Update Google Sheets with selected positions
                        if update_row(student_id, [rank_name, branch, officer_type, rank, other]):
                            st.success("Student positions confirmed and saved!")
                        else:
                            st.error("Failed to save positions.")
            else:
                st.warning("No positions available that match your criteria.")
    else:
        st.error("Student ID not found.")
