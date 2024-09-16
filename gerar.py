import streamlit as st
import mysql.connector
from mysql.connector import Error
from cryptography.fernet import Fernet
import io
from PIL import Image

# Função para conectar ao banco de dados MySQL
def conectar():
    try:
        conexao = mysql.connector.connect(
            host='localhost',
            database='smart_yduqs',
            user='vitor',
            password='Jkl73198246@'
        )
        if conexao.is_connected():
            return conexao
    except Error as e:
        st.error(f"Erro ao conectar ao MySQL: {e}")
        return None

# Função para descriptografar a senha
def descriptografar_senha(senha_criptografada, chave):
    fernet = Fernet(chave)
    return fernet.decrypt(senha_criptografada).decode('utf-8')

# Função para autenticar o aluno e recuperar o QR code
def autenticar_e_recuperar_qr(matricula, senha):
    try:
        conexao = conectar()
        if conexao:
            cursor = conexao.cursor()
            
            # Recuperar os dados do aluno
            query = "SELECT senha, qr_code, chave_criptografia FROM alunos WHERE matricula = %s"
            cursor.execute(query, (matricula,))
            resultado = cursor.fetchone()

            if resultado:
                senha_criptografada_banco = resultado[0]  # Já está em bytes
                qr_code_bytes = resultado[1]
                chave_criptografia_banco = resultado[2]  # Já está em bytes

                # Descriptografar a senha
                senha_descriptografada = descriptografar_senha(senha_criptografada_banco, chave_criptografia_banco)
                
                # Verificar a senha
                if senha == senha_descriptografada:
                    # Exibir o QR code
                    st.image(io.BytesIO(qr_code_bytes), caption="QR Code do aluno")
                else:
                    st.error("Senha incorreta.")
            else:
                st.error("Matrícula não encontrada.")
        else:
            st.error("Erro ao conectar ao banco de dados.")
    except Exception as e:
        st.error(f"Erro ao autenticar: {e}")

# Interface do Streamlit
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>Autenticação do Aluno</h1>", unsafe_allow_html=True)

matricula = st.text_input("Matrícula (12 caracteres):", max_chars=12, placeholder="Digite sua matrícula")
senha = st.text_input("Senha:", type="password")

if st.button("Recuperar QR Code"):
    autenticar_e_recuperar_qr(matricula, senha)
