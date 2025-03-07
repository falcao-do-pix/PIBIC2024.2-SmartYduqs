import 'package:aluno_qr_app/login_page.dart';
import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:qr_flutter/qr_flutter.dart';
import 'cadastro_page.dart'; // Tela de cadastro

class AutenticacaoPage extends StatefulWidget {
  @override
  _AutenticacaoPageState createState() => _AutenticacaoPageState();
}

class _AutenticacaoPageState extends State<AutenticacaoPage> {
  String? qrCodeData;
  String? alunoNome;

  // Função para deslogar
  Future<void> _logout() async {
    await FirebaseAuth.instance.signOut();
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (context) => LoginPage()), // Redireciona para a página de cadastro após o logout
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        title: Text('Autenticação', style: TextStyle(color: Colors.white)),
        backgroundColor: Colors.purple,
        centerTitle: true,
      ),
      body: FutureBuilder<User?>(
        future: FirebaseAuth.instance.authStateChanges().first, // Checando se o usuário está autenticado
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return Center(child: CircularProgressIndicator()); // Enquanto aguarda o estado da autenticação
          }

          if (snapshot.hasError) {
            return Center(child: Text('Erro ao carregar: ${snapshot.error}'));
          }

          User? user = snapshot.data;
          if (user == null) {
            // Se o usuário não estiver autenticado, redireciona para o login
            WidgetsBinding.instance.addPostFrameCallback((_) {
              Navigator.pushReplacement(
                context,
                MaterialPageRoute(builder: (context) => CadastroPage()), // Página de cadastro ou login
              );
            });
            return SizedBox.shrink();
          }

          // Se o usuário estiver autenticado, busca os dados no Firestore
          return FutureBuilder<DocumentSnapshot>(
            future: FirebaseFirestore.instance.collection('alunos').doc(user.uid).get(),
            builder: (context, alunoSnapshot) {
              if (alunoSnapshot.connectionState == ConnectionState.waiting) {
                return Center(child: CircularProgressIndicator());
              }

              if (!alunoSnapshot.hasData || !alunoSnapshot.data!.exists) {
                return Center(
                  child: Text(
                    'Dados do aluno não encontrados!',
                    style: TextStyle(color: Colors.red, fontSize: 16),
                  ),
                );
              }

              var alunoData = alunoSnapshot.data!;
              alunoNome = alunoData['nome'] ?? 'Aluno';
              qrCodeData = 'matricula:${alunoData['matricula']}';

              return Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
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
                    Text(
                      'Olá, $alunoNome',
                      style: TextStyle(color: Colors.white, fontSize: 18),
                    ),
                    SizedBox(height: 20),
                    QrImageView(
                      data: qrCodeData!,
                      version: QrVersions.auto,
                      size: 200.0,
                      foregroundColor: Colors.black,
                      backgroundColor: Colors.white,
                    ),
                    Spacer(),
                    Text(
                      'Wyden',
                      style: TextStyle(
                        color: Colors.purple,
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    SizedBox(height: 20),
                    ElevatedButton(
                      onPressed: _logout,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.red, // Alterado para backgroundColor
                        padding: EdgeInsets.symmetric(horizontal: 40, vertical: 14),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                      ),
                      child: Text(
                        'Logout',
                        style: TextStyle(fontSize: 16),
                      ),
                    ),
                    SizedBox(height: 40),
                  ],
                ),
              );
            },
          );
        },
      ),
    );
  }
}
