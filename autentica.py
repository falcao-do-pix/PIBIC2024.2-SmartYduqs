import cv2
from cryptography.fernet import Fernet
import mysql.connector
from mysql.connector import Error
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
        print(f"Erro ao conectar ao MySQL: {e}")
        return None

# Função para descriptografar a senha
def descriptografar_senha(senha_criptografada, chave):
    fernet = Fernet(chave)
    return fernet.decrypt(senha_criptografada).decode('utf-8')

# Função para ler QR Code da imagem capturada usando OpenCV
def ler_qr_code(imagem):
    detector = cv2.QRCodeDetector()
    data, bbox, _ = detector.detectAndDecode(imagem)
    if bbox is not None:
        return data
    return None

# Função para autenticar o aluno usando os dados do QR Code
def autenticar_aluno(dados_qr):
    try:
        # Conectar ao banco de dados
        conexao = conectar()
        if conexao:
            cursor = conexao.cursor()

            # Extrair matrícula e senha criptografada do QR Code
            try:
                info = re.search(r'Matrícula: (\d+), Senha criptografada: (.+)', dados_qr)
                if info:
                    matricula = int(info.group(1))  # Converter matrícula para inteiro
                    senha_criptografada_qr = info.group(2).encode()  # A senha do QR Code já vem como string, precisamos convertê-la para bytes
                    print(f"Matrícula extraída do QR Code: {matricula}")
                    print(f"Senha criptografada extraída do QR Code: {senha_criptografada_qr.decode()}")
                else:
                    print("Formato do QR Code inválido.")
                    return
            except Exception as e:
                print(f"Erro ao processar dados do QR Code: {e}")
                return

            # Recuperar a chave de criptografia e a senha criptografada do banco de dados
            query = "SELECT senha, chave_criptografia FROM alunos WHERE matricula = %s"
            print(f"Executando query SQL: {query} com matrícula {matricula}")
            cursor.execute(query, (matricula,))
            resultado = cursor.fetchone()

            if resultado:
                senha_criptografada_banco, chave_criptografia_banco = resultado

                # Se a senha for um número inteiro, converta-a para string e depois para bytes
                if isinstance(senha_criptografada_banco, int):
                    senha_criptografada_banco = str(senha_criptografada_banco).encode()  # Converter de int para bytes

                # Verificar se a chave já está em bytes
                if isinstance(chave_criptografia_banco, str):
                    chave_criptografia_banco = chave_criptografia_banco.encode()  # Convertendo a chave para bytes apenas se for uma string

                # Descriptografar a senha do banco de dados
                try:
                    senha_descriptografada_banco = descriptografar_senha(senha_criptografada_banco, chave_criptografia_banco)
                    print(f"Senha descriptografada do banco de dados: {senha_descriptografada_banco}")

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
    # Configurar captura de vídeo da câmera
    cap = cv2.VideoCapture(0)  # 0 para a câmera padrão

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Não foi possível capturar imagem da câmera.")
            break

        # Decodificar QR Code da imagem capturada
        dados_qr = ler_qr_code(frame)
        if dados_qr:
            print(f"Dados do QR Code: {dados_qr}")

            # Autenticar o aluno com os dados do QR Code
            autenticar_aluno(dados_qr)
            break

        # Mostrar o vídeo em uma janela
        cv2.imshow('QR Code Scanner', frame)

        # Sair do loop se a tecla 'q' for pressionada
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Libere a captura e feche as janelas
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
