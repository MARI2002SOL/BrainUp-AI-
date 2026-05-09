import streamlit as st
import google.generativeai as genai
from pymongo import MongoClient

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="Analizador de Poemas IA",
    page_icon="📜",
    layout="wide"
)

# =========================
# CUSTOM CSS
# =========================

st.markdown("""
<style>

.main {
    background-color: #0f1117;
}

h1 {
    text-align: center;
    color: #f5f5f5;
    font-size: 3rem;
}

.subtitle {
    text-align: center;
    color: #b0b0b0;
    font-size: 1.1rem;
    margin-bottom: 2rem;
}

.stTextArea textarea {
    background-color: #1c1f26;
    color: white;
    border-radius: 15px;
    border: 1px solid #444;
    font-size: 16px;
    padding: 15px;
}

.stButton button {
    width: 100%;
    background: linear-gradient(90deg, #7F5AF0, #2CB67D);
    color: white;
    border: none;
    border-radius: 12px;
    height: 3em;
    font-size: 18px;
    font-weight: bold;
    transition: 0.3s;
}

.stButton button:hover {
    transform: scale(1.02);
    opacity: 0.9;
}

.result-box {
    background-color: #1c1f26;
    padding: 25px;
    border-radius: 18px;
    border: 1px solid #333;
    margin-top: 20px;
}

.footer {
    text-align: center;
    color: gray;
    margin-top: 50px;
    font-size: 0.9rem;
}

</style>
""", unsafe_allow_html=True)

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
# HEADER
# =========================

st.markdown("<h1>📜 Analizador de Poemas con IA</h1>", unsafe_allow_html=True)

st.markdown("""
<div class="subtitle">
Descubre el significado oculto, emociones y recursos literarios de cualquier poema en español ✨
</div>
""", unsafe_allow_html=True)

# =========================
# INPUT
# =========================

poema = st.text_area(
    "✍️ Escribe tu poema aquí",
    height=300,
    placeholder="""
Puedo escribir los versos más tristes esta noche...
"""
)

# =========================
# BUTTON
# =========================

if st.button("✨ Analizar poema"):

    if not poema.strip():

        st.warning("⚠️ Por favor escribe un poema.")

    else:

        with st.spinner("Analizando poema..."):

            try:

                prompt = f"""
                Primero determina si el siguiente texto es realmente un poema en español.

                Si NO es un poema:
                - responde solamente:
                "El texto ingresado no parece ser un poema."

                Reglas IMPORTANTES:
                - NO analices saludos, frases cortas o palabras aisladas.
                - NO analices letras de reggaetón, trap, canciones comerciales o frases virales.
                - Si el texto no parece un poema literario auténtico, responde SOLO:
                "El texto ingresado no parece ser un poema literario."

                Si SÍ es un poema:
                analiza y genera:

                1. Tema principal
                2. Emociones transmitidas
                3. Tono del poema
                4. Recursos literarios utilizados
                5. Interpretación del significado
                6. Explicación sencilla para estudiantes

                Texto:
                {poema}
                """

                response = model.generate_content(prompt)

                analisis = response.text

                # =========================
                # RESULTS
                # =========================

                st.markdown("""
                <div class="result-box">
                """, unsafe_allow_html=True)

                st.subheader("📖 Análisis del poema")

                st.write(analisis)

                st.markdown("</div>", unsafe_allow_html=True)

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

# =========================
# FOOTER
# =========================
