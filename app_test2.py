import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
from gtts import gTTS
import pandas as pd
import base64
import json
from datetime import datetime, time

# --- Configuration ---
API_KEY = "AIzaSyBWACJwKQVwEwACVcoVANgYOXXinwuPNFw" 

try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash") 
except Exception as e:
    st.error(f"Failed to configure Gemini API: {e}")
    st.stop()

# --- Language Configuration ---
LANG_OPTIONS = {
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "Hindi (हिंदी)": "hi",
    "Telugu (తెలుగు)": "te",
    "Tamil (தமிழ்)": "ta",
    "Kannada (ಕನ್ನಡ)": "kn",
    "Marathi (मराठी)": "mr",
    "Bengali (বাংলা)": "bn"
}

# --- Enhanced Drug Interaction Database ---
DRUG_INTERACTIONS = {
    "Augmentin": {
        "interactions": {
            "Warfarin": {
                "severity": "🔴 Major",
                "type": "Drug-Drug Interaction",
                "effect": "Increased risk of bleeding",
                "recommendation": "Monitor INR levels closely. Consult doctor immediately."
            },
            "Alcohol": {
                "severity": "🟡 Moderate", 
                "type": "Drug-Food Interaction",
                "effect": "May reduce effectiveness and cause stomach upset",
                "recommendation": "Avoid alcohol during treatment period."
            }
        },
        "disease_interactions": {
            "Kidney Disease": "🟡 Use with caution - dose adjustment may be needed"
        }
    },
    "Eroflam": {
        "interactions": {
            "Aspirin": {
                "severity": "🟡 Moderate",
                "type": "Drug-Drug Interaction", 
                "effect": "Increased risk of gastric bleeding",
                "recommendation": "Take with food. Monitor for stomach pain."
            },
            "Alcohol": {
                "severity": "🔴 Major",
                "type": "Drug-Food Interaction",
                "effect": "Severe liver damage risk",
                "recommendation": "Strictly avoid alcohol consumption."
            }
        },
        "disease_interactions": {
            "High Blood Pressure": "🟡 May increase blood pressure in some patients"
        }
    },
    "Amoxicillin": {
        "interactions": {
            "Methotrexate": {
                "severity": "🔴 Major",
                "type": "Drug-Drug Interaction",
                "effect": "Increased methotrexate toxicity",
                "recommendation": "Avoid combination or monitor closely."
            }
        }
    }
}

def translate_text(text, target_lang):
    """Translate text to target language using Gemini."""
    if target_lang == "English":
        return text
    
    prompt = f"""
    Translate the following medical text to {target_lang}. 
    Keep medical terms accurate and clear.
    
    Text: {text}
    
    Return ONLY the translated text, nothing else.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except:
        return text

def check_drug_interactions_enhanced(extracted_medicines, target_lang="English"):
    """Enhanced drug interaction check with translation support."""
    
    # Generate report in English first
    report = "## Drug Interaction Safety Report\n\n"
    report += "### What Is a Drug Interaction Check?\n"
    report += "A drug interaction check analyzes whether medicines prescribed together might react in ways that could harm the patient, reduce effectiveness, or cause adverse side effects.\n\n"
    report += "---\n\n"
    
    drugs = [m.split('(')[0].strip().title() for m in extracted_medicines if m.strip()]
    
    if len(drugs) == 0:
        basic_report = report + "No medicines found for interaction check."
        return translate_text(basic_report, target_lang)
    
    report += f"### Medicines Being Checked: {', '.join(drugs)}\n\n"
    report += "---\n\n"
    
    interactions_found = []
    disease_warnings = []
    
    # Check interactions
    for i in range(len(drugs)):
        for j in range(i + 1, len(drugs)):
            drug1, drug2 = drugs[i], drugs[j]
            
            if drug1 in DRUG_INTERACTIONS and "interactions" in DRUG_INTERACTIONS[drug1]:
                if drug2 in DRUG_INTERACTIONS[drug1]["interactions"]:
                    interaction = DRUG_INTERACTIONS[drug1]["interactions"][drug2]
                    interactions_found.append({
                        "drug1": drug1,
                        "drug2": drug2,
                        "details": interaction
                    })
    
    for drug in drugs:
        if drug in DRUG_INTERACTIONS:
            if "interactions" in DRUG_INTERACTIONS[drug]:
                for substance, details in DRUG_INTERACTIONS[drug]["interactions"].items():
                    if substance not in drugs:
                        interactions_found.append({
                            "drug1": drug,
                            "drug2": substance,
                            "details": details
                        })
            
            if "disease_interactions" in DRUG_INTERACTIONS[drug]:
                for disease, warning in DRUG_INTERACTIONS[drug]["disease_interactions"].items():
                    disease_warnings.append({
                        "drug": drug,
                        "disease": disease,
                        "warning": warning
                    })
    
    if interactions_found:
        report += "### ⚠️ POTENTIAL INTERACTIONS FOUND\n\n"
        
        for idx, interaction in enumerate(interactions_found, 1):
            details = interaction["details"]
            report += f"**{idx}. {interaction['drug1']} ↔ {interaction['drug2']}**\n\n"
            report += f"- Severity: {details['severity']}\n"
            report += f"- Type: {details['type']}\n"
            report += f"- Effect: {details['effect']}\n"
            report += f"- Recommendation: {details['recommendation']}\n\n"
    else:
        report += "### ✅ No Known Drug-Drug Interactions\n\n"
        report += "No major flagged interactions found between the prescribed medicines.\n\n"
    
    if disease_warnings:
        report += "---\n\n### Drug-Disease Considerations\n\n"
        for warning in disease_warnings:
            report += f"**{warning['drug']}** - {warning['disease']}: {warning['warning']}\n\n"
    
    report += "---\n\n"
    report += "### Types of Drug Interactions\n\n"
    report += "1. **Drug-Drug Interaction**: Two medicines react with each other\n"
    report += "2. **Drug-Food Interaction**: Some foods affect medicine absorption\n"
    report += "3. **Drug-Disease Interaction**: A drug worsens an existing condition\n\n"
    report += "---\n\n"
    report += "### ⚠️ IMPORTANT\n\n"
    report += "This is a basic safety check. Always consult your doctor or pharmacist for comprehensive analysis.\n"
    
    # Translate the entire report
    return translate_text(report, target_lang)

def text_to_audio(text, lang='en'):
    """Converts text to speech in the selected language."""
    try:
        # Clean text for speech (remove markdown symbols)
        clean_text = text.replace('*', '').replace('#', '').replace('-', '').replace('|', '')
        clean_text = clean_text[:500]  # Limit length for audio
        
        gtts_lang = lang if lang in ['en', 'es', 'fr', 'hi', 'ta', 'bn', 'kn', 'mr', 'te'] else 'en'
        tts = gTTS(text=clean_text, lang=gtts_lang)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        
        audio_b64 = base64.b64encode(fp.read()).decode()
        audio_html = f'<audio autoplay controls src="data:audio/mp3;base64,{audio_b64}">Your browser does not support the audio element.</audio>'
        
        return audio_html
    except Exception as e:
        return f"Error in voice generation: {e}"

def parse_frequency_to_times(instructions):
    """Parse instructions and suggest appropriate times."""
    instructions_lower = instructions.lower()
    
    # Common patterns
    if "morning" in instructions_lower and "evening" in instructions_lower:
        return ["08:00", "20:00"]
    elif "three times" in instructions_lower or "3 times" in instructions_lower:
        return ["08:00", "14:00", "20:00"]
    elif "four times" in instructions_lower or "4 times" in instructions_lower:
        return ["08:00", "12:00", "16:00", "20:00"]
    elif "twice" in instructions_lower or "two times" in instructions_lower:
        return ["08:00", "20:00"]
    elif "night" in instructions_lower or "bedtime" in instructions_lower:
        return ["21:00"]
    elif "morning" in instructions_lower:
        return ["08:00"]
    else:
        return ["08:00"]

# --- Session State ---
if 'reminders' not in st.session_state:
    st.session_state.reminders = []
if 'extracted_medicines' not in st.session_state:
    st.session_state.extracted_medicines = {}
if 'extracted_text' not in st.session_state:
    st.session_state.extracted_text = None
if 'full_prescription' not in st.session_state:
    st.session_state.full_prescription = None
if 'interaction_report' not in st.session_state:
    st.session_state.interaction_report = None
if 'num_alarms' not in st.session_state:
    st.session_state.num_alarms = 1

# --- Main Application ---
def main():
    st.set_page_config(
        page_title="AI Smart Prescription Guide",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("💊 AI Smart Prescription Guide for Safer Healthcare")
    st.caption("Powered by Google Gemini and Streamlit")

    # --- Sidebar ---
    st.sidebar.header("⚙️ Settings & Features")
    
    selected_lang_name = st.sidebar.selectbox("🌐 Select Language for Output:", list(LANG_OPTIONS.keys()))
    target_lang_code = LANG_OPTIONS[selected_lang_name]

    voice_guidance_enabled = st.sidebar.checkbox("🔊 Enable Voice Guidance", value=True)

    st.sidebar.subheader("⏰ Set Medication Reminders")
    
    medicine_names = list(st.session_state.extracted_medicines.keys())
    
    if medicine_names:
        st.sidebar.markdown("**Step 1: Select Medicine**")
        selected_medicine = st.sidebar.selectbox(
            "Select medicine for reminder:", 
            options=["-- Select Medicine --"] + medicine_names,
            key="reminder_med_select"
        )
        
        if selected_medicine and selected_medicine != "-- Select Medicine --":
            med_data = st.session_state.extracted_medicines[selected_medicine]
            
            st.sidebar.markdown("**Step 2: Set Alarm Times**")
            
            # Get suggested times from instructions
            instructions = med_data.get('Frequency/Instructions', '')
            suggested_times = parse_frequency_to_times(instructions)
            
            # Number of alarms selector
            num_alarms = st.sidebar.number_input(
                "Number of alarms per day:",
                min_value=1,
                max_value=4,
                value=len(suggested_times),
                key="num_alarms_input"
            )
            
            alarm_times = []
            for i in range(num_alarms):
                default_time_str = suggested_times[i] if i < len(suggested_times) else "08:00"
                hour, minute = map(int, default_time_str.split(':'))
                
                col1, col2 = st.sidebar.columns(2)
                with col1:
                    alarm_hour = st.number_input(
                        f"Alarm {i+1} - Hour:",
                        min_value=0,
                        max_value=23,
                        value=hour,
                        key=f"hour_{selected_medicine}_{i}"
                    )
                with col2:
                    alarm_minute = st.number_input(
                        f"Minute:",
                        min_value=0,
                        max_value=59,
                        value=minute,
                        key=f"minute_{selected_medicine}_{i}"
                    )
                
                alarm_times.append(f"{alarm_hour:02d}:{alarm_minute:02d}")
            
            st.sidebar.markdown("**Step 3: Additional Notes**")
            additional_notes = st.sidebar.text_input(
                "Notes (optional):",
                value=med_data.get('Frequency/Instructions', '')[:50],
                key="notes_input"
            )
            
            final_reminder = f"{selected_medicine} | {', '.join(alarm_times)} | {additional_notes}"
            
            if st.sidebar.button("🔔 Add Reminder with Alarm"):
                if final_reminder not in st.session_state.reminders:
                    st.session_state.reminders.append(final_reminder)
                    st.sidebar.success(f"✅ Reminder added with {len(alarm_times)} alarm(s)!")
                else:
                    st.sidebar.warning("⚠️ This reminder already exists.")
    else:
        st.sidebar.info("📋 Upload and analyze a prescription first to enable reminders.")

    st.sidebar.markdown("---")
    
    if st.session_state.reminders:
        st.sidebar.subheader("📱 Active Reminders")
        for idx, reminder in enumerate(st.session_state.reminders):
            col1, col2 = st.sidebar.columns([5, 1])
            with col1:
                st.sidebar.text(f"{idx+1}. {reminder}")
            with col2:
                if st.sidebar.button("❌", key=f"del_{idx}"):
                    st.session_state.reminders.pop(idx)
                    st.rerun()

    st.markdown("---")
    
    # --- Main Content ---
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("1. Upload Prescription Image")
        uploaded_file = st.file_uploader("Choose a prescription image", type=["png", "jpg", "jpeg"])
        
        image = None
        if uploaded_file is not None:
            try:
                image = Image.open(uploaded_file)
                st.image(image, caption='Uploaded Prescription', use_container_width=True) 
            except Exception as e:
                st.error(f"Error loading image: {e}")
    
    with col2:
        st.subheader("2. Analyze Prescription")
        if image is not None:
            
            extraction_prompt = f"""
            You are an expert medical prescription analyzer and translator.
            
            TASK 1: Extract ALL information from this prescription image including:
            - Patient Name
            - Patient Age and Sex
            - Date
            - Doctor's Name and License Number
            - ALL Medicine Names (with brand names in parentheses if available)
            - Dosage Details for each medicine (strength, form like tablet/capsule)
            - Frequency and Instructions for each medicine (timing, duration, special instructions)
            - Any additional notes or warnings
            
            TASK 2: Translate ALL extracted information to {selected_lang_name} language.
            Keep medicine brand names in English but translate descriptions.
            
            Return valid JSON in this exact format:
            {{
                "patient_info": {{
                    "name": "patient name in {selected_lang_name}",
                    "age": "age",
                    "sex": "sex in {selected_lang_name}",
                    "date": "date"
                }},
                "doctor_info": {{
                    "name": "doctor name",
                    "license": "license number"
                }},
                "prescription": [
                    {{
                        "Medicine Name": "medicine name (keep brand in English)",
                        "Dosage Details": "dosage in {selected_lang_name}",
                        "Frequency/Instructions": "instructions in {selected_lang_name}"
                    }}
                ]
            }}
            
            Return ONLY valid JSON, no other text.
            """
            
            if st.button("🔍 Extract and Analyze"):
                for key in list(st.session_state.keys()):
                    if key.startswith('hour_') or key.startswith('minute_'):
                        del st.session_state[key]
                        
                with st.spinner(f"Analyzing and translating to {selected_lang_name}..."):
                    try:
                        try:
                            response = model.generate_content(
                                [extraction_prompt, image],
                                generation_config=genai.GenerationConfig(
                                    response_mime_type="application/json"
                                )
                            )
                        except:
                            response = model.generate_content([extraction_prompt, image])
                        
                        json_str = response.text.strip().replace('```json', '').replace('```', '').strip()
                        data = json.loads(json_str)
                        
                        # Build full prescription display
                        full_text = ""
                        
                        # Patient Info
                        patient = data.get('patient_info', {})
                        if patient:
                            full_text += f"**👤 Patient Information:**\n"
                            full_text += f"- Name: {patient.get('name', 'N/A')}\n"
                            full_text += f"- Age: {patient.get('age', 'N/A')}\n"
                            full_text += f"- Sex: {patient.get('sex', 'N/A')}\n"
                            full_text += f"- Date: {patient.get('date', 'N/A')}\n\n"
                        
                        # Doctor Info
                        doctor = data.get('doctor_info', {})
                        if doctor:
                            full_text += f"**👨‍⚕️ Doctor Information:**\n"
                            full_text += f"- Name: {doctor.get('name', 'N/A')}\n"
                            full_text += f"- License: {doctor.get('license', 'N/A')}\n\n"
                        
                        full_text += "---\n\n**💊 Prescribed Medicines:**\n\n"
                        
                        md_text = ""
                        extracted_med_map = {} 
                        medicine_names_only = []
                        
                        for idx, item in enumerate(data.get('prescription', []), 1):
                            med_name = item.get('Medicine Name', 'N/A')
                            dosage = item.get('Dosage Details', 'N/A')
                            instructions = item.get('Frequency/Instructions', 'N/A')

                            md_text += f"**{idx}. {med_name}**\n"
                            md_text += f"   - **Dosage:** {dosage}\n"
                            md_text += f"   - **Instructions:** {instructions}\n\n"
                            
                            extracted_med_map[med_name] = item
                            
                            # Extract English name for interaction check
                            english_name = med_name.split('(')[0].strip().title()
                            medicine_names_only.append(english_name)

                        full_text += md_text
                        
                        st.session_state.full_prescription = full_text
                        st.session_state.extracted_text = md_text
                        st.session_state.extracted_medicines = extracted_med_map

                        # Generate interaction report in selected language
                        interaction_report = check_drug_interactions_enhanced(
                            medicine_names_only, 
                            selected_lang_name
                        )
                        st.session_state.interaction_report = interaction_report

                        st.success("✅ Analysis Complete!")
                        
                    except Exception as e:
                        st.error(f"Error: {e}")
                        st.info("💡 Tip: pip install --upgrade google-generativeai")
    
    st.markdown("---")

    # --- Results ---
    if st.session_state.full_prescription:
        col3, col4 = st.columns(2)
        
        with col3:
            st.subheader(f"3. Complete Prescription ({selected_lang_name})")
            st.markdown(st.session_state.full_prescription)

            if voice_guidance_enabled:
                st.markdown("##### 🔊 Voice Guidance")
                audio_html = text_to_audio(st.session_state.full_prescription, lang=target_lang_code)
                st.markdown(audio_html, unsafe_allow_html=True)

        with col4:
            st.subheader("4. Drug Interaction Safety Report")
            if st.session_state.interaction_report:
                st.markdown(st.session_state.interaction_report)
                
                if voice_guidance_enabled:
                    st.markdown("##### 🔊 Safety Alert")
                    audio_html = text_to_audio(st.session_state.interaction_report, lang=target_lang_code)
                    st.markdown(audio_html, unsafe_allow_html=True)


if __name__ == "__main__":
    main()