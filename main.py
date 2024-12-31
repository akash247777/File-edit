import pandas as pd
import streamlit as st

# Function to process the CSV file
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

# File uploader
uploaded_file = st.file_uploader("Upload your CSV file", type="csv")

if uploaded_file:
    try:
        # Process the uploaded file
        processed_df = process_file(uploaded_file)

        # Display the processed DataFrame
        st.write("Processed Data:")
        st.dataframe(processed_df)

        # Convert DataFrame to CSV
        processed_file = processed_df.to_csv(index=False).encode('utf-8')

        # Download button for processed file
        st.download_button(
            label="Download Processed File",
            data=processed_file,
            file_name="processed_file.csv",
            mime="text/csv",
        )
    except Exception as e:
        st.error(f"An error occurred: {e}")
