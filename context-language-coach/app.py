import streamlit as st
import google.generativeai as genai
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Nederlandse Woorden Coach", 
    page_icon="", 
    layout="wide"
)

st.title("Nederlandse Woorden Coach")
st.write("Leer Nederlandse woorden en uitdrukkingen voor elke situatie!")

# Sidebar configuration
st.sidebar.header("🔧 Instellingen")

# API key configuration
api_key = os.getenv("GEMINI_API_KEY")
# api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))

if api_key:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        st.sidebar.success("✅ API sleutel ingesteld! (omgevingsvariabele)")
    except Exception as e:
        st.sidebar.error(f"❌ API sleutel fout: {str(e)}")
else:
    api_key = st.sidebar.text_input("Voer je Gemini API sleutel in:", type="password", 
                                   help="Gemini API sleutel van Google AI Studio")
    if api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            st.sidebar.success("✅ API sleutel ingesteld!")
        except Exception as e:
            st.sidebar.error(f"❌ API sleutel fout: {str(e)}")

# Text input area
st.header("📝 Situatie")
situation = st.text_area(
    "Voer de situatie in die je wilt leren:",
    height=200,
    placeholder="Bijv.: bestellen in een café, een bezoek aan de dokter, boodschappen doen, enz.",
    help="Hoe specifieker de situatie, hoe nuttiger de woorden die je ontvangt."
)

# Language selection
target_language = st.selectbox(
    "In welke taal wil je de uitleg ontvangen?",
    options=["Korean (한국어)", "English"],
    help="Kies je moedertaal voor uitleg en vertalingen"
)

# Language code configuration
language_mapping = {
    "Korean (한국어)": {"code": "kr", "name": "한국어", "full": "Korean"},
    "English": {"code": "en", "name": "English", "full": "English"},
}

lang_info = language_mapping[target_language]
lang_code = lang_info["code"]
lang_name = lang_info["name"]
lang_full = lang_info["full"]

# CEFR level
def get_cefr_order(level):
    """CEFR 레벨을 숫자로 변환하여 정렬에 사용"""
    level_order = {'A1': 1, 'A2': 2, 'B1': 3, 'B2': 4, 'C1': 5, 'C2': 6}
    clean_level = level.split()[0] if level else "A1"
    return level_order.get(clean_level, 0)

# Summary execution button
if st.button("🚀 Woorden ophalen", type="primary", disabled=not (api_key and situation)):
    if not api_key:
        st.warning("⚠️ Voer eerst je API sleutel in!")
    elif not situation:
        st.warning("⚠️ Voer eerst een situatie in!")
    else:
        with st.spinner("Nederlandse woorden en voorbeeldzinnen worden opgehaald... Even geduld hebben."):
            prompt = f"""Could you provide 20 useful Dutch words or phrases relevant to the following situation? {situation} 
Requirements:
- along with 4 example sentences for each 
- provide {lang_full} translations
- indicate the CEFR level for each word/phrase
- Provide result in JSON format

JSON structure:
- words: [{{"keyword": {{"nl": "Dutch keyword", "target": "{lang_full} keyword", "level": "CEFR level"}}, "examples": [{{"nl": "Dutch example", "target": "{lang_full} example"}}] (4 items) }}] (20 items)"""
            
            # API call
            response = model.generate_content(prompt)
            result_text = response.text
                
            # JSON parsing
            try:
                if "```json" in result_text:
                    json_start = result_text.find("```json") + 7
                    json_end = result_text.find("```", json_start)
                    json_text = result_text[json_start:json_end].strip()
                elif "{" in result_text:
                    json_start = result_text.find("{")
                    json_end = result_text.rfind("}") + 1
                    json_text = result_text[json_start:json_end]
                else:
                    json_text = result_text
                
                result_json = json.loads(json_text)
                
                # Display results
                st.success("✅ Klaar!")                    
                # words and expressions section
                st.header("💬 Nuttige Woorden en Uitdrukkingen")
                words = result_json.get("words", [])
                
                if words:
                    sorted_words = sorted(words, key=lambda x: get_cefr_order(x.get('keyword', {}).get('level', 'A1')))

                    for i, item in enumerate(sorted_words, 1):
                        word_nl = item.get('keyword', {}).get('nl', 'N/A')
                        word_target = item.get('keyword', {}).get('target', 'N/A')
                        word_level = item.get('keyword', {}).get('level', 'N/A')
                        with st.expander(f"**{word_nl}** ({word_level})"):
                            st.write(f"{word_target}")
                            st.write(f"**Voorbeelden:**")
                            examples = item.get('examples', [])
                            for idx, example in enumerate(examples, 1):
                                example_nl = example.get('nl', 'N/A')
                                example_target = example.get('target', 'N/A')
                                st.write(f"- {example_nl} ({example_target})")
                    
                # Display original JSON
                # with st.expander("🔧 Originele JSON Data for developer"):
                #     st.json(result_json)
                
            except json.JSONDecodeError:
                st.warning("⚠️ JSON verwerking mislukt. Originele respons:")
                st.text_area("Originele respons:", value=result_text, height=300)
                
# Markdown
st.markdown("---")
st.markdown("*Gemaakt met ❤️ door Ahkyeong*")
st.markdown("*Voor vragen of opmerkingen kun je een e-mail sturen naar ahkyeong.choe@gmail.com.*")