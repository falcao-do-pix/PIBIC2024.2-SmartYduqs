from flask import Flask, render_template, request, redirect, url_for
import qrcode
import hashlib
import os

app = Flask(__name__)

# Define the directory where QR codes will be saved
app.config['UPLOAD_FOLDER'] = os.path.join('templates','static', 'qr_codes')

# Ensure the directory exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Main route to display the form
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        matricula = request.form.get('matricula')
        senha = request.form.get('senha')

        # Basic validation
        if not matricula or not senha:
            return "Error: Matricula and Senha cannot be empty", 400

        # Generate a random salt
        salt = os.urandom(16)

        # Combine the student ID and salt
        data = senha + salt.hex()

        # Create a SHA-256 hash of the data
        hash_data = hashlib.sha256(data.encode()).hexdigest()

        # Generate QR code from the hash_data (you can use libraries like `qrcode` for this)
        # Generate QR code content
        qr_data = f"{matricula},{hash_data}"

        # Generate the QR code
        qr_img = qrcode.make(qr_data)

        # Define the path to save the image
        qr_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{matricula}.png")

        # Save the QR code image
        qr_img.save(qr_path)

        return redirect(url_for('qrcode_display', filename=f"{matricula}.png"))

    return render_template('index.html')

# Route to display the generated QR code
@app.route('/qrcode/<filename>')
def qrcode_display(filename):
    return render_template('qrcode.html', filename=filename)

if __name__ == '__main__':
    app.run(debug=True)
