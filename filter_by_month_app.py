import streamlit as st
import pandas as pd
from io import BytesIO

def filter_by_month(data, month):
    """
    Filters the data based on the specified month for Birth, Death, and Other columns.

    :param data: DataFrame, input data with datetime columns.
    :param month: int, month to filter by (1-12).
    :return: DataFrame, filtered data.
    """
    # Convert Birth, Death, and Other columns to datetime
    for col in ['Birth', 'Death', 'Other']:
        data[col] = pd.to_datetime(data[col], errors='coerce')

    # Filter the data based on the selected month
    filtered_data = data[
        (data['Birth'].dt.month == month) |
        (data['Death'].dt.month == month) |
        (data['Other'].dt.month == month)
    ]
    return filtered_data

# Streamlit app
st.title("Filter Excel Data by Month")

# File uploader
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file:
    # Read the uploaded Excel file
    sheet_names = pd.ExcelFile(uploaded_file).sheet_names
    sheet_name = st.selectbox("Select a sheet", sheet_names)

    if sheet_name:
        data = pd.read_excel(uploaded_file, sheet_name=sheet_name)

        # Check for required columns
        required_columns = ['Birth', 'Death', 'Other']
        if all(col in data.columns for col in required_columns):

            # Month selection
            month = st.number_input("Enter the month (1-12):", min_value=1, max_value=12, step=1)

            if st.button("Filter Data"):
                # Filter the data
                filtered_data = filter_by_month(data, month)

                if not filtered_data.empty:
                    st.success(f"Found {len(filtered_data)} records for the selected month.")
    
                    # Explicitly create a copy of the filtered DataFrame to avoid SettingWithCopyWarning
                    filtered_data = filtered_data.copy()
                    
                    
                    # Ensure serialization compatibility
                    for col in filtered_data.columns:
                        if not pd.api.types.is_datetime64_any_dtype(filtered_data[col]):
                            filtered_data[col] = filtered_data[col].astype(str)

                    # Display filtered data
                    st.dataframe(filtered_data)

                    # Download button
                    output = BytesIO()
                    filtered_data.to_csv(output, index=False, encoding='utf-8-sig')
                    output.seek(0)

                    st.download_button(
                        label="Download Filtered Data as CSV",
                        data=output,
                        file_name=f"filtered_data_{month}.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("No records found for the selected month.")
            
        else:
            st.error(f"The uploaded file must contain the following columns: {', '.join(required_columns)}")
