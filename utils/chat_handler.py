import os
import re
import shutil
import platform
import streamlit as st
import google.generativeai as genai
from openai import OpenAI

# Import utility functions to divide the json file and to select the basic or costume tree
from utils.json_divider import divide_json
from utils.select_tree import choose_basic_or_costume_tree

# Detect operating system
os_name = platform.system()

# Define appropriate temp directory based on OS
if os_name == "Windows":
    temp_path = "O:\\03_trees\\temp"
else:  # Linux/macOS
    temp_path = "/tmp/MemoryInvestigator/03_trees/temp"

def handle_llm_chat(llm_option, api_key, number_of_divided_jsons, prompt):
    """
    Handles interaction with an LLM (either Gemini or OpenAI models) for forensic RAM analysis.

    :param llm_option: The selected LLM model (Gemini or OpenAI).
    :param api_key: API key for authentication.
    :param number_of_divided_jsons: Number of parts the JSON should be divided into for processing.
    :param prompt: User input prompt for guiding the LLM response.
    :return: None, outputs results directly in Streamlit.
    """
    # Google LLM Options
    if llm_option.startswith("gemini"):
        genai.configure(api_key=api_key)
        tree = choose_basic_or_costume_tree()
        if tree is not None:
            if number_of_divided_jsons > 1:
                all_responses = []
                divide_json(number_of_divided_jsons, tree, temp_path)
                for i in range(number_of_divided_jsons):
                    file_name = os.path.join(temp_path, f"temp_{i + 1:02d}.json")
                    with open(file_name, 'r', encoding='utf-8') as file:
                        chunk = file.read()
                        chunk = re.sub(r'"children": \[\]', ' ', chunk)  # Replace empty children with a space
                        chunk = re.sub(r'Required memory at 0x[0-9a-fA-F]+ is not valid \(process exited\?\)', '', chunk)  # Remove error message
                        chunk = re.sub(r'Required memory at 0x[0-9a-fA-F]+ is inaccessible \(swapped\)', '', chunk)  # Remove error message

                        cleaned_chunk = re.sub(r'\s+', ' ', chunk).strip()  # Replace all whitespace (newlines, tabs, spaces) with a single space

                        model = genai.GenerativeModel(model_name=llm_option, system_instruction=f"You are a forensic RAM Analyst Assistant specializing in Windows memory analysis. Analyze the JSON tree of Windows memory artifacts to detect intrusions or malicious activities. Cross-check your findings with known threats and provide clear, specific reasons for flagging any anomalies (e.g., unusual parent-child relationships, code injection, execution from non-standard locations). If you're unsure, ask clarifying questions; if you don't know, say so. Generate a structured forensic report highlighting confirmed threats while minimizing noise. Data: {cleaned_chunk}")
                        convo = model.start_chat(history=[])

                        if prompt:
                            with st.spinner(f"Fetching response for part {i + 1}..."):
                                response = convo.send_message(prompt)
                                all_responses.append(convo.last.text)
                            st.write(f"**Gemini says (part {i + 1}):**", convo.last.text)

                if all_responses:
                    summary_prompt = "Summarize the findings from all parts of the JSON data. " + " ".join(
                        all_responses)
                    model = genai.GenerativeModel(model_name=llm_option, system_instruction="You are a forensic RAM Analyst Assistant specializing in Windows memory analysis. Analyze the JSON tree of Windows memory artifacts to detect intrusions or malicious activities. Cross-check your findings with known threats and provide clear, specific reasons for flagging any anomalies (e.g., unusual parent-child relationships, code injection, execution from non-standard locations). If you're unsure, ask clarifying questions; if you don't know, say so. Generate a structured forensic report highlighting confirmed threats while minimizing noise.")
                    convo = model.start_chat(history=[])
                    with st.spinner("Fetching summary..."):
                        summary_response = convo.send_message(summary_prompt)
                    st.write("**Gemini's Summary:**", convo.last.text)
                    shutil.rmtree(temp_path, ignore_errors=True)
            else:
                with open(tree, 'r', encoding='utf-8') as file:
                    json_data = file.read()
                    json_data = re.sub(r'"children": \[\]', ' ', json_data)  # Replace empty children with a space
                    json_data = re.sub(r'Required memory at 0x[0-9a-fA-F]+ is not valid \(process exited\?\)', '', json_data)  # Remove error message
                    json_data = re.sub(r'Required memory at 0x[0-9a-fA-F]+ is inaccessible \(swapped\)', '', json_data)  # Remove error message
                    cleaned_json_data = re.sub(r'\s+', ' ', json_data).strip()  # Replace all whitespace (newlines, tabs, spaces) with a single space

                    model = genai.GenerativeModel(model_name=llm_option, system_instruction=f"You are a forensic RAM Analyst Assistant specializing in Windows memory analysis. Analyze the JSON tree of Windows memory artifacts to detect intrusions or malicious activities. Cross-check your findings with known threats and provide clear, specific reasons for flagging any anomalies (e.g., unusual parent-child relationships, code injection, execution from non-standard locations). If you're unsure, ask clarifying questions; if you don't know, say so. Generate a structured forensic report highlighting confirmed threats while minimizing noise. Data: {cleaned_json_data}")

                    convo = model.start_chat(history=[])

                    if prompt:
                        with st.spinner("Fetching response..."):
                            response = convo.send_message(prompt)
                        st.write(f"**Gemini says:**", convo.last.text)
        else:
            st.error("Please build a tree first.")

    # OpenAI LLM Options
    elif llm_option in ["gpt-4o", "gpt-3.5-turbo"]:
        tree = choose_basic_or_costume_tree()
        client = OpenAI(api_key=api_key)
        if tree is not None:
            if number_of_divided_jsons > 1:
                all_responses = []
                divide_json(number_of_divided_jsons, tree, temp_path)
                for i in range(number_of_divided_jsons):
                    file_name = os.path.join(temp_path, f"temp_{i + 1:02d}.json")
                    with open(file_name, 'r', encoding='utf-8') as file:
                        chunk = file.read()
                        chunk = re.sub(r'"children": \[\]', ' ', chunk)  # Replace empty children with a space
                        chunk = re.sub(r'Required memory at 0x[0-9a-fA-F]+ is not valid \(process exited\?\)', '', chunk)  # Remove error message
                        chunk = re.sub(r'Required memory at 0x[0-9a-fA-F]+ is inaccessible \(swapped\)', '', chunk)  # Remove error message

                        cleaned_chunk = re.sub(r'\s+', ' ', chunk).strip()  # Replace all whitespace (newlines, tabs, spaces) with a single space

                        if prompt:
                            with st.spinner(f"Fetching response for part {i + 1}..."):
                                completion = client.chat.completions.create(
                                    model=llm_option,
                                    messages=[
                                        {"role": "system",
                                         "content": f"You are a forensic RAM Analyst Assistant specializing in Windows memory analysis. Analyze the JSON tree of Windows memory artifacts to detect intrusions or malicious activities. Cross-check your findings with known threats and provide clear, specific reasons for flagging any anomalies (e.g., unusual parent-child relationships, code injection, execution from non-standard locations). If you're unsure, ask clarifying questions; if you don't know, say so. Generate a structured forensic report highlighting confirmed threats while minimizing noise. Data: {cleaned_chunk}"},
                                        {"role": "user", "content": prompt}
                                    ]
                                )
                                all_responses.append(completion.choices[0].message.content)
                            st.write(f"**ChatGPT says (part {i + 1}):**", completion.choices[0].message.content)

                if all_responses:
                    summary_prompt = "Summarize the findings from all parts of the JSON data. " + " ".join(
                        all_responses)
                    with st.spinner("Fetching summary..."):
                        completion = client.chat.completions.create(
                            model=llm_option,
                            messages=[
                                {"role": "system",
                                 "content": "You are a forensic RAM Analyst Assistant specializing in Windows memory analysis. Analyze the JSON tree of Windows memory artifacts to detect intrusions or malicious activities. Cross-check your findings with known threats and provide clear, specific reasons for flagging any anomalies (e.g., unusual parent-child relationships, code injection, execution from non-standard locations). If you're unsure, ask clarifying questions; if you don't know, say so. Generate a structured forensic report highlighting confirmed threats while minimizing noise."},
                                {"role": "user", "content": summary_prompt}
                            ]
                        )
                    st.write("**ChatGPT's Summary:**", completion.choices[0].message.content)
                    shutil.rmtree(temp_path, ignore_errors=True)
            else:
                with open(tree, 'r', encoding='utf-8') as file:
                    json_data = file.read()
                    json_data = re.sub(r'"children": \[\]', ' ', json_data)  # Replace empty children with a space
                    json_data = re.sub(r'Required memory at 0x[0-9a-fA-F]+ is not valid \(process exited\?\)', '', json_data)  # Remove error message
                    json_data = re.sub(r'Required memory at 0x[0-9a-fA-F]+ is inaccessible \(swapped\)', '', json_data)  # Remove error message

                    cleaned_json_data = re.sub(r'\s+', ' ', json_data).strip()  # Replace all whitespace (newlines, tabs, spaces) with a single space

                    if prompt:
                        with st.spinner("Fetching response..."):
                            completion = client.chat.completions.create(
                                model=llm_option,
                                messages=[
                                    {"role": "system",
                                     "content": f"You are a forensic RAM Analyst Assistant specializing in Windows memory analysis. Analyze the JSON tree of Windows memory artifacts to detect intrusions or malicious activities. Cross-check your findings with known threats and provide clear, specific reasons for flagging any anomalies (e.g., unusual parent-child relationships, code injection, execution from non-standard locations). If you're unsure, ask clarifying questions; if you don't know, say so. Generate a structured forensic report highlighting confirmed threats while minimizing noise. Data: {cleaned_json_data}"},
                                    {"role": "user", "content": prompt}
                                ]
                            )
                        st.write(f"**ChatGPT says:**", completion.choices[0].message.content)

        else:
            st.error("Please build a tree first.")

    # OpenAI LLM Options
    elif llm_option in ["o1-preview", "o1", "o1-2024-12-17"]:
        tree = choose_basic_or_costume_tree()
        client = OpenAI(api_key=api_key)
        if tree is not None:
            if number_of_divided_jsons > 1:
                all_responses = []
                divide_json(number_of_divided_jsons, tree, temp_path)
                for i in range(number_of_divided_jsons):
                    file_name = os.path.join(temp_path, f"temp_{i + 1:02d}.json")
                    with open(file_name, 'r', encoding='utf-8') as file:
                        chunk = file.read()
                        chunk = re.sub(r'"children": \[\]', ' ', chunk)  # Replace empty children with a space
                        chunk = re.sub(r'Required memory at 0x[0-9a-fA-F]+ is not valid \(process exited\?\)', '', chunk)  # Remove error message
                        chunk = re.sub(r'Required memory at 0x[0-9a-fA-F]+ is inaccessible \(swapped\)', '', chunk)  # Remove error message

                        cleaned_chunk = re.sub(r'\s+', ' ', chunk).strip()  # Replace all whitespace (newlines, tabs, spaces) with a single space

                        if prompt:
                            with st.spinner(f"Fetching response for part {i + 1}..."):
                                completion = client.chat.completions.create(
                                    model=llm_option,
                                    messages=[
                                        {"role": "user", "content": f"{cleaned_chunk}\n\n{prompt}"}
                                    ]
                                )
                                all_responses.append(completion.choices[0].message.content)
                            st.write(f"**ChatGPT says (part {i + 1}):**", completion.choices[0].message.content)

                if all_responses:
                    summary_prompt = "Summarize the findings from all parts of the JSON data. " + " ".join(
                        all_responses)
                    with st.spinner("Fetching summary..."):
                        completion = client.chat.completions.create(
                            model=llm_option,
                            messages=[
                                {"role": "user", "content": summary_prompt}
                            ]
                        )
                    st.write("**ChatGPT's Summary:**", completion.choices[0].message.content)
                    shutil.rmtree(temp_path, ignore_errors=True)
            else:
                with open(tree, 'r', encoding='utf-8') as file:
                    json_data = file.read()
                    json_data = re.sub(r'"children": \[\]', ' ', json_data)  # Replace empty children with a space
                    json_data = re.sub(r'Required memory at 0x[0-9a-fA-F]+ is not valid \(process exited\?\)', '', json_data)  # Remove error message
                    json_data = re.sub(r'Required memory at 0x[0-9a-fA-F]+ is inaccessible \(swapped\)', '', json_data)  # Remove error message

                    cleaned_json_data = re.sub(r'\s+', ' ', json_data).strip()  # Replace all whitespace (newlines, tabs, spaces) with a single space

                    if prompt:
                        with st.spinner("Fetching response..."):
                            completion = client.chat.completions.create(
                                model=llm_option,
                                messages=[
                                    {"role": "user", "content": f"{cleaned_json_data}\n\n{prompt}"}
                             ]
                            )
                        st.write(f"**ChatGPT says:**", completion.choices[0].message.content)

        else:
            st.error("Please build a tree first.")


    else:
        st.error("Select a valid LLM.")
