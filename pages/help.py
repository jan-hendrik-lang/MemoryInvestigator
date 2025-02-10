import streamlit as st

# Function to load README.md
def load_readme():
    with open("README.md", "r", encoding="utf-8") as file:
        return file.read()

# Streamlit Page
st.title("Help Page")

# Display README.md content
readme_content = load_readme()
st.markdown(readme_content, unsafe_allow_html=True)