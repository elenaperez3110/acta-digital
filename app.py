import streamlit as st

st.set_page_config(page_title="Acta Digital", page_icon="📝", layout="centered")

st.title("📝 Acta Digital")
st.write("Hola, Streamlit está funcionando.")

with st.form("acta_form"):
    titulo = st.text_input("Título del acta")
    asistentes = st.text_area("Asistentes (uno por línea)")
    acuerdos = st.text_area("Acuerdos")
    enviado = st.form_submit_button("Guardar")
    if enviado:
        st.success("Acta registrada ✅")
        st.json({
            "titulo": titulo,
            "asistentes": [a for a in asistentes.splitlines() if a.strip()],
            "acuerdos": acuerdos
        })
