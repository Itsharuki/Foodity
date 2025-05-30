import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:mobile_ecom_foodity/Url/AllUrl.dart';
import 'package:mobile_ecom_foodity/Cookies/dio_cookie.dart';


class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {

//############################################//
//#############  B A C K  E N D  #############//
//############################################//

final TextEditingController _email = TextEditingController(); //get value from text box
final TextEditingController _password = TextEditingController();
String loginResponse = ''; //output from back end
String loginMessage = ''; //message from backend code

//#######################################//
//#############  L O G I N  #############//
//#######################################//

Future<void> loginData() async{
  final url = Uri.parse('$globalurl/loginMobile'); //pass url

  final response = await DioCookie.dio.post(
    '$globalurl/loginMobile',
    data: jsonEncode({
      'email': _email.text,
      'password': _password.text
    }),
    );
    DioCookie.dio.options.connectTimeout = Duration(seconds: 90);
    DioCookie.dio.options.receiveTimeout = Duration(seconds: 90);

  final decoded = response.data; //conversion of json to dart

  setState(() {
    loginResponse = decoded['message'];
    if (loginResponse == 'buyer') {
      setState(() {
        loginMessage = 'Login successful';
        Navigator.pushNamed(context, '/buyerHome');
      });
    }else if (loginResponse == 'courier'){
      setState(() {
        loginMessage = 'Logged in successfully';
        Navigator.pushNamed(context, '/courierHome');
      });
    }else if (loginResponse == 'restricted'){
      setState(() {
        loginMessage = 'Account is restricted';
      });
    }else if (loginResponse == 'approval'){
      setState(() {
        loginMessage = 'Account is still for approval';
      });
    }else{
      setState(() {
        loginMessage = 'Invalid email or password';
      });
    }
    print(decoded['status']);
  });
}


//##############################################//
//#############  F R O N T  E N D  #############//
//##############################################//

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          image: DecorationImage(image: AssetImage('assets/login/all_bg.png'), fit: BoxFit.cover)
        ),

      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(height: 150,),
          Expanded(
            
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Container(width: 20,
                ),
                Expanded(
                  child: Container(
                    decoration: BoxDecoration(
                      image: DecorationImage(image: AssetImage('assets/login/Container.png'), fit: BoxFit.fill)
                    ),
                    child: Row(
                      children: [
                        Container(width: 10,),
                        Expanded(
                          child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Spacer(),
                            Expanded(
                              child: Align(alignment: Alignment.topCenter, child: Container(width: 250,child: Image.asset('assets/login/foodity_logo.png',width: 400, fit: BoxFit.contain,)),)),
                              Container(height: 40,),
                            Expanded(child: Container(width: 320,child: TextField(
                              controller: _email,
                              decoration: InputDecoration(
                                labelText: 'Enter your email',
                                border: OutlineInputBorder(),),),)),
                                Container(height: 20,),
                                Expanded(child: Container(width: 320,child: TextField(
                                  controller: _password,
                                  obscureText: true,
                              decoration: InputDecoration(
                                labelText: 'Enter your password',
                                border: OutlineInputBorder(),),),)),
                                Container(height: 20, child: Text('$loginMessage'),),
                                Expanded(child: Container(height: 50,child: ElevatedButton(
                                  onPressed: (){
                                    loginData();
                                  }, style: ElevatedButton.styleFrom(fixedSize: Size(320, 50),foregroundColor: Colors.white, backgroundColor: Color.fromRGBO(76, 0, 163, 1), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)), padding: EdgeInsets.symmetric(vertical: 5, horizontal: 30)), child: Text('Login', style: TextStyle(fontSize: 15, fontFamily: 'RadioCanada', fontWeight: FontWeight.bold),)),)),
                                Container(height: 10,),
                                Expanded(child: GestureDetector(
                                  onTap: () async {
                                    print('link is pressed');
                                  },
                                  child: Text('Forgot Password?', style: TextStyle(decoration: TextDecoration.underline, fontWeight: FontWeight.bold))
                                ),
                                  ),
                                Spacer()
                                ],),),
                            Container(
                                  width: 10,
                                )
                                ],
                        ) 
                    
                    
                  )
                    
                ),
                Container(width: 20,
                ),
              ],
            )
            ),
            Container(height: 150,),
        ],
      ),

      ),
    );
  }
}