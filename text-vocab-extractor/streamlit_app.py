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

st.title("Nederlandse Tekst Samenvatting")
st.write("Gemini AI gebruiken om Nederlandse teksten samen te vatten voor taalstudenten!")

# Sidebar configuration
st.sidebar.header("🔧 Instellingen")


# API key configuration
# api_key = os.getenv("GEMINI_API_KEY")
api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))

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
    placeholder="Voer hier de Nederlandse tekst in die je wilt samenvatten..."
)

# Language selection
target_language = st.selectbox(
    "Welke taal spreek je?",
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

# Analysis level selection
analysis_level = st.selectbox(
    "Kies je Nederlandse niveau:",
    options=["A1 (Beginner)", "A2 (Elementair)", "B1 (Intermediate)", "B2 (Gevorderd)"],
    help="Kies je huidige Nederlandse niveau voor aangepaste uitleg"
)


# Summary execution button
if st.button("🚀 Tekst Samenvatten", type="primary", disabled=not (api_key and keyword)):
    if not api_key:
        st.warning("⚠️ Voer eerst je API sleutel in!")
    elif not keyword:
        st.warning("⚠️ Voer de Nederlandse tekst in!")
    else:
        with st.spinner("Gemini AI analyseert de tekst..."):
            try:
                # Generate prompt (based on selected language)
                if lang_code == "kr":
                    target_explanation = "한국어"
                    prompt = f"""다음 조건에 맞춰 네덜란드어 텍스트를 요약하고 분석하시오: "{keyword}"

조건:
- {analysis_level.split()[0]} 수준 학습자를 위한 쉬운 네덜란드어 요약 (최대 10문장)
- 한국어 사용자를 위한 상세한 설명
- JSON 형태로 결과 제공

중요한 키워드 선별 규칙:
- 고유명사 제외: 사람 이름, 지역명, 도시명, 국가명, 회사명, 브랜드명, 단체명 등은 포함하지 말 것
- 일반 명사, 동사, 형용사, 부사 등 언어 학습에 유용한 단어만 선별
- 네덜란드어에서 자주 사용되는 실용적인 어휘 위주로 선택

유용한 표현 선별 규칙:
- 관용어, 숙어, 고정된 표현(동사+명사, 형용사+명사, 전치사구, 구동사)
- 특별한 의미가 없는 단순한 어휘 조합은 제외

JSON 구조:
- summary: {{"nl": "네덜란드어 요약", "kr": "한국어 번역"}}
- expressions: [{{"expression": "유용한 표현", "explanation": {{"nl": "네덜란드어 설명", "kr": "한국어 설명"}}, "examples": [{{"nl": "네덜란드어 예문", "kr": "한국어 예문"}}] (3개) }}] (5개 이상)
- keywords: [{{"keyword": {{"nl": "네덜란드어 키워드", "kr": "한국어 키워드"}}, "examples": [{{"nl": "네덜란드어 예문", "kr": "한국어 예문"}}] (3개) }}] (10개 이상)"""
                
                else:  # English
                    prompt = f"""Summarize and analyze the following Dutch text for English speakers: "{keyword}"

Requirements:
- Easy Dutch summary for {analysis_level.split()[0]} level learners (max 10 sentences)
- Detailed explanations for English speakers
- Provide result in JSON format

Important keyword selection rules:
- EXCLUDE proper nouns: person names, place names, city names, country names, company names, brand names, organization names, etc.
- ONLY include common nouns, verbs, adjectives, adverbs that are useful for language learning
- Focus on practical vocabulary frequently used in Dutch

Useful expressions selection rules:
- Idioms, Fixed constructions (verb + noun combinations, adjective + noun combination, prepositional phrases, common phrasal verbs)
- Only select phrases with special meaning, not simple word listings 

JSON structure:
- summary: {{"nl": "Dutch summary", "en": "English translation"}}
- expressions: [{{"expression": "useful expression", "explanation": {{"nl": "Dutch explanation", "en": "English explanation"}}, "examples": [{{"nl": "Dutch example", "en": "English example"}}] (3 items) }}] (more than 5 items)
- keywords: [{{"keyword": {{"nl": "Dutch keyword", "en": "English keyword"}}, "examples": [{{"nl": "Dutch example", "kr": "English example"}}] (3 items) }}] (more than 10 items)"""
                
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
                    st.success("✅ Samenvatting voltooid!")
                    
                    # Summary section
                    st.header("📋 Samenvatting")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Nederlands")
                        summary_nl = result_json.get("summary", {}).get("nl", "Geen samenvatting gevonden.")
                        st.write(summary_nl)
                    
                    with col2:
                        st.subheader(f"{lang_name}")
                        summary_target = result_json.get("summary", {}).get(lang_code, "Geen vertaling gevonden.")
                        st.write(summary_target)
                    
                    # Useful expressions section
                    st.header("💬 Nuttige Uitdrukkingen")
                    expressions = result_json.get("expressions", [])
                    
                    if expressions:
                        for i, item in enumerate(expressions, 1):
                            with st.expander(f"**{item.get('expression', 'N/A')}**"):
                                explanation_nl = item.get('explanation', {}).get('nl', 'N/A')
                                explanation_target = item.get('explanation', {}).get(lang_code, 'N/A')
                                st.write(f"{explanation_nl} ({explanation_target})")
                                st.write(f"**voorbeeld:**")

                                examples = item.get('examples', [])
                                for idx, example in enumerate(examples, 1):
                                    example_nl = example.get('nl', 'N/A')
                                    example_target = example.get(lang_code, 'N/A')
                                    st.write(f"- {example_nl} ({example_target})")
                    
                    # Keywords section
                    st.header("🏷️ Belangrijke Woorden")
                    keywords = result_json.get("keywords", [])
                    
                    if keywords:
                        for i, item in enumerate(keywords, 1):
                            with st.expander(f"**{item.get('keyword', {}).get('nl', 'N/A')}**"):
                                item.get('keyword', {}).get('nl', 'N/A')
                                st.write(f"{item.get('keyword', {}).get(lang_code, 'N/A')}")
                                st.write(f"**voorbeeld:**")
                                examples = item.get('examples', [])
                                for idx, example in enumerate(examples, 1):
                                    example_nl = example.get('nl', 'N/A')
                                    example_target = example.get(lang_code, 'N/A')
                                    st.write(f"- {example_nl} ({example_target})")
                    
                    # Display original JSON
                    # with st.expander("🔧 Originele JSON Data for developer"):
                    #     st.json(result_json)
                
                except json.JSONDecodeError:
                    st.warning("⚠️ JSON verwerking mislukt. Originele respons:")
                    st.text_area("Originele respons:", value=result_text, height=300)
                    
            except Exception as e:
                st.error(f"❌ Er is een fout opgetreden: {str(e)}")

# Markdown
st.markdown("---")
st.markdown("*Gemaakt met ❤️ door Streamlit en Google Gemini AI voor Nederlandse taalstudenten*")
st.markdown("*Als je contact wilt opnemen met de maker, kun je een e-mail sturen naar ahkyeong.choe@gmail.com.*")