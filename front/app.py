import streamlit as st
import base64
import requests
from PIL import Image

# === Affichage du logo + titre ===
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def display_logo_header(png_file_path):
    logo_base64 = get_base64_of_bin_file(png_file_path)
    html_code = f"""
    <div style="text-align: center; margin-top: 10px; margin-bottom: 10px;">
        <img src="data:image/png;base64,{logo_base64}" width="700"/>
    </div>
    """
    st.markdown(html_code, unsafe_allow_html=True)

# 🧠 Appel de l'en-tête (tout en haut)
display_logo_header("logo.png")

# === Interface utilisateur ===

# Input texte
text_input = st.text_input("Entrez un message :")

# Input image
image_file = st.file_uploader("Choisissez une image", type=["png", "jpg", "jpeg"])

# Bouton d'envoi
if st.button("Envoyer"):

    if not text_input or not image_file:
        st.warning("Veuillez remplir le texte et choisir une image.")
    else:
        # Préparer les données
        files = {
            "image": (image_file.name, image_file, image_file.type),
        }
        data = {
            "text": text_input,
        }

        try:
            # ⚠️ Remplace cette URL par celle de ton API FastAPI réelle
            response = requests.post("http://pipeline:8080/upload", data=data, files=files)

            if response.status_code == 200:
                st.success("Succès : " + response.text)
            else:
                st.error(f"Erreur {response.status_code} : {response.text}")
        except Exception as e:
            st.error(f"Erreur de requête : {e}")

# Bouton de test GET
if st.button("Test"):
    try:
        response = requests.get("http://pipeline:8000/")
        if response.status_code == 200:
            st.success("Succès : " + response.text)
        else:
            st.error(f"Erreur {response.status_code} : {response.text}")
    except Exception as e:
        st.error(f"Erreur de requête : {e}")
