import streamlit as st
import mysql.connector
from mysql.connector import Error
from cryptography.fernet import Fernet
import re

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

# Função para validar a senha
def validar_senha(senha):
    if (len(senha) < 8 or
        not re.search(r'[A-Z]', senha) or
        not re.search(r'[0-9]', senha) or
        not re.search(r'[!@#$%^&*(),.?":{}|<>]', senha)):
        return False
    return True

# Função para criptografar a senha
def criptografar_senha(senha, chave):
    fernet = Fernet(chave)
    senha_criptografada = fernet.encrypt(senha.encode())
    return senha_criptografada

# Função para cadastrar aluno no banco de dados
def cadastrar_aluno(conexao, matricula, nome, email, senha_criptografada, chave_byte):
    try:
        query = "INSERT INTO alunos (matricula, nome, email, senha, chave_criptografia) VALUES (%s, %s, %s, %s, %s)"
        cursor = conexao.cursor()
        cursor.execute(query, (matricula, nome, email, senha_criptografada, chave_byte))
        conexao.commit()
        st.success("Cadastro realizado com sucesso!")
    except Error as e:
        st.error(f"Erro ao cadastrar aluno: {e}")
    finally:
        if conexao.is_connected():
            cursor.close()

# Interface do Streamlit
# Exibe o logo no topo
st.image("img1.png", width=200)

st.markdown("<h1 style='text-align: center; color: #4CAF50;'>Cadastro de Alunos</h1>", unsafe_allow_html=True)

matricula = st.text_input("Matrícula (12 caracteres):", max_chars=12, placeholder="Digite sua matrícula")
nome = st.text_input("Nome completo:")
email = st.text_input("Email:")
senha = st.text_input("Senha:", type="password", help="A senha deve conter pelo menos 8 caracteres, incluindo uma letra maiúscula, um número e um símbolo especial.")

if st.button("Cadastrar"):
    if not (nome and email and matricula.isdigit() and len(matricula) == 12):
        st.warning("Por favor, preencha todos os campos corretamente.")
    elif not validar_senha(senha):
        st.warning("A senha deve ter pelo menos 8 caracteres, incluindo uma letra maiúscula, um número e um símbolo especial.")
    else:
        conexao = conectar()
        if conexao:
            chave = Fernet.generate_key()
            senha_criptografada = criptografar_senha(senha, chave)
            cadastrar_aluno(conexao, matricula, nome, email, senha_criptografada, chave)
            conexao.close()
