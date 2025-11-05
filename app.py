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

import streamlit as st
import hashlib, time, json

st.title("Prueba de imports")
st.write("Streamlit OK ✅")
st.write("hash de 'hola':", hashlib.sha256(b"hola").hexdigest())
st.write("Epoch time:", int(time.time()))
st.json({"clave": "valor"})

import streamlit as st
import hashlib, time, json
from typing import Literal

# ---------- Núcleo ----------
def get_hash(
    text: str,
    *,
    algo: Literal["sha256","sha512","sha1","md5"]="sha256",
    salt: str="",
    iterations: int=1,
    output: Literal["hex","bytes"]="hex",
):
    """Calcula el hash de 'text' con opciones."""
    if iterations < 1:
        iterations = 1
    # Construye bytes: salt + texto (UTF-8)
    data = (salt + text).encode("utf-8")
    h = _hash_once(data, algo)
    for _ in range(iterations - 1):
        h = _hash_once(h, algo)  # re-hasheo de bytes
    return h.hex() if output == "hex" else h

def _hash_once(data: bytes, algo: str) -> bytes:
    h = getattr(hashlib, algo)()
    h.update(data)
    return h.digest()

# ---------- UI ----------
st.set_page_config(page_title="Acta Digital — Hashing", page_icon="🧩", layout="centered")
st.title("🧩 Herramientas de Hash")
st.caption("SHA-256 por defecto. Evita MD5/SHA-1 para seguridad.")

with st.expander("ℹ️ ¿Qué es un hash?"):
    st.write(
        "- Es una huella digital del contenido. Cambios mínimos producen hashes distintos.\n"
        "- Útil para verificar integridad o deduplicar, **no** para cifrar ni guardar contraseñas en claro.\n"
        "- Para contraseñas usa funciones específicas (bcrypt/argon2/scrypt)."
    )

tab_texto, tab_archivo, tab_verificar = st.tabs(["Texto", "Archivo", "Verificar"])

# ---------- Controles comunes ----------
def controles_hash(prefix=""):
    col1, col2 = st.columns([1,1])
    with col1:
        algo = st.selectbox(
            "Algoritmo",
            ["sha256","sha512","sha1","md5"],
            index=0,
            key=f"{prefix}_algo"
        )
    with col2:
        iterations = st.number_input("Iteraciones", 1, 1_000_000, 1, key=f"{prefix}_iters")
    salt = st.text_input("Salt (opcional)", key=f"{prefix}_salt", placeholder="p. ej. proyecto-2025")
    if algo in ("md5","sha1"):
        st.warning("MD5/SHA-1 están obsoletos para seguridad. Úsalos solo por compatibilidad.")
    return algo, salt, iterations

# ---------- TAB: Texto ----------
with tab_texto:
    texto = st.text_area("Texto a hashear", placeholder="Escribe el contenido…", height=120, key="texto_input")
    algo, salt, iters = controles_hash("texto")
    if st.button("Calcular hash", use_container_width=True, key="btn_texto"):
        if not texto:
            st.warning("Escribe algún texto primero.")
        else:
            hx = get_hash(texto, algo=algo, salt=salt, iterations=iters)
            st.success("Hash generado")
            st.code(hx, language="text")
            st.download_button("Descargar hash.txt", hx, file_name="hash.txt")

    # Mini demo de libs estándar
    with st.popover("Ver demo JSON/tiempo"):
        st.json({"now_epoch": int(time.time()), "ejemplo": ["a","b","c"]})

# ---------- TAB: Archivo ----------
with tab_archivo:
    up = st.file_uploader("Sube un archivo para calcular su hash", type=None, key="uploader")
    algo_f, salt_f, iters_f = controles_hash("file")
    if st.button("Calcular hash de archivo", use_container_width=True, key="btn_file"):
        if not up:
            st.warning("Sube un archivo primero.")
        else:
            # Leemos por chunks para no saturar memoria en archivos grandes
            digest = getattr(hashlib, algo_f)()
            if salt_f:
                digest.update(salt_f.encode("utf-8"))
            for chunk in iter(lambda: up.read(8192), b""):
                digest.update(chunk)
            raw = digest.digest()
            for _ in range(iters_f - 1):
                raw = _hash_once(raw, algo_f)
            hx = raw.hex()
            st.success(f"Hash {algo_f} del archivo")
            st.code(hx, language="text")
            st.download_button("Descargar hash.txt", hx, file_name=f"{up.name}.{algo_f}.txt")

# ---------- TAB: Verificar ----------
with tab_verificar:
    st.write("Compara si un contenido coincide con un hash esperado.")
    texto_v = st.text_area("Texto/Contenido", placeholder="Pega el contenido a verificar…", height=120, key="verify_text")
    expected = st.text_input("Hash esperado (hex)", placeholder="64 hex para sha256, 128 para sha512…", key="verify_expected")
    algo_v, salt_v, iters_v = controles_hash("verify")
    if st.button("Verificar", use_container_width=True, key="btn_verify"):
        if not texto_v or not expected:
            st.warning("Rellena el contenido y el hash esperado.")
        else:
            got = get_hash(texto_v, algo=algo_v, salt=salt_v, iterations=iters_v)
            ok = (got.lower().strip() == expected.lower().strip())
            st.write("Hash calculado:")
            st.code(got, language="text")
            if ok:
                st.success("✅ Coincide: el contenido corresponde al hash esperado.")
            else:
                st.error("❌ No coincide: el contenido NO corresponde al hash esperado.")

# ---------- Pie ----------
st.divider()
st.caption("Tip: guarda `requirements.txt` con `streamlit` y despliega en Streamlit Community Cloud.")

