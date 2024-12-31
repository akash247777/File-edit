import pandas as pd
import streamlit as st
import zipfile
import io

# Function to process each CSV file
def process_file(uploaded_file):
    # Read the CSV file
    df = pd.read_csv(uploaded_file)

    # Clean column names by stripping extra spaces
    df.columns = df.columns.str.strip()

    # Remove duplicate columns by keeping the first occurrence
    df = df.loc[:, ~df.columns.duplicated()]

    # Ensure 'VAT %' column exists
    if 'VAT %' not in df.columns:
        raise ValueError("The column 'VAT %' is missing from the uploaded file.")

    # Add 'CGST' and 'SGST' columns
    df['CGST'] = df['VAT %'] / 2
    df['SGST'] = df['VAT %'] / 2

    # Rearrange columns to place 'CGST' and 'SGST' after 'VAT %'
    cols = list(df.columns)
    vat_index = cols.index('VAT %')
    cols = cols[:vat_index + 1] + ['CGST', 'SGST'] + cols[vat_index + 1:]

    # Ensure no duplicate columns before returning the dataframe
    df = df[cols]
    df = df.loc[:, ~df.columns.duplicated()]

    return df

# Streamlit app
st.title("CSV File Processor")

# File uploader for multiple files
uploaded_files = st.file_uploader("Upload CSV files", type="csv", accept_multiple_files=True)

if uploaded_files:
    try:
        # Create an in-memory ZIP file
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Process each uploaded file and add them to the zip file
            for uploaded_file in uploaded_files:
                processed_df = process_file(uploaded_file)

                # Extract the Bill Number from the processed data
                bill_number = processed_df['Bill Number'].iloc[0] if 'Bill Number' in processed_df.columns else 'processed_file'

                # Convert the DataFrame to CSV in memory
                csv_buffer = io.StringIO()
                processed_df.to_csv(csv_buffer, index=False)
                csv_data = csv_buffer.getvalue()

                # Add the CSV file to the zip archive
                zip_file.writestr(f"{bill_number}.csv", csv_data)

        # Set the position of the zip buffer to the beginning
        zip_buffer.seek(0)

        # Provide a download button for the ZIP file
        st.download_button(
            label="Download All Processed Files",
            data=zip_buffer,
            file_name="processed_files.zip",
            mime="application/zip",
        )
    except Exception as e:
        st.error(f"An error occurred: {e}")
