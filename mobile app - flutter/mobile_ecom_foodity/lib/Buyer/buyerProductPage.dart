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
  final double product_price;
  final int product_stocks;
  final String base64Image;

  Product({
    required this.product_id,
    required this.product_name,
    required this.product_description,
    required this.product_price,
    required this.product_stocks,
    required this.base64Image});

  factory Product.fromJson(Map <String, dynamic> json) {
    return Product(
      product_id: json['product_id'],
      product_name: json['product_name'],
      product_description: json['product_description'],
      product_price: double.tryParse(json['product_price'].toString()) ?? 0.0,
      product_stocks: json['product_stocks'],
      base64Image: json['product_photo'] ?? '',
      );
  }

  Map<String, dynamic> toJson() {
    return {
      'product_id': product_id,
      'product_name': product_name,
      'product_description': product_description,
      'product_price': product_price,
      'product_stocks': product_stocks,
      'product_photo': base64Image,
    };
  }
}

class BuyerProductPage extends StatefulWidget {
  const BuyerProductPage({
    super.key,
    });

  @override
  State<BuyerProductPage> createState() => _BuyerProductPageState();
}

class _BuyerProductPageState extends State<BuyerProductPage> {
  List<dynamic> productList = [];
  int count = 1;
  String errMessage = '';
  
  // final product_id = ModalRoute.of(context)!.settings.arguments as int;  //retrieve the passed data!
  

//############################################//
//#############  B A C K  E N D  #############//
//############################################//

//#############################################//
//###  G E T  P R O D U C T  D E T A I L S  ###//
//#############################################//

Future<void> getProductDetails() async{

  try{
    final searched = await DioCookie.dio.get(
    '$globalurl/getProductDetails');
    
    if (searched.statusCode == 200){
      var decoded = searched.data;
      print(decoded);
      setState(() {
        productList = List<Product>.from((decoded['productDetails'] as List).map((product) => Product.fromJson(product)).toList());
      });
    }
  }catch (e){ 
    print("Error searching products: $e");
  }
}

//#########################//
//###  O V E R R I D E  ###//
//#########################//

@override
void initState() {
  super.initState();
    getProductDetails();
}

//##########################//
//###  A D D  C O U N T  ###//
//##########################//

void addQuantity(){
  setState(() {
    count++;
  });
}

//################################//
//###  R E D U C E  C O U N T  ###//
//################################//

void reduceQuantity(){
  setState(() {
    if (count > 1){
      count--;
    }
  });
}

//##############################//
//###  O R D E R  C O U N T  ###//
//##############################//

Future<void> orderCount() async{

    final response = await DioCookie.dio.post(
    '$globalurl/storeOrderCount',

    data: {
      'orderCount': count,
    },);
    print(response.statusCode);
    if (response.statusCode == 200){
      Navigator.pushNamed(context, '/buyerCheckout');
    }else if (response.statusCode == 404){
      errMessage = 'Low on stocks, please select other quantity';
    }
}

//############################//
//###  C A R T  C O U N T  ###//
//############################//

Future<void> cartCount() async{

    final response = await DioCookie.dio.post(
    '$globalurl/storeCartCount',

    data: {
      'cartCount': count,
    },);
    print(response.statusCode);
    if (response.statusCode == 200){
      Navigator.pushNamed(context, '/buyerCart');
    }else if (response.statusCode == 404){
      errMessage = 'Low on stocks, please select other quantity';
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
          image: DecorationImage(image: AssetImage('assets/login/all_bg.png'), fit: BoxFit.fill)
        ),
        child: Expanded(
          child: SingleChildScrollView(
          child: Container(
            child: Column(
              children: [
                SizedBox(height: 80,),
                Container(
                  decoration: BoxDecoration(
                    color: Colors.white
                    ),
                    child: Column(
                      children: [
                        Container(
                  height: 300,
                  decoration: BoxDecoration(
                    color: Colors.lightBlueAccent
                  ),
                  child: productList.isNotEmpty ? Image.memory( //image
                      _safeDecodeImage(productList[0].base64Image),
                      width: double.infinity,
                      fit: BoxFit.fill,
                    ) : SizedBox.shrink()
                ),
                Padding(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 30,
                    vertical: 20,
                    ),
                    child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Row(
                            children: [
                              Icon(
                                Icons.star,
                                color: Colors.yellow,
                                size: 30,
                                ),
                                SizedBox(
                                  width: 10,
                                ),
                                Text(
                                  '5.0',
                                  style: TextStyle(
                                    fontFamily: 'RadioCanada',
                                    fontSize: 20,
                                    fontWeight: FontWeight.bold
                                  ),
                                ),
                            ],
                          ),
                          IconButton(
                            onPressed: (){
                              getProductDetails();
                            },
                            icon: Icon(Icons.link))
                        ],
                      ),
                      SizedBox(height: 20,),
                      Text(
                        productList.isNotEmpty ? '₱${productList[0].product_price.toStringAsFixed(2)}' : '₱0.00',
                        style: TextStyle(
                          fontSize: 30,
                          fontWeight: FontWeight.bold,
                          color: Color.fromRGBO(88, 0, 146, 1)
                        ),
                      ),
                      SizedBox(height: 50,),
                      Text(
                        productList.isNotEmpty ? productList[0].product_name : 'Product Name'
                      ),
                      SizedBox(height: 30,),
                      Row(
                        children: [
                          Text('Stock(s):'),
                          SizedBox(width: 10),
                          Text(
                            productList.isNotEmpty ? '${productList[0].product_stocks} pc(s)' : '0'
                            )
                        ],
                      ),
                      SizedBox(height: 20,),
                      Text('Description'),
                      SizedBox(height: 5,),
                      Text(
                        productList.isNotEmpty ? productList[0].product_description : 'Loremipsum bla bla'
                      ),
                      SizedBox(height: 20,),
                      Text(
                        'Quantity:'
                      ),
                      Row(
                        children: [
                          IconButton(
                            onPressed: (){
                              reduceQuantity();
                            },
                            icon: Icon(
                              Icons.remove_circle_outline_rounded
                              ),
                              iconSize: 30,
                          ),
                          SizedBox(width: 5,),
                          Text(
                            '$count',
                            style: TextStyle(
                              fontFamily: 'RadioCanada',
                              fontSize: 25,
                              fontWeight: FontWeight.bold
                            ),
                            
                            ),
                          SizedBox(width: 5,),
                          IconButton(onPressed: (){
                            addQuantity();
                          },
                          icon: Icon(
                            Icons.add_circle_outline_rounded
                          ),
                          iconSize: 30,
                          )
                        ],
                      ),
                      Align(
                        alignment: Alignment.center,
                        child: Text(
                          '$errMessage'
                        ),
                      )
                    ],
                  ),
                ),
              ],
            ),
          )
                
        ],
      ),
    )
  )
          )
  ),
  bottomNavigationBar: Container(
    padding: EdgeInsets.symmetric(
      horizontal: 20,
      vertical: 15,
    ),
    color: Colors.white,
    child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                        children: [
                          ElevatedButton(
                            onPressed: (){
                              cartCount();
                            },
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Color.fromRGBO(230, 200, 255, 1),
                              foregroundColor: Colors.black,
                              padding: EdgeInsets.symmetric(horizontal: 30, vertical: 10)
                              ),
                            child: Text(
                              'Add to cart',
                              style: TextStyle(
                                fontFamily: 'RadioCanada',
                                fontSize: 20,
                                fontWeight: FontWeight.bold
                              ),
                              )
                            ),
                            ElevatedButton(
                            onPressed: (){
                              orderCount();
                            },
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Color.fromRGBO(97, 0, 161, 1),
                              foregroundColor: Colors.white,
                              padding: EdgeInsets.symmetric(horizontal: 40, vertical: 10)
                              ),
                            child: Text(
                              'Buy now',
                              style: TextStyle(
                                fontFamily: 'RadioCanada',
                                fontSize: 20,
                                fontWeight: FontWeight.bold
                              ),
                              )
                            ),
                        ],
                      ),
  ),
  );
  }
}