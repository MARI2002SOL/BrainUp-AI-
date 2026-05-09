import streamlit as st
import google.generativeai as genai
from pymongo import MongoClient

# =========================
# CONFIG
# =========================

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
MONGODB_URI = st.secrets["MONGODB_URI"]

# =========================
# GEMINI
# =========================

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash"
)

# =========================
# MONGODB
# =========================

client = MongoClient(MONGODB_URI)

db = client["poetry_ai"]

collection = db["analyses"]

# =========================
# STREAMLIT UI
# =========================

st.set_page_config(
    page_title="Analizador de Poemas IA",
    page_icon="📜",
    layout="wide"
)

st.title("📜 Analizador de Poemas con IA")

st.markdown("""
Escribe o pega un poema en español y la IA analizará:

- Tema principal
- Emociones
- Recursos literarios
- Significado
- Tono del poema
- Interpretación sencilla
""")

# =========================
# INPUT
# =========================

poema = st.text_area(
    "✍️ Escribe tu poema aquí",
    height=300,
    placeholder="Ejemplo:\n\nPuedo escribir los versos más tristes esta noche..."
)

# =========================
# ANALYZE BUTTON
# =========================

if st.button("Analizar poema"):

    if not poema.strip():

        st.warning("⚠️ Por favor escribe un poema.")

    else:

        with st.spinner("Analizando poema..."):

            try:

                prompt = f"""
                Eres un experto en literatura y poesía en español.

                Analiza el siguiente poema y genera:

                1. Tema principal
                2. Emociones transmitidas
                3. Tono del poema
                4. Recursos literarios utilizados
                5. Interpretación del significado
                6. Explicación sencilla para estudiantes

                Sé claro, organizado y profundo.

                POEMA:
                {poema}
                """

                response = model.generate_content(prompt)

                analisis = response.text

                # =========================
                # SHOW RESULTS
                # =========================

                st.subheader("📖 Análisis del poema")

                st.write(analisis)

                # =========================
                # SAVE TO MONGODB
                # =========================

                document = {
                    "poema": poema,
                    "analisis": analisis
                }

                collection.insert_one(document)

                st.success("✅ Análisis guardado en MongoDB")

            except Exception as e:

                st.error(f"⚠️ Error: {str(e)}")