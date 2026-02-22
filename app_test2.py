# import streamlit as st
# import google.generativeai as genai
# from PIL import Image
# import io
# from gtts import gTTS
# import pandas as pd
# import base64
# import json
# from datetime import datetime, time

# # --- Configuration ---
# API_KEY = "AIzaSyBWACJwKQVwEwACVcoVANgYOXXinwuPNFw" 

# try:
#     genai.configure(api_key=API_KEY)
#     model = genai.GenerativeModel("gemini-2.5-flash") 
# except Exception as e:
#     st.error(f"Failed to configure Gemini API: {e}")
#     st.stop()

# # --- Language Configuration ---
# LANG_OPTIONS = {
#     "English": "en",
#     "Spanish": "es",
#     "French": "fr",
#     "Hindi (हिंदी)": "hi",
#     "Telugu (తెలుగు)": "te",
#     "Tamil (தமிழ்)": "ta",
#     "Kannada (ಕನ್ನಡ)": "kn",
#     "Marathi (मराठी)": "mr",
#     "Bengali (বাংলা)": "bn"
# }

# # --- Enhanced Drug Interaction Database ---
# DRUG_INTERACTIONS = {
#     "Augmentin": {
#         "interactions": {
#             "Warfarin": {
#                 "severity": "🔴 Major",
#                 "type": "Drug-Drug Interaction",
#                 "effect": "Increased risk of bleeding",
#                 "recommendation": "Monitor INR levels closely. Consult doctor immediately."
#             },
#             "Alcohol": {
#                 "severity": "🟡 Moderate", 
#                 "type": "Drug-Food Interaction",
#                 "effect": "May reduce effectiveness and cause stomach upset",
#                 "recommendation": "Avoid alcohol during treatment period."
#             }
#         },
#         "disease_interactions": {
#             "Kidney Disease": "🟡 Use with caution - dose adjustment may be needed"
#         }
#     },
#     "Eroflam": {
#         "interactions": {
#             "Aspirin": {
#                 "severity": "🟡 Moderate",
#                 "type": "Drug-Drug Interaction", 
#                 "effect": "Increased risk of gastric bleeding",
#                 "recommendation": "Take with food. Monitor for stomach pain."
#             },
#             "Alcohol": {
#                 "severity": "🔴 Major",
#                 "type": "Drug-Food Interaction",
#                 "effect": "Severe liver damage risk",
#                 "recommendation": "Strictly avoid alcohol consumption."
#             }
#         },
#         "disease_interactions": {
#             "High Blood Pressure": "🟡 May increase blood pressure in some patients"
#         }
#     },
#     "Amoxicillin": {
#         "interactions": {
#             "Methotrexate": {
#                 "severity": "🔴 Major",
#                 "type": "Drug-Drug Interaction",
#                 "effect": "Increased methotrexate toxicity",
#                 "recommendation": "Avoid combination or monitor closely."
#             }
#         }
#     }
# }

# def translate_text(text, target_lang):
#     """Translate text to target language using Gemini."""
#     if target_lang == "English":
#         return text
    
#     prompt = f"""
#     Translate the following medical text to {target_lang}. 
#     Keep medical terms accurate and clear.
    
#     Text: {text}
    
#     Return ONLY the translated text, nothing else.
#     """
    
#     try:
#         response = model.generate_content(prompt)
#         return response.text.strip()
#     except:
#         return text

# def check_drug_interactions_enhanced(extracted_medicines, target_lang="English"):
#     """Enhanced drug interaction check with translation support."""
    
#     # Generate report in English first
#     report = "## Drug Interaction Safety Report\n\n"
#     report += "### What Is a Drug Interaction Check?\n"
#     report += "A drug interaction check analyzes whether medicines prescribed together might react in ways that could harm the patient, reduce effectiveness, or cause adverse side effects.\n\n"
#     report += "---\n\n"
    
#     drugs = [m.split('(')[0].strip().title() for m in extracted_medicines if m.strip()]
    
#     if len(drugs) == 0:
#         basic_report = report + "No medicines found for interaction check."
#         return translate_text(basic_report, target_lang)
    
#     report += f"### Medicines Being Checked: {', '.join(drugs)}\n\n"
#     report += "---\n\n"
    
#     interactions_found = []
#     disease_warnings = []
    
#     # Check interactions
#     for i in range(len(drugs)):
#         for j in range(i + 1, len(drugs)):
#             drug1, drug2 = drugs[i], drugs[j]
            
#             if drug1 in DRUG_INTERACTIONS and "interactions" in DRUG_INTERACTIONS[drug1]:
#                 if drug2 in DRUG_INTERACTIONS[drug1]["interactions"]:
#                     interaction = DRUG_INTERACTIONS[drug1]["interactions"][drug2]
#                     interactions_found.append({
#                         "drug1": drug1,
#                         "drug2": drug2,
#                         "details": interaction
#                     })
    
#     for drug in drugs:
#         if drug in DRUG_INTERACTIONS:
#             if "interactions" in DRUG_INTERACTIONS[drug]:
#                 for substance, details in DRUG_INTERACTIONS[drug]["interactions"].items():
#                     if substance not in drugs:
#                         interactions_found.append({
#                             "drug1": drug,
#                             "drug2": substance,
#                             "details": details
#                         })
            
#             if "disease_interactions" in DRUG_INTERACTIONS[drug]:
#                 for disease, warning in DRUG_INTERACTIONS[drug]["disease_interactions"].items():
#                     disease_warnings.append({
#                         "drug": drug,
#                         "disease": disease,
#                         "warning": warning
#                     })
    
#     if interactions_found:
#         report += "### ⚠️ POTENTIAL INTERACTIONS FOUND\n\n"
        
#         for idx, interaction in enumerate(interactions_found, 1):
#             details = interaction["details"]
#             report += f"**{idx}. {interaction['drug1']} ↔ {interaction['drug2']}**\n\n"
#             report += f"- Severity: {details['severity']}\n"
#             report += f"- Type: {details['type']}\n"
#             report += f"- Effect: {details['effect']}\n"
#             report += f"- Recommendation: {details['recommendation']}\n\n"
#     else:
#         report += "### ✅ No Known Drug-Drug Interactions\n\n"
#         report += "No major flagged interactions found between the prescribed medicines.\n\n"
    
#     if disease_warnings:
#         report += "---\n\n### Drug-Disease Considerations\n\n"
#         for warning in disease_warnings:
#             report += f"**{warning['drug']}** - {warning['disease']}: {warning['warning']}\n\n"
    
#     report += "---\n\n"
#     report += "### Types of Drug Interactions\n\n"
#     report += "1. **Drug-Drug Interaction**: Two medicines react with each other\n"
#     report += "2. **Drug-Food Interaction**: Some foods affect medicine absorption\n"
#     report += "3. **Drug-Disease Interaction**: A drug worsens an existing condition\n\n"
#     report += "---\n\n"
#     report += "### ⚠️ IMPORTANT\n\n"
#     report += "This is a basic safety check. Always consult your doctor or pharmacist for comprehensive analysis.\n"
    
#     # Translate the entire report
#     return translate_text(report, target_lang)

# def text_to_audio(text, lang='en'):
#     """Converts text to speech in the selected language."""
#     try:
#         # Clean text for speech (remove markdown symbols)
#         clean_text = text.replace('*', '').replace('#', '').replace('-', '').replace('|', '')
#         clean_text = clean_text[:500]  # Limit length for audio
        
#         gtts_lang = lang if lang in ['en', 'es', 'fr', 'hi', 'ta', 'bn', 'kn', 'mr', 'te'] else 'en'
#         tts = gTTS(text=clean_text, lang=gtts_lang)
#         fp = io.BytesIO()
#         tts.write_to_fp(fp)
#         fp.seek(0)
        
#         audio_b64 = base64.b64encode(fp.read()).decode()
#         audio_html = f'<audio autoplay controls src="data:audio/mp3;base64,{audio_b64}">Your browser does not support the audio element.</audio>'
        
#         return audio_html
#     except Exception as e:
#         return f"Error in voice generation: {e}"

# def parse_frequency_to_times(instructions):
#     """Parse instructions and suggest appropriate times."""
#     instructions_lower = instructions.lower()
    
#     # Common patterns
#     if "morning" in instructions_lower and "evening" in instructions_lower:
#         return ["08:00", "20:00"]
#     elif "three times" in instructions_lower or "3 times" in instructions_lower:
#         return ["08:00", "14:00", "20:00"]
#     elif "four times" in instructions_lower or "4 times" in instructions_lower:
#         return ["08:00", "12:00", "16:00", "20:00"]
#     elif "twice" in instructions_lower or "two times" in instructions_lower:
#         return ["08:00", "20:00"]
#     elif "night" in instructions_lower or "bedtime" in instructions_lower:
#         return ["21:00"]
#     elif "morning" in instructions_lower:
#         return ["08:00"]
#     else:
#         return ["08:00"]

# # --- Session State ---
# if 'reminders' not in st.session_state:
#     st.session_state.reminders = []
# if 'extracted_medicines' not in st.session_state:
#     st.session_state.extracted_medicines = {}
# if 'extracted_text' not in st.session_state:
#     st.session_state.extracted_text = None
# if 'full_prescription' not in st.session_state:
#     st.session_state.full_prescription = None
# if 'interaction_report' not in st.session_state:
#     st.session_state.interaction_report = None
# if 'num_alarms' not in st.session_state:
#     st.session_state.num_alarms = 1

# # --- Main Application ---
# def main():
#     st.set_page_config(
#         page_title="AI Smart Prescription Guide",
#         layout="wide",
#         initial_sidebar_state="expanded"
#     )

#     st.title("💊 AI Smart Prescription Guide for Safer Healthcare")
#     st.caption("Powered by Google Gemini and Streamlit")

#     # --- Sidebar ---
#     st.sidebar.header("⚙️ Settings & Features")
    
#     selected_lang_name = st.sidebar.selectbox("🌐 Select Language for Output:", list(LANG_OPTIONS.keys()))
#     target_lang_code = LANG_OPTIONS[selected_lang_name]

#     voice_guidance_enabled = st.sidebar.checkbox("🔊 Enable Voice Guidance", value=True)

#     st.sidebar.subheader("⏰ Set Medication Reminders")
    
#     medicine_names = list(st.session_state.extracted_medicines.keys())
    
#     if medicine_names:
#         st.sidebar.markdown("**Step 1: Select Medicine**")
#         selected_medicine = st.sidebar.selectbox(
#             "Select medicine for reminder:", 
#             options=["-- Select Medicine --"] + medicine_names,
#             key="reminder_med_select"
#         )
        
#         if selected_medicine and selected_medicine != "-- Select Medicine --":
#             med_data = st.session_state.extracted_medicines[selected_medicine]
            
#             st.sidebar.markdown("**Step 2: Set Alarm Times**")
            
#             # Get suggested times from instructions
#             instructions = med_data.get('Frequency/Instructions', '')
#             suggested_times = parse_frequency_to_times(instructions)
            
#             # Number of alarms selector
#             num_alarms = st.sidebar.number_input(
#                 "Number of alarms per day:",
#                 min_value=1,
#                 max_value=4,
#                 value=len(suggested_times),
#                 key="num_alarms_input"
#             )
            
#             alarm_times = []
#             for i in range(num_alarms):
#                 default_time_str = suggested_times[i] if i < len(suggested_times) else "08:00"
#                 hour, minute = map(int, default_time_str.split(':'))
                
#                 col1, col2 = st.sidebar.columns(2)
#                 with col1:
#                     alarm_hour = st.number_input(
#                         f"Alarm {i+1} - Hour:",
#                         min_value=0,
#                         max_value=23,
#                         value=hour,
#                         key=f"hour_{selected_medicine}_{i}"
#                     )
#                 with col2:
#                     alarm_minute = st.number_input(
#                         f"Minute:",
#                         min_value=0,
#                         max_value=59,
#                         value=minute,
#                         key=f"minute_{selected_medicine}_{i}"
#                     )
                
#                 alarm_times.append(f"{alarm_hour:02d}:{alarm_minute:02d}")
            
#             st.sidebar.markdown("**Step 3: Additional Notes**")
#             additional_notes = st.sidebar.text_input(
#                 "Notes (optional):",
#                 value=med_data.get('Frequency/Instructions', '')[:50],
#                 key="notes_input"
#             )
            
#             final_reminder = f"{selected_medicine} | {', '.join(alarm_times)} | {additional_notes}"
            
#             if st.sidebar.button("🔔 Add Reminder with Alarm"):
#                 if final_reminder not in st.session_state.reminders:
#                     st.session_state.reminders.append(final_reminder)
#                     st.sidebar.success(f"✅ Reminder added with {len(alarm_times)} alarm(s)!")
#                 else:
#                     st.sidebar.warning("⚠️ This reminder already exists.")
#     else:
#         st.sidebar.info("📋 Upload and analyze a prescription first to enable reminders.")

#     st.sidebar.markdown("---")
    
#     if st.session_state.reminders:
#         st.sidebar.subheader("📱 Active Reminders")
#         for idx, reminder in enumerate(st.session_state.reminders):
#             col1, col2 = st.sidebar.columns([5, 1])
#             with col1:
#                 st.sidebar.text(f"{idx+1}. {reminder}")
#             with col2:
#                 if st.sidebar.button("❌", key=f"del_{idx}"):
#                     st.session_state.reminders.pop(idx)
#                     st.rerun()

#     st.markdown("---")
    
#     # --- Main Content ---
#     col1, col2 = st.columns([1, 1])

#     with col1:
#         st.subheader("1. Upload Prescription Image")
#         uploaded_file = st.file_uploader("Choose a prescription image", type=["png", "jpg", "jpeg"])
        
#         image = None
#         if uploaded_file is not None:
#             try:
#                 image = Image.open(uploaded_file)
#                 st.image(image, caption='Uploaded Prescription', use_container_width=True) 
#             except Exception as e:
#                 st.error(f"Error loading image: {e}")
    
#     with col2:
#         st.subheader("2. Analyze Prescription")
#         if image is not None:
            
#             extraction_prompt = f"""
#             You are an expert medical prescription analyzer and translator.
            
#             TASK 1: Extract ALL information from this prescription image including:
#             - Patient Name
#             - Patient Age and Sex
#             - Date
#             - Doctor's Name and License Number
#             - ALL Medicine Names (with brand names in parentheses if available)
#             - Dosage Details for each medicine (strength, form like tablet/capsule)
#             - Frequency and Instructions for each medicine (timing, duration, special instructions)
#             - Any additional notes or warnings
            
#             TASK 2: Translate ALL extracted information to {selected_lang_name} language.
#             Keep medicine brand names in English but translate descriptions.
            
#             Return valid JSON in this exact format:
#             {{
#                 "patient_info": {{
#                     "name": "patient name in {selected_lang_name}",
#                     "age": "age",
#                     "sex": "sex in {selected_lang_name}",
#                     "date": "date"
#                 }},
#                 "doctor_info": {{
#                     "name": "doctor name",
#                     "license": "license number"
#                 }},
#                 "prescription": [
#                     {{
#                         "Medicine Name": "medicine name (keep brand in English)",
#                         "Dosage Details": "dosage in {selected_lang_name}",
#                         "Frequency/Instructions": "instructions in {selected_lang_name}"
#                     }}
#                 ]
#             }}
            
#             Return ONLY valid JSON, no other text.
#             """
            
#             if st.button("🔍 Extract and Analyze"):
#                 for key in list(st.session_state.keys()):
#                     if key.startswith('hour_') or key.startswith('minute_'):
#                         del st.session_state[key]
                        
#                 with st.spinner(f"Analyzing and translating to {selected_lang_name}..."):
#                     try:
#                         try:
#                             response = model.generate_content(
#                                 [extraction_prompt, image],
#                                 generation_config=genai.GenerationConfig(
#                                     response_mime_type="application/json"
#                                 )
#                             )
#                         except:
#                             response = model.generate_content([extraction_prompt, image])
                        
#                         json_str = response.text.strip().replace('```json', '').replace('```', '').strip()
#                         data = json.loads(json_str)
                        
#                         # Build full prescription display
#                         full_text = ""
                        
#                         # Patient Info
#                         patient = data.get('patient_info', {})
#                         if patient:
#                             full_text += f"**👤 Patient Information:**\n"
#                             full_text += f"- Name: {patient.get('name', 'N/A')}\n"
#                             full_text += f"- Age: {patient.get('age', 'N/A')}\n"
#                             full_text += f"- Sex: {patient.get('sex', 'N/A')}\n"
#                             full_text += f"- Date: {patient.get('date', 'N/A')}\n\n"
                        
#                         # Doctor Info
#                         doctor = data.get('doctor_info', {})
#                         if doctor:
#                             full_text += f"**👨‍⚕️ Doctor Information:**\n"
#                             full_text += f"- Name: {doctor.get('name', 'N/A')}\n"
#                             full_text += f"- License: {doctor.get('license', 'N/A')}\n\n"
                        
#                         full_text += "---\n\n**💊 Prescribed Medicines:**\n\n"
                        
#                         md_text = ""
#                         extracted_med_map = {} 
#                         medicine_names_only = []
                        
#                         for idx, item in enumerate(data.get('prescription', []), 1):
#                             med_name = item.get('Medicine Name', 'N/A')
#                             dosage = item.get('Dosage Details', 'N/A')
#                             instructions = item.get('Frequency/Instructions', 'N/A')

#                             md_text += f"**{idx}. {med_name}**\n"
#                             md_text += f"   - **Dosage:** {dosage}\n"
#                             md_text += f"   - **Instructions:** {instructions}\n\n"
                            
#                             extracted_med_map[med_name] = item
                            
#                             # Extract English name for interaction check
#                             english_name = med_name.split('(')[0].strip().title()
#                             medicine_names_only.append(english_name)

#                         full_text += md_text
                        
#                         st.session_state.full_prescription = full_text
#                         st.session_state.extracted_text = md_text
#                         st.session_state.extracted_medicines = extracted_med_map

#                         # Generate interaction report in selected language
#                         interaction_report = check_drug_interactions_enhanced(
#                             medicine_names_only, 
#                             selected_lang_name
#                         )
#                         st.session_state.interaction_report = interaction_report

#                         st.success("✅ Analysis Complete!")
                        
#                     except Exception as e:
#                         st.error(f"Error: {e}")
#                         st.info("💡 Tip: pip install --upgrade google-generativeai")
    
#     st.markdown("---")

#     # --- Results ---
#     if st.session_state.full_prescription:
#         col3, col4 = st.columns(2)
        
#         with col3:
#             st.subheader(f"3. Complete Prescription ({selected_lang_name})")
#             st.markdown(st.session_state.full_prescription)

#             if voice_guidance_enabled:
#                 st.markdown("##### 🔊 Voice Guidance")
#                 audio_html = text_to_audio(st.session_state.full_prescription, lang=target_lang_code)
#                 st.markdown(audio_html, unsafe_allow_html=True)

#         with col4:
#             st.subheader("4. Drug Interaction Safety Report")
#             if st.session_state.interaction_report:
#                 st.markdown(st.session_state.interaction_report)
                
#                 if voice_guidance_enabled:
#                     st.markdown("##### 🔊 Safety Alert")
#                     audio_html = text_to_audio(st.session_state.interaction_report, lang=target_lang_code)
#                     st.markdown(audio_html, unsafe_allow_html=True)


# if __name__ == "__main__":
#     main()


import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
from gtts import gTTS
import base64
import json

# --- Configuration ---
API_KEY = "AIzaSyC2bb5Tcy8Lns7PXQgqAYFi8gAc3D6ppKg"

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

LANG_PLAIN_NAME = {
    "English": "English",
    "Spanish": "Spanish",
    "French": "French",
    "Hindi (हिंदी)": "Hindi",
    "Telugu (తెలుగు)": "Telugu",
    "Tamil (தமிழ்)": "Tamil",
    "Kannada (ಕನ್ನಡ)": "Kannada",
    "Marathi (मराठी)": "Marathi",
    "Bengali (বাংলা)": "Bengali"
}


# -----------------------------------------------------------------------
# CORE: Get medicine info AND translate in ONE single Gemini call
# -----------------------------------------------------------------------
def get_medicine_info_from_gemini(medicine_name, all_medicines, patient_allergies, target_lang):
    """
    Single Gemini API call that:
    1. Analyzes the medicine clinically
    2. Returns ALL text already in the target language
    
    This avoids multiple translation calls that fail silently.
    """
    other_medicines = [m for m in all_medicines if m.lower() != medicine_name.lower()]
    other_meds_str = ", ".join(other_medicines) if other_medicines else "None"

    # Tell Gemini exactly what language to write in
    if target_lang == "English":
        lang_instruction = "Write ALL text values in English."
    else:
        lang_instruction = (
            f"IMPORTANT: Write ALL text values (usage, side_effects, general_warnings, "
            f"interaction notes, allergy message, overall_interaction_summary) in {target_lang} language. "
            f"You MUST use {target_lang} script. Do NOT write in English for these fields. "
            f"Only keep medicine brand/generic names and drug_class in English."
        )

    prompt = f"""You are an expert clinical pharmacist.

Medicine: {medicine_name}
Other medicines in same prescription: {other_meds_str}
Patient allergies: {patient_allergies or "None"}

{lang_instruction}

Return ONLY this valid JSON, no markdown, no extra text:
{{
  "usage": [
    "first use or condition treated — in {target_lang}",
    "mechanism of action — in {target_lang}",
    "another key benefit — in {target_lang}"
  ],
  "side_effects": [
    "side effect 1 in {target_lang}",
    "side effect 2 in {target_lang}",
    "side effect 3 in {target_lang}",
    "side effect 4 in {target_lang}"
  ],
  "drug_class": "pharmacological class in English only",
  "interaction_with_prescribed": [
    {{
      "medicine": "other medicine name in English",
      "safe": true,
      "note": "interaction note in {target_lang}"
    }}
  ],
  "general_warnings": [
    "warning 1 in {target_lang}",
    "warning 2 in {target_lang}"
  ],
  "allergy_alert": {{
    "triggered": false,
    "message": "allergy message in {target_lang} if triggered, else empty string"
  }},
  "overall_interaction_summary": "one line summary in {target_lang}"
}}

Rules:
- Set allergy_alert.triggered = true ONLY if patient allergy matches drug class of {medicine_name}
- Set safe = false if known moderate or major interaction exists
- Return ONLY valid JSON"""

    fallback = {
        "usage": ["Information not available"],
        "side_effects": ["Information not available"],
        "drug_class": "Unknown",
        "interaction_with_prescribed": [],
        "general_warnings": [],
        "allergy_alert": {"triggered": False, "message": ""},
        "overall_interaction_summary": "Could not retrieve data."
    }

    try:
        response = model.generate_content(prompt)
        json_str = response.text.strip()
        # Clean any markdown wrapping
        json_str = json_str.replace("```json", "").replace("```", "").strip()
        # Sometimes Gemini adds text before/after JSON — extract just the JSON object
        start = json_str.find("{")
        end = json_str.rfind("}") + 1
        if start != -1 and end > start:
            json_str = json_str[start:end]
        return json.loads(json_str)
    except Exception as e:
        return fallback


# -----------------------------------------------------------------------
# Translate dosage fields — single call for all fields at once
# -----------------------------------------------------------------------
def translate_dosage_fields(prescription_list, target_lang):
    """
    Translates Frequency/Instructions and Dosage Details for all medicines
    in a SINGLE Gemini call instead of one call per field.
    """
    if target_lang == "English":
        return prescription_list

    # Build a numbered list of all fields to translate
    items_to_translate = []
    for i, item in enumerate(prescription_list):
        freq = item.get("Frequency/Instructions", "")
        dosage = item.get("Dosage Details", "")
        if freq:
            items_to_translate.append({"idx": i, "field": "Frequency/Instructions", "text": freq})
        if dosage:
            items_to_translate.append({"idx": i, "field": "Dosage Details", "text": dosage})

    if not items_to_translate:
        return prescription_list

    # Build numbered list for Gemini
    numbered = "\n".join([f"{j+1}. {t['text']}" for j, t in enumerate(items_to_translate)])

    prompt = f"""Translate each numbered text below into {target_lang} language.

RULES:
- You MUST translate into {target_lang}. Do NOT return English text.
- Keep medicine names, numbers, mg values, and patterns like 1-0-1 in English.
- Return ONLY a JSON array with the translated texts in the same order.
- Format: ["translation 1", "translation 2", ...]
- No explanation, no markdown, just the JSON array.

Texts to translate:
{numbered}

JSON array of {target_lang} translations:"""

    try:
        response = model.generate_content(prompt)
        result = response.text.strip()
        # Extract JSON array
        start = result.find("[")
        end = result.rfind("]") + 1
        if start != -1 and end > start:
            translations = json.loads(result[start:end])
            for j, t in enumerate(items_to_translate):
                if j < len(translations) and translations[j]:
                    prescription_list[t["idx"]][t["field"]] = translations[j]
    except Exception:
        pass  # Keep English if translation fails

    return prescription_list


# -----------------------------------------------------------------------
# BUILD MEDICINE DISPLAY CARD
# -----------------------------------------------------------------------
def build_medicine_card(idx, med_name, dosage, instructions, pattern, duration, med_info):
    md = f"---\n### 💊 {idx}. {med_name}\n\n"

    # Usage
    md += "✅ **Usage:**\n"
    for point in med_info.get("usage", []):
        point = point.strip().lstrip("-").lstrip("*").strip()
        if point:
            md += f"- {point}\n"
    md += "\n"

    # Dosage
    md += f"💊 **Dosage:** {dosage}\n"
    md += f"- {instructions}\n"
    if pattern:
        md += f"- **({pattern} pattern)**\n"
    if duration:
        md += f"- Duration: **{duration}**\n"
    md += "\n"

    # Side Effects
    md += "⚠️ **Common Side Effects:**\n"
    for effect in med_info.get("side_effects", []):
        effect = effect.strip().lstrip("-").lstrip("*").strip()
        if effect:
            md += f"- {effect}\n"
    md += "\n"

    # Allergy Alert or Drug Interaction
    allergy_info = med_info.get("allergy_alert", {})
    if allergy_info.get("triggered", False):
        drug_class = med_info.get("drug_class", "this drug class")
        md += "🚨 **Drug Interaction & Allergy Check:**\n"
        md += f"❌ **ALERT:** {allergy_info.get('message', '')}\n"
        md += f"⚠ **{med_name}** belongs to **{drug_class}**\n"
        md += "👉 **Recommendation: Consult doctor immediately before taking this medicine.**\n\n"
    else:
        md += "🔎 **Drug Interaction Check:**\n"
        interactions = med_info.get("interaction_with_prescribed", [])
        if interactions:
            for interaction in interactions:
                other_med = interaction.get("medicine", "")
                is_safe = interaction.get("safe", True)
                note = interaction.get("note", "")
                if is_safe:
                    md += f"✔ Safe with **{other_med}**"
                    if note:
                        md += f" — {note}"
                    md += "\n"
                else:
                    md += f"⚠ Use cautiously with **{other_med}** — {note}\n"

        for warning in med_info.get("general_warnings", []):
            warning = warning.strip()
            if warning:
                md += f"⚠ {warning}\n"

        summary = med_info.get("overall_interaction_summary", "")
        if summary:
            md += f"\n📋 *{summary}*\n"

    md += "\n"
    return md


# -----------------------------------------------------------------------
# AUDIO HELPERS
# -----------------------------------------------------------------------
def clean_text_for_speech(text):
    symbols = [
        "*", "#", "|", "`", "_", "---", "**",
        "✅", "⚠️", "⚠", "🔎", "💊", "🚨", "❌",
        "✔", "📋", "👉", "🧾", "👤", "👨", "🔊"
    ]
    for s in symbols:
        text = text.replace(s, "")
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line and line.strip("-").strip()]
    return "\n".join(lines)


def text_to_audio(text, lang="en"):
    try:
        clean_text = clean_text_for_speech(text)
        if not clean_text.strip():
            return "<p>No text to speak.</p>"

        gtts_lang = lang if lang in ["en", "es", "fr", "hi", "ta", "bn", "kn", "mr", "te"] else "en"

        chunk_size = 500
        chunks = []
        while len(clean_text) > chunk_size:
            split_at = clean_text.rfind(".", 0, chunk_size)
            if split_at == -1:
                split_at = clean_text.rfind("\n", 0, chunk_size)
            if split_at == -1:
                split_at = chunk_size
            chunks.append(clean_text[: split_at + 1].strip())
            clean_text = clean_text[split_at + 1:].strip()
        if clean_text:
            chunks.append(clean_text)

        combined = io.BytesIO()
        for chunk in chunks:
            if chunk.strip():
                try:
                    tts = gTTS(text=chunk, lang=gtts_lang)
                    fp = io.BytesIO()
                    tts.write_to_fp(fp)
                    fp.seek(0)
                    combined.write(fp.read())
                except Exception:
                    continue

        combined.seek(0)
        audio_b64 = base64.b64encode(combined.read()).decode()
        return f'<audio controls src="data:audio/mp3;base64,{audio_b64}">Your browser does not support audio.</audio>'
    except Exception as e:
        return f"<p>Error in voice generation: {e}</p>"


def parse_frequency_to_times(instructions):
    instructions_lower = instructions.lower()
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
if "reminders" not in st.session_state:
    st.session_state.reminders = []
if "extracted_medicines" not in st.session_state:
    st.session_state.extracted_medicines = {}
if "patient_info_display" not in st.session_state:
    st.session_state.patient_info_display = None
if "medicine_display_text" not in st.session_state:
    st.session_state.medicine_display_text = None
if "full_prescription" not in st.session_state:
    st.session_state.full_prescription = None
if "medicine_cards_list" not in st.session_state:
    st.session_state.medicine_cards_list = []


# -----------------------------------------------------------------------
# MAIN APP
# -----------------------------------------------------------------------
def main():
    st.set_page_config(
        page_title="AI Smart Prescription Guide",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("💊 AI Smart Prescription Guide for Safer Healthcare")
    st.caption("Powered by Google Gemini — Fully AI-driven analysis, no hardcoded database")

    # --- Sidebar ---
    st.sidebar.header("⚙️ Settings & Features")

    selected_lang_name = st.sidebar.selectbox(
        "🌐 Select Language for Output:", list(LANG_OPTIONS.keys())
    )
    target_lang_code = LANG_OPTIONS[selected_lang_name]
    clean_lang = LANG_PLAIN_NAME[selected_lang_name]

    voice_guidance_enabled = st.sidebar.checkbox("🔊 Enable Voice Guidance", value=True)

    st.sidebar.subheader("⏰ Set Medication Reminders")
    medicine_names = list(st.session_state.extracted_medicines.keys())

    if medicine_names:
        st.sidebar.markdown("**Step 1: Select Medicine**")
        selected_medicine = st.sidebar.selectbox(
            "Select medicine for reminder:",
            options=["-- Select Medicine --"] + medicine_names,
            key="reminder_med_select",
        )

        if selected_medicine and selected_medicine != "-- Select Medicine --":
            med_data = st.session_state.extracted_medicines[selected_medicine]

            st.sidebar.markdown("**Step 2: Set Alarm Times**")
            instructions = med_data.get("Frequency/Instructions", "")
            suggested_times = parse_frequency_to_times(instructions)

            num_alarms = st.sidebar.number_input(
                "Number of alarms per day:",
                min_value=1, max_value=4,
                value=len(suggested_times),
                key="num_alarms_input",
            )

            alarm_times = []
            for i in range(num_alarms):
                default_time_str = suggested_times[i] if i < len(suggested_times) else "08:00"
                hour, minute = map(int, default_time_str.split(":"))
                c1, c2 = st.sidebar.columns(2)
                with c1:
                    alarm_hour = st.number_input(
                        f"Alarm {i+1} Hour:", min_value=0, max_value=23,
                        value=hour, key=f"hour_{selected_medicine}_{i}",
                    )
                with c2:
                    alarm_minute = st.number_input(
                        f"Minute:", min_value=0, max_value=59,
                        value=minute, key=f"minute_{selected_medicine}_{i}",
                    )
                alarm_times.append(f"{alarm_hour:02d}:{alarm_minute:02d}")

            st.sidebar.markdown("**Step 3: Notes**")
            additional_notes = st.sidebar.text_input(
                "Notes (optional):", value=instructions[:50], key="notes_input"
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
            c1, c2 = st.sidebar.columns([5, 1])
            with c1:
                st.sidebar.text(f"{idx+1}. {reminder}")
            with c2:
                if st.sidebar.button("❌", key=f"del_{idx}"):
                    st.session_state.reminders.pop(idx)
                    st.rerun()

    st.markdown("---")

    # --- Main Content ---
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("1. Upload Prescription Image")
        uploaded_file = st.file_uploader(
            "Choose a prescription image", type=["png", "jpg", "jpeg"]
        )

        image = None
        if uploaded_file is not None:
            try:
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Prescription", use_container_width=True)
            except Exception as e:
                st.error(f"Error loading image: {e}")

    with col2:
        st.subheader("2. Analyze Prescription")
        if image is not None:

            extraction_prompt = """
You are a medical prescription analyzer.
Extract ALL information from this prescription image.
Keep ALL medicine names and dosage instructions in English.
Return ONLY valid JSON, no other text:
{
    "patient_info": {
        "name": "patient name",
        "age": "age",
        "sex": "sex",
        "date": "date",
        "known_allergies": "allergies mentioned or None"
    },
    "doctor_info": {
        "name": "doctor name",
        "license": "license number or N/A"
    },
    "prescription": [
        {
            "Medicine Name": "medicine brand name with strength in English",
            "Dosage Details": "strength and form e.g. 625mg tablet",
            "Frequency/Instructions": "full dosage instructions in English",
            "Dosage Pattern": "pattern like 1-0-1",
            "Duration": "e.g. 5 days"
        }
    ]
}
"""

            if st.button("🔍 Extract and Analyze"):
                for key in list(st.session_state.keys()):
                    if key.startswith("hour_") or key.startswith("minute_"):
                        del st.session_state[key]

                # STEP 1: Extract prescription from image
                with st.spinner("📖 Reading prescription image..."):
                    try:
                        try:
                            response = model.generate_content(
                                [extraction_prompt, image],
                                generation_config=genai.GenerationConfig(
                                    response_mime_type="application/json"
                                ),
                            )
                        except Exception:
                            response = model.generate_content([extraction_prompt, image])

                        json_str = (
                            response.text.strip()
                            .replace("```json", "")
                            .replace("```", "")
                            .strip()
                        )
                        data = json.loads(json_str)

                        patient = data.get("patient_info", {})
                        doctor = data.get("doctor_info", {})
                        prescription_list = data.get("prescription", [])
                        patient_allergies = patient.get("known_allergies", "None")

                        # Build patient info block (names/dates stay in English)
                        patient_text = "## 🧾 AI Smart Prescription Guide\n\n"
                        patient_text += "### 👤 Patient Information\n"
                        patient_text += f"- **Name:** {patient.get('name', 'N/A')}\n"
                        patient_text += f"- **Age:** {patient.get('age', 'N/A')}\n"
                        patient_text += f"- **Sex:** {patient.get('sex', 'N/A')}\n"
                        patient_text += f"- **Date:** {patient.get('date', 'N/A')}\n"
                        patient_text += f"- **Known Allergies:** {patient_allergies}\n\n"
                        patient_text += "### 👨‍⚕️ Doctor Information\n"
                        patient_text += f"- **Name:** {doctor.get('name', 'N/A')}\n"
                        patient_text += f"- **License:** {doctor.get('license', 'N/A')}\n\n"

                        st.session_state.patient_info_display = patient_text

                        # Translate dosage fields in ONE batch call
                        if clean_lang != "English":
                            with st.spinner(f"🌐 Translating dosage instructions to {clean_lang}..."):
                                prescription_list = translate_dosage_fields(prescription_list, clean_lang)

                        all_medicine_names = []
                        extracted_med_map = {}
                        for item in prescription_list:
                            med_name = item.get("Medicine Name", "N/A")
                            all_medicine_names.append(med_name)
                            extracted_med_map[med_name] = item

                        st.session_state.extracted_medicines = extracted_med_map

                    except json.JSONDecodeError:
                        st.error("Could not parse prescription. Try a clearer image.")
                        st.stop()
                    except Exception as e:
                        st.error(f"Extraction error: {e}")
                        st.stop()

                st.success(f"✅ Found {len(prescription_list)} medicine(s). Fetching AI analysis in {clean_lang}...")

                # STEP 2: Per-medicine — ONE Gemini call that returns data already in target language
                medicine_text = ""
                medicine_cards_list = []
                progress_bar = st.progress(0, text="Starting analysis...")

                total = len(prescription_list)
                for idx, item in enumerate(prescription_list, 1):
                    med_name = item.get("Medicine Name", "N/A")
                    dosage = item.get("Dosage Details", "N/A")
                    instructions = item.get("Frequency/Instructions", "N/A")
                    pattern = item.get("Dosage Pattern", "")
                    duration = item.get("Duration", "")

                    progress_bar.progress(
                        int((idx / total) * 100),
                        text=f"🔍 Analyzing {med_name} in {clean_lang} ({idx}/{total})...",
                    )

                    # Single call: analyze + translate in one shot
                    med_info = get_medicine_info_from_gemini(
                        medicine_name=med_name,
                        all_medicines=all_medicine_names,
                        patient_allergies=patient_allergies,
                        target_lang=clean_lang,
                    )

                    card = build_medicine_card(
                        idx, med_name, dosage, instructions, pattern, duration, med_info
                    )
                    medicine_text += card
                    medicine_cards_list.append({"name": med_name, "text": card})

                progress_bar.empty()

                st.session_state.medicine_display_text = medicine_text
                st.session_state.medicine_cards_list = medicine_cards_list
                st.session_state.full_prescription = patient_text + medicine_text

                st.success(f"✅ Full Analysis Complete in {clean_lang}!")

    st.markdown("---")

    # --- Results Display ---
    if st.session_state.full_prescription:

        if st.session_state.patient_info_display:
            st.markdown(st.session_state.patient_info_display)

        st.markdown("---")
        st.subheader(f"💊 Prescribed Medicines – Detailed Analysis ({selected_lang_name})")

        if st.session_state.medicine_display_text:
            st.markdown(st.session_state.medicine_display_text)

        if voice_guidance_enabled:
            st.markdown("---")
            st.markdown("### 🔊 Voice Guidance")

            st.markdown("**👤 Patient & Doctor Info:**")
            audio_html = text_to_audio(
                st.session_state.patient_info_display or "", lang=target_lang_code
            )
            st.markdown(audio_html, unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("**💊 Medicine-wise Audio:**")
            med_cards = st.session_state.get("medicine_cards_list", [])
            if med_cards:
                for card_info in med_cards:
                    st.markdown(f"🔊 *{card_info['name']}*")
                    audio_html = text_to_audio(card_info["text"], lang=target_lang_code)
                    st.markdown(audio_html, unsafe_allow_html=True)
            else:
                audio_html = text_to_audio(
                    st.session_state.medicine_display_text or "", lang=target_lang_code
                )
                st.markdown(audio_html, unsafe_allow_html=True)

        st.markdown("---")
        st.warning(
            "⚠️ **Important Disclaimer:** This AI analysis is for informational purposes only. "
            "Always consult your doctor or pharmacist for comprehensive medical advice. "
            "Do not modify your prescription based solely on this report."
        )


if __name__ == "__main__":
    main()
