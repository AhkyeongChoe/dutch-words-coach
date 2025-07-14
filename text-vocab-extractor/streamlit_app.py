import streamlit as st
import google.generativeai as genai
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Nederlandse Tekst Samenvatting", 
    page_icon="", 
    layout="wide"
)

st.title("Woorden & Uitdrukkingen")
st.write("Ontdek belangrijke Nederlandse woorden en uitdrukkingen in teksten!")

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
st.header("📝 Nederlandse Tekst Invoeren")
keyword = st.text_area(
    "Plak hier je Nederlandse tekst:",
    height=200,
    placeholder="Voer hier de Nederlandse tekst in die je wilt lezen..."
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
    level_order = {'A1': 1, 'A2': 2, 'B1': 3, 'B2': 4, 'C1': 5, 'C2': 6}
    clean_level = level.split()[0] if level else "A1"
    return level_order.get(clean_level, 0)

# Analysis level selection
analysis_level = st.selectbox(
    "Kies je Nederlandse niveau:",
    options=["A1 (Beginner)", "A2 (Elementair)", "B1 (Intermediate)", "B2 (Gevorderd)"],
    help="Kies je huidige Nederlandse niveau voor aangepaste uitleg"
)
lang_level = analysis_level.split()[0]


# Summary execution button
if st.button("🚀 Woorden ophalen", type="primary", disabled=not (api_key and keyword)):
    if not api_key:
        st.warning("⚠️ Voer eerst je API sleutel in!")
    elif not keyword:
        st.warning("⚠️ Voer de Nederlandse tekst in!")
    else:
        with st.spinner("Nederlandse woorden en voorbeeldzinnen worden opgehaald... Even geduld hebben."):
            prompt = f"""Please analyze the following Dutch text and extract the most useful vocabulary for language learners.
TEXT TO ANALYZE: 
"{keyword}"

REQUIREMENTS:
- Extract 20 important and useful Dutch words, phrases, or expressions from the provided text
- Provide 4 example sentences for each expressions
- Rewrite the given text to be suitable for {lang_level} level learners
- Provide {lang_full} translations for all content
- Indicate the CEFR level for each word/phrase

SELECTION RULES:
✓ INCLUDE: Common nouns, verbs, adjectives, adverbs useful for language learning
✓ INCLUDE: Idioms, fixed constructions (verb+noun, adjective+noun, prepositional phrases)
✓ INCLUDE: Common phrasal verbs and expressions with special meanings
✓ EXCLUDE: Proper nouns (person names, place names, companies, brands, organizations)
✓ EXCLUDE: Simple word listings without special meaning
✓ PRIORITY: Practical vocabulary frequently used in everyday Dutch
  
OUTPUT FORMAT:
provide the result in JSON format with this structure:

{{
  "rewritten_text": {{
    "nl": "Dutch text adapted for {lang_level} level",
    "target": "{lang_full} translation"
  }},
  "words": [
    {{
      "nl": "useful Dutch word from text",
      "target": "{lang_full} translation ",
      "level": "CEFR level (A1/A2/B1/B2/C1/C2)"
      "examples": [
        {{
          "nl": "Natural Dutch example sentence",
          "target": "{lang_full} translation"
        }}
      ]
    }}
  ]
}}"""
                
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
                
                # rewritten text section
                st.header(f"📋 Tekst op {lang_level}-niveau")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Nederlands")
                    rewritten_nl = result_json.get("rewritten_text", {}).get("nl", "Geen samenvatting gevonden.")
                    st.write(rewritten_nl)
                
                with col2:
                    st.subheader(f"{lang_name}")
                    rewritten_target = result_json.get("rewritten_text", {}).get("target", "Geen vertaling gevonden.")
                    st.write(rewritten_target)
                
                # Expressions section
                st.header("💬 Nuttige Uitdrukkingen & Woorden")
                words = result_json.get("words", [])
                
                if words:
                    sorted_words = sorted(words, key=lambda x: get_cefr_order(x.get('level', 'A1')))

                    for i, item in enumerate(sorted_words, 1):
                        word_nl = item.get('nl', 'N/A')
                        word_target = item.get('target', 'N/A')
                        word_level = item.get('level', 'N/A')
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
st.markdown("*Als je contact wilt opnemen met de maker, kun je een e-mail sturen naar ahkyeong.choe@gmail.com.*")