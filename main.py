import streamlit as st
from sistema import mostrar_cadastro_aluno
from gerar import mostrar_gerar_qr
import autentica

# Menu de navegação para escolher a funcionalidade
st.sidebar.title("Menu")
escolha = st.sidebar.radio("Navegar", ["Cadastro de Aluno", "Gerar QR Code", "Autenticação QR Code"])

# Exibir a página correspondente à escolha
if escolha == "Cadastro de Aluno":
    mostrar_cadastro_aluno()
elif escolha == "Gerar QR Code":
    mostrar_gerar_qr()
elif escolha == "Autenticação QR Code":
    st.warning("A autenticação via QR Code é feita pela câmera externa e não é exibida no Streamlit.")
    autentica.main()  # Executa a função de autenticação QR via câmera
