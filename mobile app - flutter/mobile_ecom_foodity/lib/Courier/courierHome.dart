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

class OrderTotal {
  final double subTotal;
  final double total;

  OrderTotal({
    required this.subTotal,
    required this.total,
    });

  factory OrderTotal.fromJson(Map <String, dynamic> json) {
    return OrderTotal(
      subTotal: double.tryParse(json['subTotal'].toString()) ?? 0.0,
      total: double.tryParse(json['total'].toString()) ?? 0.0,
      );
  }

  Map<String, dynamic> toJson() {
    return {
      'subTotal': subTotal,
      'total': total,
    };
  }
}

class CourierHome extends StatefulWidget {
  CourierHome({super.key});

  @override
  State<CourierHome> createState() => CourierHomePageState();
}

class CourierHomePageState extends State<CourierHome> {
  List<dynamic> productList = [];
  List<dynamic> userList = [];
  String selectedPaymentMethod = '';
  int currentPage = 1;
  bool _isLoading = false;
  List<dynamic> orderTotalList = [];
  bool _isSearching = false;
  TextEditingController searchBox = TextEditingController();
  int removeProductId = 0;

//############################################//
//#############  B A C K  E N D  #############//
//############################################//

//##################################//
//###  T O G G L E  S E A R C H  ###//
//##################################//

void toggleSearch(){ //search products icons
  setState(() {
    _isSearching = !_isSearching;
    if(!_isSearching){
      searchBox.clear();
    }
  });
}

//####################################//
//###  P R O D U C T  S E A R C H  ###//
//####################################//

Future<void> getSearchedOrders() async{
  final url = Uri.parse('$globalurl/getProductsSearch'); //pass url

  try{
    final searched = await http.post(
    url,
    headers: {
      'Content-Type': 'application/json',
    },
    body: jsonEncode({
      'productName' : searchBox.text.trim().toLowerCase()
    })
    ).timeout(Duration(seconds: 90));
  
    if (searched.statusCode == 200){
      var decoded = jsonDecode(searched.body);
      setState(() {
        productList.clear();
        productList = List<Product>.from((decoded['searched'] as List).map((product) => Product.fromJson(product)).toList());
        searchBox.clear();
      });
    }
  }catch (e){
    print("Error searching products: $e");
  }
}

//##################################//
//###  O R D E R  D E T A I L S  ###//
//##################################//

Future<void> getMyOrderDetails({int page = 1}) async{
  if (_isLoading) return;

  setState(() {
    _isLoading = true;
  });

  try{
    final products = await DioCookie.dio.get(
    '$globalurl/getMyOrderDetails?page=$page');
    DioCookie.dio.options.connectTimeout = Duration(seconds: 90);
    DioCookie.dio.options.receiveTimeout = Duration(seconds: 90);
    
    if (products.statusCode == 200){
    var decoded = (products.data);
    setState(() {
    if (page == 1){
      productList = List<Product>.from((decoded['myOrderDetails'] as List).map((product) => Product.fromJson(product)).toList());
    }else{
      productList.addAll(List<Product>.from((decoded['myOrderDetails'] as List).map((product) => Product.fromJson(product))));
    }
    currentPage = page;
    });
  }else{
    throw Exception('Failed loading products');
  }
  } catch (e){
    print("Error loading products: $e");
    await Future.delayed(Duration(seconds: 2));
    await getMyOrderDetails(page: page);
  }
  setState(() {
    _isLoading = false;
  });
}

//##############################//
//###  O R D E R  T O T A L  ###//
//##############################//

Future<void> getOrderTotal() async{

  try{
    final orderAmount = await DioCookie.dio.get(
    '$globalurl/getMyOrderTotal');
    
    if (orderAmount.statusCode == 200){
      var decoded = orderAmount.data;
      print(decoded);
      setState(() {
        orderTotalList = List<OrderTotal>.from((decoded['orderTotal'] as List).map((totalOrder) => OrderTotal.fromJson(totalOrder)).toList());
      });
    }
  }catch (e){ 
    print("Error total amount: $e");
  }
}

@override
void initState() {
  super.initState();
    getMyOrderDetails();
    getOrderTotal();
}

//####################################//
//###  R E M O V E  P R O D U C T  ###//
//####################################//

Future<void> removeProduct() async{

    final response = await DioCookie.dio.post(
    '$globalurl/remove_product',

    data: {
      'remove_id': removeProductId,
      'product_name' : productList[0].product_name,
      'order_quantity' : productList[0].order_quantity
    },);
    print(response.statusCode);
    if (response.statusCode == 200){
      print('success');
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
        title: Text(
          'Home',
          style: TextStyle(
            fontFamily: 'RadioCanada',
            color: Colors.white
          ),
        ),
        centerTitle: true,
      ),
      body: Container(
        decoration: BoxDecoration(
          image: DecorationImage(image: AssetImage('assets/login/all_bg.png'), fit: BoxFit.fill)
        ),
          child: SingleChildScrollView(
                child: ConstrainedBox(
                  constraints: BoxConstraints(
                    minHeight: MediaQuery.of(context).size.height,
                    minWidth: MediaQuery.of(context).size.width,
                  ),
                  child: Container(
                    child: Column(
                      children: [
                        SizedBox(
                          height: 100,
                        ),
                        Container(
                          width: 340,
                          height: 70,
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(10)
                          ),
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                            children: [
                              Image.asset(
                                'assets/courier/delivery.png',
                                height: 40,
                                width: 40,
                                fit: BoxFit.contain,
                              ),
                              Text(
                                'For Delivery',
                                style: TextStyle(
                                  fontFamily: 'RadioCanada',
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                              Text(
                                '20',
                                style: TextStyle(
                                  fontFamily: 'RadioCanada',
                                  fontWeight: FontWeight.w500,
                                  fontSize: 25
                                ),
                              )
                            ],
                          ),
                        ),
                        SizedBox(
                          height: 50,
                        ),
                        Container(
                          width: 340,
                          height: 70,
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(10)
                          ),
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                            children: [
                              Image.asset(
                                'assets/courier/on_delivery.png',
                                height: 40,
                                width: 40,
                                fit: BoxFit.contain,
                              ),
                              Text(
                                'For Delivery',
                                style: TextStyle(
                                  fontFamily: 'RadioCanada',
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                              Text(
                                '20',
                                style: TextStyle(
                                  fontFamily: 'RadioCanada',
                                  fontWeight: FontWeight.w500,
                                  fontSize: 25
                                ),
                              )
                            ],
                          ),
                        ),
                        SizedBox(
                          height: 50,
                        ),
                        Container(
                          width: 340,
                          height: 70,
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(10)
                          ),
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                            children: [
                              Image.asset(
                                'assets/courier/delivered.png',
                                height: 40,
                                width: 40,
                                fit: BoxFit.contain,
                              ),
                              Text(
                                'For Delivery',
                                style: TextStyle(
                                  fontFamily: 'RadioCanada',
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                              Text(
                                '23',
                                style: TextStyle(
                                  fontFamily: 'RadioCanada',
                                  fontWeight: FontWeight.w500,
                                  fontSize: 25
                                ),
                              )
                            ],
                          ),
                        ),
                        SizedBox(
                          height: 50,
                        ),
                        Container(
                          width: MediaQuery.of(context).size.width,
                          height: 550,
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.only(
                              topLeft: Radius.elliptical(20, 20),
                              topRight: Radius.elliptical(20, 20)
                            )
                          ),
                          child: Padding(
                            padding: EdgeInsets.all(3),
                            child: Column(
                              children: [
                                SizedBox(
                                  height: 10,
                                ),
                                Row(
                                  children: [
                                    SizedBox(
                                      width: 20,
                                    ),
                                    Align(
                                  alignment: Alignment.centerLeft,
                                    child: Text(
                                      'Deliveries',
                                      style: TextStyle(
                                        fontFamily: 'RadioCanada',
                                        fontSize: 20,
                                        fontWeight: FontWeight.w500
                                      ),
                                    ),
                                  )
                                  ],
                                )
                              ],
                            ),
                          )
                        ),
                      ],
                    ),
                  ),
                ),
              )
          ),
          bottomNavigationBar: Container(
              height: 65,
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.only(topLeft: Radius.circular(10), topRight: Radius.circular(10),),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black38,
                    blurRadius: 8,
                    offset: Offset(0, -6)
                  )
                ]
              ),
              child: Row(mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  Spacer(),

                  Column(
                    children: [
                      IconButton(onPressed: (){
                      }, icon: Container(
                        width: 30,
                        height: 30,
                        child: Image(image: AssetImage('assets/icons/Home.png'), fit: BoxFit.contain,),
                      ),
                      iconSize: 20,
                      ),
                      Text(
                        'Home',
                        style: TextStyle(fontFamily: 'RadioCanada', fontSize: 10, fontWeight: FontWeight.bold),),
                      Spacer()
                    ],
                  ),
                  
                  Spacer(),
                  Column(
                    children: [
                      Spacer(),
                      IconButton(onPressed: (){
                      }, icon: Container(
                        width: 30,
                        height: 30,
                        child: Image(image: AssetImage('assets/icons/delivery.png'), fit: BoxFit.contain,),
                      ),
                      iconSize: 20,
                      ),
                      Text(
                        'Deliveries',
                        style: TextStyle(fontFamily: 'RadioCanada', fontSize: 10, fontWeight: FontWeight.bold),),
                      Spacer()
                    ],
                  ),
                  Spacer(),
                  Column(
                    children: [
                      Spacer(),
                      IconButton(onPressed: (){
                      }, icon: Container(
                        width: 30,
                        height: 30,
                        child: Image(image: AssetImage('assets/icons/delivery_report.png'), fit: BoxFit.contain,),
                      ),
                      iconSize: 20,
                      ),
                      Text(
                        'Delivery Reports',
                        style: TextStyle(fontFamily: 'RadioCanada', fontSize: 10, fontWeight: FontWeight.bold),),
                      Spacer()
                    ],
                  ),
                  Spacer(),
                  Column(
                    children: [
                      Spacer(),
                      IconButton(onPressed: (){
                      }, icon: Container(
                        width: 30,
                        height: 30,
                        child: Image(image: AssetImage('assets/icons/user.png'), fit: BoxFit.contain,),
                      ),
                      iconSize: 20,
                      ),
                      Text(
                        'Me',
                        style: TextStyle(fontFamily: 'RadioCanada', fontSize: 10, fontWeight: FontWeight.bold),),
                      Spacer()
                    ],
                  ),
                  Spacer(),
                ],
              ),
              ),
    );
  }
}

