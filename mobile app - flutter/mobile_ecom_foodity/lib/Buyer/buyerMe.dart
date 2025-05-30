import 'package:flutter/material.dart';
import 'package:mobile_ecom_foodity/Buyer/buyerHome.dart';
import 'package:mobile_ecom_foodity/Url/AllUrl.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:typed_data';
import 'package:mobile_ecom_foodity/Cookies/dio_cookie.dart';

class Product {
  final int product_id;
  final String product_name;
  final String product_description;
  final double item_total_amount;
  final int order_quantity;
  final String base64Image;

  Product({
    required this.product_id,
    required this.product_name,
    required this.product_description,
    required this.item_total_amount,
    required this.order_quantity,
    required this.base64Image
    });

  factory Product.fromJson(Map <String, dynamic> json) {
    return Product(
      product_id: json['product_id'],
      product_name: json['product_name'],
      product_description: json['product_description'],
      item_total_amount: double.tryParse(json['item_total_amount'].toString()) ?? 0.0,
      order_quantity: json['order_quantity'],
      base64Image: json['product_photo'] ?? '',
      );
  }

  Map<String, dynamic> toJson() {
    return {
      'product_id': product_id,
      'product_name': product_name,
      'product_description': product_description,
      'item_total_amount': item_total_amount,
      'order_quantity': order_quantity,
      'product_photo': base64Image,
    };
  }
}

class User {
  final int accounts_id;
  final String firstName;
  final String lastName;
  final String email;
  final String password;
  final String barangay;
  final String city;
  final String province;
  final String zip_code;
  final String account_type;
  final String base64Image;

  User({
    required this.accounts_id,
    required this.firstName,
    required this.lastName,
    required this.email,
    required this.password,
    required this.barangay,
    required this.city,
    required this.province,
    required this.zip_code,
    required this.account_type,
    required this.base64Image
    });

  factory User.fromJson(Map <String, dynamic> json) {
    return User(
      accounts_id: json['accounts_id'],
      firstName: json['firstName'],
      lastName: json['lastName'],
      email: json['email'],
      password: json['password'],
      barangay: json['barangay'],
      city: json['city'],
      province: json['province'],
      zip_code: json['zip_code'],
      account_type: json['account_type'],
      base64Image: json['profile_pic_decoded'] ?? ''
      );
  }

  Map<String, dynamic> toJson() {
    return {
      'accounts_id': accounts_id,
      'firstName': firstName,
      'lastName': lastName,
      'email': email,
      'password': password,
      'barangay': barangay,
      'city': city,
      'province': province,
      'zip_code': zip_code,
      'account_type': account_type,
      'profile_pic_decoded': base64Image,
    };
  }
}


class BuyerMyProfile extends StatefulWidget {
  const BuyerMyProfile({super.key});

  @override
  State<BuyerMyProfile> createState() => _BuyerMyProfileState();
}

class _BuyerMyProfileState extends State<BuyerMyProfile> {
  List<dynamic> productList = [];
  List<User> userList = [];

//############################################//
//#############  B A C K  E N D  #############//
//############################################//

//################################//
//###  U S E R  D E T A I L S  ###//
//################################//

Future<void> getProfileDetails() async{

  try{
    final user = await DioCookie.dio.get(
    '$globalurl/getProfileDetails');
    
    if (user.statusCode == 200){
      var decoded = user.data;
      print(decoded);
      setState(() {
        userList = List<User>.from((decoded['profileDetails'] as List).map((user) => User.fromJson(user)).toList());
      });
    }
  }catch (e){ 
    print("Error searching user: $e");
  }
}


//##################################//
//###  I M A G E  H A N D L E R  ###//
//##################################//

Uint8List _safeDecodeImage(String base64String) { //safe decoding of image
  try {
    if (base64String.isEmpty) {
      throw Exception('Empty string');
    }

    final cleaned = base64String.replaceAll(RegExp(r'\s+'), '');
    return base64Decode(cleaned);
  }catch (e) {
    print('Error decoding image: $e');
    return Uint8List.fromList([
      0x89, 0x50, 0x4E, 0x47,
      0x0D, 0x0A, 0x1A, 0x0A,
      0x00, 0x00, 0x00, 0x0D,
      0x49, 0x48, 0x44, 0x52,
      0x00, 0x00, 0x00, 0x01,
      0x00, 0x00, 0x00, 0x01,
      0x08, 0x06, 0x00, 0x00,
      0x00, 0x1F, 0x15, 0xC4,
      0x89, 0x00, 0x00, 0x00,
      0x0A, 0x49, 0x44, 0x41,
      0x54, 0x78, 0x9C, 0x63,
      0x00, 0x01, 0x00, 0x00,
      0x05, 0x00, 0x01, 0x0D,
      0x0A, 0x2D, 0xB4, 0x00,
      0x00, 0x00, 0x00, 0x49,
      0x45, 0x4E, 0x44, 0xAE,
      0x42, 0x60, 0x82
    ]);
  }
}

//######################//
//###  L O G  O U T  ###//
//######################//

Future<void> productID() async{

    final response = await DioCookie.dio.post(
    '$globalurl/storeProductId',

    data: {
    },);
    print(response.statusCode);
    if (response.statusCode == 200){
      Navigator.pushNamed(context, '/buyerProductPage');
    }

}


//#########################//
//###  O V E R R I D E  ###//
//#########################//

@override
void initState() {
  super.initState();
  getProfileDetails();
}


//##############################################//
//#############  F R O N T  E N D  #############//
//##############################################//


  @override
  Widget build(BuildContext context) {
    return Scaffold(
      extendBodyBehindAppBar: true,
      appBar: AppBar(
      iconTheme: IconThemeData(color: Colors.white),
        backgroundColor: Colors.transparent,
        title: Row(
          children: [
            CircleAvatar(
              radius: 20,
              backgroundImage: userList.isNotEmpty 
              ? MemoryImage(_safeDecodeImage(userList[0].base64Image))
              : null,
            ),
            SizedBox(
              width: 10,
            ),
            Container(
              width: 120,
              child: Text(
              userList.isNotEmpty ? '${userList[0].email}' : 'name',
              style: TextStyle(
                color: Colors.white,
                fontSize: 15
              ),
              overflow: TextOverflow.ellipsis,
            ),
            )
            
          ],
        ),
        
        actions: [

          IconButton(
            onPressed: (){
            Navigator.pushNamed(context, '/buyerCart');
          },
          icon: Image(image: AssetImage('assets/icons/shopping_cart.png'))),
          IconButton(
            onPressed: (){
            },
            icon: Image(image: AssetImage('assets/icons/message.png')))
        ],
      ),
      body: Container(
        decoration: BoxDecoration(
          image: DecorationImage(image: AssetImage('assets/login/all_bg.png'), fit: BoxFit.cover)
        ),
        child: Expanded(
          child: SingleChildScrollView(
            child: Column(
              children: [
                SizedBox(
                  height: 100,
                ),
                Container(
                  height: 800,
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.only(
                      topLeft: Radius.elliptical(20,20),
                      topRight: Radius.elliptical(20,20)
                      )
                  ),
                  child: Padding(
                    padding: EdgeInsets.symmetric(
                      horizontal: 30,
                      vertical: 20
                    ),
                    child: Column(
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              'My Purchases'
                            ),
                            Text(
                              'View Purchase History >'
                            )
                          ],
                        ),
                        SizedBox(
                          height: 20,
                        ),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                          children: [
                            Container(
                              height: 70,
                              child: Column(
                                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                                children: [
                                  IconButton(onPressed: (){
                                    Navigator.pushNamed(context, '/buyerToPay');
                                  }, icon: Container(
                                    width: 30,
                                    height: 30,
                                    child: Image(image: AssetImage('assets/icons/wallet.png'), fit: BoxFit.contain,),
                                  ),
                                  iconSize: 20,
                                  ),
                                  Text(
                                    'To Pay',
                                    style: TextStyle(fontFamily: 'RadioCanada', fontSize: 12, fontWeight: FontWeight.w500),
                                  ),
                                ],
                              ),
                            ),
                            Container(
                              height: 70,
                              child: Column(
                                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                                children: [
                                  IconButton(onPressed: (){
                                    Navigator.pushNamed(context, '/buyerToShip');
                                  }, icon: Container(
                                    width: 30,
                                    height: 30,
                                    child: Image(image: AssetImage('assets/icons/delivery.png'), fit: BoxFit.contain,),
                                  ),
                                  iconSize: 20,
                                  ),
                                  Text(
                                    'To Ship',
                                    style: TextStyle(fontFamily: 'RadioCanada', fontSize: 12, fontWeight: FontWeight.w500),
                                  ),
                                ],
                              ),
                            ),
                            Container(
                              height: 70,
                              child: Column(
                                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                                children: [
                                  IconButton(onPressed: (){
                                    Navigator.pushNamed(context, '/buyerCompleted');
                                  }, icon: Container(
                                    width: 30,
                                    height: 30,
                                    child: Image(image: AssetImage('assets/icons/completed.png'), fit: BoxFit.contain,),
                                  ),
                                  iconSize: 20,
                                  ),
                                  Text(
                                    'Completed',
                                    style: TextStyle(fontFamily: 'RadioCanada', fontSize: 12, fontWeight: FontWeight.w500),
                                  ),
                                ],
                              ),
                            ),
                            
                          ],
                        ),
                        Divider(
                          thickness: 1,
                          color: Colors.grey[350],
                        ),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              'More Activities'
                              ),
                              SizedBox(
                                width: 10,
                              )
                          ],
                        ),
                        Material(
                          color: Colors.white,
                          child: InkWell(
                          onTap: () {
                            print('likes button');
                          },
                          child: ListTile(
                            title: const Text(
                              'My Likes'
                            ),
                            leading: Image(image: AssetImage('assets/icons/likes.png'),width: 30, fit: BoxFit.contain,),
                            trailing: Icon(
                              Icons.keyboard_arrow_right_sharp,
                              color: Colors.grey[400],
                            )
                          )
                        ),
                        ),
                        Divider(
                          thickness: 1,
                        ),
                        Material(
                          color: Colors.white,
                          child: InkWell(
                          onTap: () {
                            print('guide button');
                          },
                          child: ListTile(
                            title: const Text(
                              'Buyer Guide'
                            ),
                            leading: Image(image: AssetImage('assets/icons/guide.png'),width: 30, fit: BoxFit.contain,),
                            trailing: Icon(
                              Icons.keyboard_arrow_right_sharp,
                              color: Colors.grey[400],
                            )
                          )
                        ),
                        ),
                        Divider(
                          thickness: 2,
                          color: Colors.grey[350],
                        ),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              'Support'
                            ),
                            SizedBox(
                              width: 20,
                            )
                          ],
                        ),
                        Material(
                          color: Colors.white,
                          child: InkWell(
                          onTap: () {
                            print('guide button');
                          },
                          child: ListTile(
                            title: const Text(
                              'Help'
                            ),
                            leading: Image(image: AssetImage('assets/icons/help.png'),width: 30, fit: BoxFit.contain,),
                            trailing: Icon(
                              Icons.keyboard_arrow_right_sharp,
                              color: Colors.grey[400],
                            )
                          )
                        ),
                        ),
                        Divider(
                          thickness: 1,
                          color: Colors.grey[350],
                        ),
                        Material(
                          color: Colors.white,
                          child: InkWell(
                          onTap: () {
                            print('guide button');
                          },
                          child: ListTile(
                            title: const Text(
                              'Chat with admin'
                            ),
                            leading: Image(image: AssetImage('assets/icons/message_admin.png'),width: 30, fit: BoxFit.contain,),
                            trailing: Icon(
                              Icons.keyboard_arrow_right_sharp,
                              color: Colors.grey[400],
                            )
                          )
                        ),
                        ),
                        Divider(
                          thickness: 1,
                          color: Colors.grey[350],
                        ),
                        Material(
                          color: Colors.white,
                          child: InkWell(
                          onTap: () {
                            Navigator.of(context).pushNamedAndRemoveUntil('/', (route) => false);

                          },
                          child: ListTile(
                            title: const Text(
                              'Log out'
                            ),
                            leading: Image(image: AssetImage('assets/icons/log-out.png'),width: 30, fit: BoxFit.contain,),
                            trailing: Icon(
                              Icons.keyboard_arrow_right_sharp,
                              color: Colors.grey[400],
                            )
                          )
                        ),
                        ),
                      ],
                    ),
                  ),
                  )
              ],
            ),
          ),
        )
      )
    );
  }
}