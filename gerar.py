import streamlit as st
import mysql.connector
from mysql.connector import Error
from cryptography.fernet import Fernet
import qrcode
from io import BytesIO

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

# Função para gerar QR code com a senha criptografada do banco de dados
def gerar_qr_code(matricula, senha_criptografada):
    data = f'Matrícula: {matricula}, Senha criptografada: {senha_criptografada.decode()}'
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill='black', back_color='white')
    
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.getvalue()

# Função para autenticar o aluno e gerar o QR code com a senha criptografada
def autenticar_e_gerar_qr(matricula, senha):
    try:
        conexao = conectar()
        if conexao:
            cursor = conexao.cursor()

            # Recuperar os dados do aluno
            query = "SELECT senha, chave_criptografia FROM alunos WHERE matricula = %s"
            cursor.execute(query, (matricula,))
            resultado = cursor.fetchone()

            if resultado:
                senha_criptografada_banco = resultado[0]  # Senha criptografada (em bytes)
                chave_criptografia_banco = resultado[1]  # Chave de criptografia (em bytes)

                # Descriptografar a senha armazenada no banco
                senha_descriptografada = descriptografar_senha(senha_criptografada_banco, chave_criptografia_banco)

                # Verificar se a senha inserida é igual à senha descriptografada
                if senha == senha_descriptografada:
                    # Gerar o QR code com a senha criptografada do banco de dados
                    qr_code_bytes = gerar_qr_code(matricula, senha_criptografada_banco)
                    st.image(BytesIO(qr_code_bytes), caption="QR Code do aluno")
                else:
                    st.error("Senha incorreta.")
            else:
                st.error("Matrícula não encontrada.")
        else:
            st.error("Erro ao conectar ao banco de dados.")
    except Exception as e:
        st.error(f"Erro ao autenticar: {e}")

# Interface do Streamlit
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>Autenticação do Aluno e Geração de QR Code</h1>", unsafe_allow_html=True)

matricula = st.text_input("Matrícula (12 caracteres):", max_chars=12, placeholder="Digite sua matrícula")
senha = st.text_input("Senha:", type="password")

if st.button("Gerar QR Code"):
    autenticar_e_gerar_qr(matricula, senha)
