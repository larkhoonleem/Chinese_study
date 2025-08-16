import streamlit as st
import pandas as pd
import random
import os

# Set page config
st.set_page_config(
    page_title="Chinese Practice",
    page_icon="🇨🇳",
    layout="centered"
)

# Title and description
st.title("Chinese Practice Homework")
st.markdown("Click the button below to get a random sentence from your practice file!")

# File path - update this to match your file location
FILE_PATH = "Chinese practice homework_250503.xlsx"

# Initialize session state for random sentence
if 'current_sentence' not in st.session_state:
    st.session_state.current_sentence = None
if 'show_sentence' not in st.session_state:
    st.session_state.show_sentence = False

# Load the Excel file
@st.cache_data
def load_data(file_path):
    """Load Excel file and return dataframe"""
    try:
        # Try reading with different engines
        df = pd.read_excel(file_path, engine='openpyxl')
        return df, None
    except FileNotFoundError:
        return None, f"File '{file_path}' not found. Please check the file path."
    except Exception as e:
        return None, f"Error loading file: {str(e)}"

# Load data
df, error = load_data(FILE_PATH)

if error:
    st.error(error)
    st.info("Please make sure the Excel file is in the same directory as this script.")
    
    # Allow file upload as alternative
    st.markdown("---")
    st.subheader("Or upload your file here:")
    uploaded_file = st.file_uploader("Choose an Excel file", type=['xlsx', 'xls'])
    
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            st.success("File uploaded successfully!")
        except Exception as e:
            st.error(f"Error reading uploaded file: {str(e)}")
            df = None

# Main app logic
if df is not None:
    # Display file info
    with st.expander("📊 File Information"):
        st.write(f"Total rows: {len(df)}")
        st.write(f"Columns: {', '.join(df.columns.tolist())}")
    
    # Button to get random sentence
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🎲 Get Random Sentence", type="primary", use_container_width=True):
            # Select random row
            random_index = random.randint(0, len(df) - 1)
            st.session_state.current_sentence = df.iloc[random_index]
            st.session_state.show_sentence = True
    
    # Display the random sentence
    if st.session_state.show_sentence and st.session_state.current_sentence is not None:
        st.markdown("---")
        st.subheader("📝 Your Random Sentence:")
        
        # Create cards for each column value
        sentence_data = st.session_state.current_sentence
        
        # Display each column in a nice format
        for column_name in df.columns:
            value = sentence_data[column_name]
            
            # Skip if value is NaN or empty
            if pd.isna(value) or (isinstance(value, str) and value.strip() == ''):
                continue
            
            # Create a nice display for each field
            with st.container():
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.markdown(f"**{column_name}:**")
                with col2:
                    # Display value with larger font if it contains Chinese characters
                    if isinstance(value, str) and any('\u4e00' <= char <= '\u9fff' for char in str(value)):
                        st.markdown(f"<p style='font-size: 24px; margin: 0;'>{value}</p>", 
                                  unsafe_allow_html=True)
                    else:
                        st.markdown(f"<p style='font-size: 18px; margin: 0;'>{value}</p>", 
                                  unsafe_allow_html=True)
        
        # Add row number info
        st.caption(f"Row #{df.index.get_loc(st.session_state.current_sentence.name) + 1} of {len(df)}")
        
        # Option to show/hide full row data
        with st.expander("🔍 View Raw Data"):
            st.write(sentence_data.to_dict())
    
    # Statistics section
    st.markdown("---")
    with st.expander("📈 Practice Statistics"):
        if 'practice_count' not in st.session_state:
            st.session_state.practice_count = 0
        if 'practiced_rows' not in st.session_state:
            st.session_state.practiced_rows = set()
        
        # Update stats when new sentence is shown
        if st.session_state.show_sentence and st.session_state.current_sentence is not None:
            row_index = df.index.get_loc(st.session_state.current_sentence.name)
            if row_index not in st.session_state.practiced_rows:
                st.session_state.practiced_rows.add(row_index)
                st.session_state.practice_count += 1
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Practices", st.session_state.practice_count)
        with col2:
            coverage = (len(st.session_state.practiced_rows) / len(df)) * 100
            st.metric("Coverage", f"{coverage:.1f}%")
        
        # Progress bar
        st.progress(len(st.session_state.practiced_rows) / len(df))
        st.caption(f"You've practiced {len(st.session_state.practiced_rows)} out of {len(df)} unique sentences")

else:
    st.warning("⚠️ No data loaded. Please check the file path or upload a file.")

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>加油! Keep practicing! 💪</p>", 
           unsafe_allow_html=True)