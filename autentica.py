import cv2
import numpy as np
import streamlit as st
from cryptography.fernet import Fernet
import mysql.connector
from mysql.connector import Error
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

# Função para escanear o QR code e autenticar (adaptado para Streamlit)
def autenticar_qr_code():
    # Verificar se a variável de estado "parar" já foi inicializada
    if "parar" not in st.session_state:
        st.session_state.parar = False  # Inicializa o estado como False
    
    cap = cv2.VideoCapture(0)
    detector = cv2.QRCodeDetector()

    frameST = st.empty()  # Espaço reservado para o feed de vídeo
    mensagem = st.empty()  # Espaço reservado para a mensagem de validação

    # Laço para capturar o QR Code
    while not st.session_state.parar:  # Mantém o loop enquanto o botão "Parar" não for clicado
        ret, frame = cap.read()
        if not ret:
            st.error("Erro ao acessar a câmera.")
            break

        # Detectar e decodificar o QR code no frame
        data, bbox, _ = detector.detectAndDecode(frame)

        if bbox is not None:  # Se houver um QR code detectado, desenhar bordas ao redor dele
            bbox = bbox.astype(int)  # Convertendo para inteiros
            for i in range(len(bbox)):
                pt1 = tuple(bbox[i][0])
                pt2 = tuple(bbox[(i + 1) % len(bbox)][0])
                cv2.line(frame, pt1, pt2, color=(255, 0, 0), thickness=2)

            if data:  # Se o QR code foi lido corretamente
                matricula, senha_criptografada = processar_dados_qr(data)
                
                if matricula and senha_criptografada:
                    resultado = autenticar_matricula(matricula, senha_criptografada)
                    if resultado:
                        mensagem.success(f"Autenticação bem-sucedida para a matrícula {matricula}.")
                    else:
                        mensagem.error("Autenticação falhou. Matrícula ou senha incorreta.")
        
        # Exibir o frame na interface
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(frame_rgb)
        frameST.image(img_pil, channels="RGB")

    cap.release()
    cv2.destroyAllWindows()

# Função para processar os dados do QR code (split na matrícula e senha)
def processar_dados_qr(data):
    try:
        dados = data.split(",")
        matricula = dados[0].split(":")[1].strip()
        senha_criptografada = bytes(dados[1].split(":")[1].strip(), 'utf-8')
        return matricula, senha_criptografada
    except Exception as e:
        st.error(f"Erro ao processar QR Code: {e}")
        return None, None

# Função para autenticar a matrícula no banco de dados
def autenticar_matricula(matricula, senha_criptografada):
    conexao = conectar()
    if conexao:
        cursor = conexao.cursor()

        # Recuperar os dados do aluno no banco
        query = "SELECT chave_criptografia FROM alunos WHERE matricula = %s"
        cursor.execute(query, (matricula,))
        resultado = cursor.fetchone()

        if resultado:
            chave_criptografia_banco = resultado[0]  # Chave de criptografia (em bytes)

            # Descriptografar a senha do QR code e comparar com a armazenada
            senha_descriptografada = descriptografar_senha(senha_criptografada, chave_criptografia_banco)
            if senha_descriptografada:
                return True
        else:
            st.error("Matrícula não encontrada.")
    return False

# Função principal para exibir a interface do QR code
def main():
    st.title("Autenticação via QR Code")
    st.write("Aponte o QR Code para a câmera para autenticar.")
    
    if st.button("Iniciar Captura", key="start_button"):
        st.session_state.parar = False  # Resetar o estado parar ao iniciar a captura
        autenticar_qr_code()

    # Botão "Parar" com chave única fora do loop de captura
    if st.button("Parar Captura", key="unique_stop_button"):
        st.session_state.parar = True  # Alterar o estado para parar a captura

    # Se o botão "Parar" foi clicado
    if st.session_state.get("parar"):
        st.success("Captura interrompida.")

if __name__ == "__main__":
    main()
