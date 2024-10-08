import cv2
import numpy as np
from cryptography.fernet import Fernet
import mysql.connector
from mysql.connector import Error
import re

# Função para conectar ao banco de dados MySQL
def conectar():
    try:
        print("Tentando conectar ao banco de dados...")
        conexao = mysql.connector.connect(
            host='localhost',
            database='smart_yduqs',
            user='vitor',
            password='Jkl73198246@'
        )
        if conexao.is_connected():
            print("Conexão com o banco de dados bem-sucedida.")
            return conexao
    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return None

# Função para descriptografar a senha
def descriptografar_senha(senha_criptografada, chave):
    fernet = Fernet(chave)
    return fernet.decrypt(senha_criptografada).decode('utf-8')

# Função para ler QR Code da imagem capturada
def ler_qr_code(imagem):
    print("Tentando ler o QR Code...")
    detector = cv2.QRCodeDetector()
    data, bbox, _ = detector.detectAndDecode(imagem)
    if bbox is not None:
        print("QR Code detectado!")
        return data
    return None

# Função para autenticar o aluno usando os dados do QR Code
def autenticar_aluno(dados_qr):
    try:
        print(f"Tentando autenticar o aluno com os dados: {dados_qr}")
        conexao = conectar()
        if conexao:
            cursor = conexao.cursor()

            # Extrair matrícula e senha criptografada do QR Code
            try:
                info = re.search(r'Matrícula: (\d+), Senha criptografada: (.+)', dados_qr)
                if info:
                    matricula = int(info.group(1))  # Converter matrícula para inteiro
                    senha_criptografada_qr = info.group(2).encode()  # A senha do QR Code já vem como bytes
                    print(f"Matrícula extraída: {matricula}")
                else:
                    print("Formato do QR Code inválido.")
                    return
            except Exception as e:
                print(f"Erro ao processar dados do QR Code: {e}")
                return

            # Recuperar a chave de criptografia e a senha criptografada do banco de dados
            query = "SELECT senha, chave_criptografia FROM alunos WHERE matricula = %s"
            cursor.execute(query, (matricula,))
            resultado = cursor.fetchone()

            if resultado:
                senha_criptografada_banco, chave_criptografia_banco = resultado

                # Verificar se a chave já está em bytes
                if isinstance(chave_criptografia_banco, str):
                    chave_criptografia_banco = chave_criptografia_banco.encode()

                # Descriptografar a senha do banco de dados
                try:
                    senha_descriptografada_banco = descriptografar_senha(senha_criptografada_banco, chave_criptografia_banco)

                    # Comparar a senha descriptografada com a senha criptografada do QR Code
                    if senha_criptografada_qr == senha_criptografada_banco:
                        print("Acesso liberado!")
                    else:
                        print("Acesso negado: senha não confere.")
                except Exception as e:
                    print(f"Erro ao descriptografar senha: {e}")
            else:
                print(f"Matrícula {matricula} não encontrada no banco de dados.")
        else:
            print("Erro ao conectar ao banco de dados.")
    except Exception as e:
        print(f"Erro ao autenticar: {e}")

# Função principal para capturar e processar QR Code
def main():
    esp32_url = 'http://192.168.137.183:81/stream'  # Substitua pelo IP da sua ESP32-CAM

    # Configura captura de vídeo
    cap = cv2.VideoCapture(esp32_url)  # Abre o feed da ESP32-CAM

    if not cap.isOpened():
        print("Erro ao abrir o stream da ESP32-CAM.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Falha ao capturar frame.")
            break

        # Decodificar QR Code da imagem capturada
        dados_qr = ler_qr_code(frame)
        if dados_qr:
            print(f"Dados do QR Code: {dados_qr}")

            # Autenticar o aluno com os dados do QR Code
            autenticar_aluno(dados_qr)
            # Após autenticação, o loop continua para novas tentativas

        # Mostrar o vídeo em uma janela
        cv2.imshow('ESP32-CAM QR Code Scanner', frame)

        # Sair do loop se a tecla 'q' for pressionada
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Saindo do loop.")
            break

    # Libere a captura e feche as janelas
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
