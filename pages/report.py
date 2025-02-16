import os
import platform
import streamlit as st
import google.generativeai as genai

# Detect operating system
os_name = platform.system()

# Define appropriate file path based on OS
if os_name == "Windows":
    report_file_path = "O:/analysis_report.txt"
else:  # Linux/macOS
    report_file_path = "/tmp/MemoryInvestigator/analysis_report.txt"

# Streamlit page title and description
st.title("Report Generator")
st.caption("Generate a report summarizing your findings.")

# Select an LLM model
left, right = st.columns(2)
llm_options = ["gemini-1.5-flash", "gemini-2.0-flash-exp"]
llm_option = left.selectbox(
    "Select an LLM of your choice:",
    options=llm_options,
    index=0
)

# Input field for API key
api_key = right.text_input("API LLM Key Input:", type="password")

if api_key:
    # Google LLM Options
    if llm_option in ["gemini-1.5-flash", "gemini-2.0-flash-exp"]:
        genai.configure(api_key=api_key)
        prompt = st.chat_input("Ask Gemini about helping to summarize your key findings:")

        # Define the model and instructions for forensic analysis report generation
        model = genai.GenerativeModel(model_name=llm_option, system_instruction="You are a forensic RAM Analyst Assistant. Help summarizing the key findings to a LaTeX file.")
        convo = model.start_chat(history=[])

        # Send user prompt
        if prompt:
            with st.spinner("Fetching response..."):
                answer = convo.send_message(prompt)
                txt_content = convo.last.text

            # Save output as a Word file
            try:
                os.makedirs(os.path.dirname(report_file_path), exist_ok=True)
                with open(report_file_path, "w", encoding="utf-8") as txt_file:
                    txt_file.write(txt_content)
                st.success(f"Word file saved to {report_file_path}")
            except Exception as e:
                st.error(f"Failed to save Text file: {e}")

            st.write("**Gemini says:**", txt_content)
