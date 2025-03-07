import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'login_page.dart'; // Importa a tela de login correta

class CadastroPage extends StatefulWidget {
  @override
  _CadastroPageState createState() => _CadastroPageState();
}

class _CadastroPageState extends State<CadastroPage> {
  final _formKey = GlobalKey<FormState>();
  final _nomeController = TextEditingController();
  final _matriculaController = TextEditingController();
  final _emailController = TextEditingController();
  final _cursoController = TextEditingController();
  final _telefoneController = TextEditingController();
  final _senhaController = TextEditingController();
  bool _loading = false; // Para exibir o indicador de carregamento

  Future<void> cadastrarAluno() async {
    if (_formKey.currentState!.validate()) {
      setState(() => _loading = true);

      String nome = _nomeController.text.trim();
      String matricula = _matriculaController.text.trim();
      String email = _emailController.text.trim();
      String curso = _cursoController.text.trim();
      String telefone = _telefoneController.text.trim();
      String senha = _senhaController.text.trim();

      try {
        // Verifica se a matrícula já está cadastrada
        var matriculaExistente = await FirebaseFirestore.instance
            .collection('alunos')
            .where('matricula', isEqualTo: matricula)
            .get();

        if (matriculaExistente.docs.isNotEmpty) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Matrícula já cadastrada!')),
          );
          return;
        }

        // Cadastra o usuário no Firebase Authentication
        UserCredential userCredential = await FirebaseAuth.instance
            .createUserWithEmailAndPassword(email: email, password: senha);

        // Salva os dados no Firestore
        await FirebaseFirestore.instance.collection('alunos').doc(userCredential.user!.uid).set({
          'uid': userCredential.user!.uid,
          'nome': nome,
          'matricula': matricula,
          'email': email,
          'curso': curso,
          'telefone': telefone,
          'qrCode': 'matricula:$matricula', // Dados do QR Code
        });

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Cadastro realizado com sucesso!')),
        );

        // ✅ Direciona para a tela de login
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (context) => LoginPage()), // Agora leva para a página de login
        );
      } catch (e) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Erro ao cadastrar: $e')),
        );
      } finally {
        setState(() => _loading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        title: Text('Cadastro', style: TextStyle(color: Colors.white)),
        backgroundColor: Colors.purple,
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        padding: EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Align(
                alignment: Alignment.topLeft,
                child: Text(
                  'Smart Yduqs',
                  style: TextStyle(
                    color: Colors.orange,
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              SizedBox(height: 20),
              _buildTextField(_nomeController, 'Nome'),
              _buildTextField(_matriculaController, 'Matrícula'),
              _buildTextField(_emailController, 'Email'),
              _buildTextField(_cursoController, 'Curso'),
              _buildTextField(_telefoneController, 'Telefone'),
              _buildTextField(_senhaController, 'Senha', obscureText: true),
              SizedBox(height: 30),
              Center(
                child: _loading
                    ? CircularProgressIndicator() // Exibe indicador de carregamento
                    : ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.purple,
                    padding: EdgeInsets.symmetric(horizontal: 40, vertical: 14),
                  ),
                  onPressed: cadastrarAluno,
                  child: Text(
                    'Cadastrar',
                    style: TextStyle(fontSize: 16, color: Colors.white),
                  ),
                ),
              ),
              SizedBox(height: 20),
              Center(
                child: TextButton(
                  onPressed: () {
                    // Ao clicar em 'Já tem uma conta?', vai para a tela de login
                    Navigator.pushReplacement(
                      context,
                      MaterialPageRoute(builder: (context) => LoginPage()), // Agora leva para a tela de login correta
                    );
                  },
                  child: Text(
                    'Já tem uma conta? Faça login',
                    style: TextStyle(color: Colors.orange, fontSize: 16),
                  ),
                ),
              ),
              SizedBox(height: 30),
              Center(
                child: Text(
                  'Wyden',
                  style: TextStyle(
                    color: Colors.purple,
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  // Função que constrói os campos de texto
  Widget _buildTextField(TextEditingController controller, String label, {bool obscureText = false}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16.0),
      child: TextFormField(
        controller: controller,
        obscureText: obscureText,
        style: TextStyle(color: Colors.white),
        decoration: InputDecoration(
          labelText: label,
          labelStyle: TextStyle(color: Colors.white),
          filled: true,
          fillColor: Colors.white10,
          border: OutlineInputBorder(),
        ),
        validator: (value) {
          if (value == null || value.isEmpty) return 'Insira seu $label';
          return null;
        },
      ),
    );
  }
}
