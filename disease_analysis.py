import streamlit as st
from openai import OpenAI
import json
import pandas as pd

# Replace "your_api_key_here" with your actual OpenAI API key
client = OpenAI(api_key="your_api_key_here")

# Caching the function to prevent repeated API calls for the same input
@st.cache_data
def get_disease_info(disease_name):
    """
    Function to query OpenAI and return structured information about a disease.
    """
    medication_format = '''"name":""
    "side_effects":[
    0:""
    1:""
    ...
    ]
    "dosage":""'''
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"Please provide information on the following aspects for {disease_name}: 1. Key Statistics, 2. Recovery Options, 3. Recommended Medications. Format the response in JSON with keys for 'name', 'statistics', 'total_cases' (this always has to be a number), 'recovery_rate' (this always has to be a percentage), 'mortality_rate' (this always has to be a percentage) 'recovery_options', (explain each recovery option in detail), and 'medication', (give some side effect examples and dosages) always use this json format for medication : {medication_format} ."}
        ]
    )
    return response.choices[0].message.content

def display_disease_info(disease_info):
    """
    Function to display the disease information in a structured way using Streamlit.
    """
    try:
        info = json.loads(disease_info)

        st.write(f"## Statistics for {info['name']}")

        col1, col2 = st.columns(2)

        with col1:
            st.metric(label="Total Cases", value=info['statistics']['total_cases'])
            st.metric(label="Recovery Rate", value=info['statistics']['recovery_rate'])
            st.metric(label="Mortality Rate", value=info['statistics']['mortality_rate'])

        with col2:
            recovery_rate = float(info['statistics']["recovery_rate"].strip('%'))
            mortality_rate = float(info['statistics']["mortality_rate"].strip('%'))

            chart_data = pd.DataFrame(
                {
                    "Recovery Rate": [recovery_rate],
                    "Mortality Rate": [mortality_rate],
                },
                index = ["Rate"]  # This is a single index. You might adjust it based on your data structure.
            )
            st.bar_chart(chart_data)

        st.write("## Recovery Options")
        recovery_options = info['recovery_options']
        for option, description in recovery_options.items():
            st.subheader(option)
            st.write(description)

        st.write("## Medication")
        medication = info['medication']
        medication_count = 1
        for option, description in medication.items():
            st.subheader(f"{medication_count}. {option}")
            st.write(description)
            medication_count += 1


    except json.JSONDecodeError:
        st.error("Failed to decode the response into JSON. Please check the format of the OpenAI response.")
        st.write("### Raw Response:")
        st.write(disease_info)  # Print the raw response for debugging purposes

def get_diagnosis(symptoms):
    """
    Function to query OpenAI for possible diagnoses based on symptoms.
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"Based on the following symptoms: {symptoms}, suggest possible diagnoses. Provide a list of potential diseases with a brief description for each."}
        ]
    )
    return response.choices[0].message.content

def get_health_tips(disease_name):
    """
    Function to query OpenAI for health tips and preventative measures for a disease.
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"Provide health tips and preventative measures for managing or preventing {disease_name}."}
        ]
    )
    return response.choices[0].message.content

def get_risk_assessment(age, gender, habits, disease_name):
    """
    Function to query OpenAI for a risk assessment based on personal data.
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": f"Based on the following data: age {age}, gender {gender}, habits {habits}, assess the risk for {disease_name} and provide a brief explanation."}
        ]
    )
    return response.choices[0].message.content

# Streamlit App Layout
st.title("Disease Information Dashboard")

# Symptom-based Diagnosis Suggestions
st.write("## Symptom-based Diagnosis Suggestions")
symptoms = st.text_area("Enter your symptoms:")
if symptoms:
    diagnosis_info = get_diagnosis(symptoms)
    st.write("### Possible Diagnoses")
    st.write(diagnosis_info)

# Adding a selectbox for common diseases for user convenience
st.write("## Disease Information")
common_diseases = ["Cold", "Hypertension", "HIV", "AIDS", "COVID-19", "Influenza", "Cancer"]
disease_name = st.text_input("Enter the name of the disease:", value="").capitalize()
disease_name = st.selectbox("Or select a common disease:", common_diseases) if disease_name == "" else disease_name

# Disease Information Display
if disease_name:
    disease_info = get_disease_info(disease_name)
    display_disease_info(disease_info)

    # Health tips and Preventative Measures
    st.write("### Health Tips and Preventative Measures")
    tips = get_health_tips(disease_name)
    st.write(tips)

# Risk Factor Assessment
st.write("## Risk Factor Assessment")
age = st.number_input("Enter your age:", min_value=0)
gender = st.selectbox("Select your gender:", ["Male", "Female", "Other"])
habits = st.text_area("Describe your lifestyle habits (e.g. smoking, exercise, diet):")

if st.button("Assess Risk"):
    risk_info = get_risk_assessment(age, gender, habits, disease_name)
    st.write("### Risk Assessment")
    st.write(risk_info)

# Disease Comparison Tool
st.write("## Disease Comparison Tool")
diseases_input = st.text_area("Enter the names of diseases to compare (separate each disease with a comma):")
if diseases_input:
    # Split input by comma and process each disease
    diseases_list = [disease.strip().capitalize() for disease in diseases_input.split(',')]
    for disease in diseases_list:
        if disease:  # Ensure that the disease name is not empty
            st.write(f"### Information for {disease}")
            comparison_info = get_disease_info(disease)
            display_disease_info(comparison_info)
        else:
            st.error("One or more disease names were not valid.")
