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
    required this.account_type
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

class BuyerCheckoutPage extends StatefulWidget {
  const BuyerCheckoutPage({super.key});

  @override
  State<BuyerCheckoutPage> createState() => _BuyerCheckoutPageState();
}

class _BuyerCheckoutPageState extends State<BuyerCheckoutPage> {
  List<dynamic> productList = [];
  List<dynamic> userList = [];
  String selectedPaymentMethod = '';
  int currentPage = 1;
  bool _isLoading = false;
  List<dynamic> orderTotalList = [];
  
//############################################//
//#############  B A C K  E N D  #############//
//############################################//

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

Future<void> getUserDetails() async{

  try{
    final user = await DioCookie.dio.get(
    '$globalurl/getUserDetails');
    
    if (user.statusCode == 200){
      var decoded = user.data;
      print(decoded);
      setState(() {
        userList = List<User>.from((decoded['userDetails'] as List).map((user) => User.fromJson(user)).toList());
      });
    }
  }catch (e){ 
    print("Error searching products: $e");
  }
}

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


Future<void> placeOrder() async{

    final response = await DioCookie.dio.post(
    '$globalurl/orderPlacement',

    data: {
      'selectedPaymentMethod': selectedPaymentMethod,
    },);
    print(response.statusCode);
    if (response.statusCode == 200){
      Navigator.pushNamed(context, '/buyerToPay');
    }

}




@override
void initState() {
  super.initState();
    getMyOrderDetails();
    getUserDetails();
    getOrderTotal();
}


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

@override
void dispose() {
  // Cancel any timers or subscriptions
  super.dispose();
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
          'Checkout',
          style: TextStyle(
            fontFamily: 'RadioCanada',
            color: Colors.white
          ),
          ),
        centerTitle: true,
      ),
      body: Container(
        decoration: BoxDecoration(
          image: DecorationImage(image: AssetImage('assets/login/all_bg.png'), fit: BoxFit.cover)
        ),
        child: Expanded(
          child: SingleChildScrollView(
          child: Container(
            child: Column(
              children: [
                SizedBox(
                  height: 80,
                ),
                Container(
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
                          children: [
                            Icon(Icons.location_on_outlined),
                            Text(
                              'Delivery Address',
                              style: TextStyle(
                                fontFamily: 'RadioCanada',
                                fontWeight: FontWeight.w500,
                                fontSize: 16
                              ),
                            ),
                          ],
                        ),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            SizedBox(
                              width:250,
                              child: Text(
                              userList.isNotEmpty ? 'Address \n${userList[0].barangay}, ${userList[0].city}, ${userList[0].province}, ${userList[0].zip_code}': 'Address Value'
                              ),
                            ),
                            Icon(
                              Icons.chevron_right_rounded
                            )
                          ],
                        ),
                        SizedBox(
                          height: 10,
                          ),
                        Divider(
                          color: Color.fromRGBO(217, 217, 217, 1),
                          thickness: 2,
                        ),
                        SizedBox(
                          height: 20,
                        ),
                        Icon(
                          Icons.add,
                          color: Color.fromRGBO(170, 170, 170, 1),
                        ),
                        SizedBox(
                          height: 20,
                        ),
                        Divider(
                          color: Color.fromRGBO(217, 217, 217, 1),
                          thickness: 2,
                        ),
                        SizedBox(
                          height: 20,
                        ),
                        Align(
                          alignment: Alignment.centerLeft,
                          child: Text(
                          'Shopping List',
                          style: TextStyle(
                            fontFamily: 'RadioCanada',
                            fontSize: 15,
                            fontWeight: FontWeight.w400,
                            color: Colors.black
                          ),
                        ),
                        ),
                          Container(
                          height: 250,
                          child: productList.isEmpty ? Center(child: CircularProgressIndicator())
                          : NotificationListener<ScrollNotification>(
                            onNotification: (ScrollNotification scrollInfo) {
                              if (!_isLoading && scrollInfo.metrics.pixels == scrollInfo.metrics.maxScrollExtent) {
                                getMyOrderDetails(page: currentPage + 1);
                                return true;
                              }
                              return false;
                            },
                            child:  ListView.builder(
                            itemCount: productList.length,
                            itemBuilder: (context, index) {
                              final product = productList[index];
                              return Card(
                                elevation: 2,
                                margin: EdgeInsets.symmetric(vertical: 6),
                                child: ListTile(
                                leading: Padding(
                                  padding: EdgeInsets.all(1),
                                  child: Image.memory( //image
                                  _safeDecodeImage(product.base64Image),
                                  width: 40,
                                  height: 40,
                                  fit: BoxFit.fill,
                                )
                                ),
                                title: Row(
                                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                  children: [
                                    Container(
                                      width: 110,
                                      child: Text(
                                      product.product_name,
                                      overflow: TextOverflow.ellipsis,
                                      maxLines: 1,
                                      )
                                    ),
                                    Text(
                                      '₱${product.item_total_amount.toStringAsFixed(2)}',
                                      style: TextStyle(
                                        color: Color.fromRGBO(88, 0, 146, 1)
                                      ),
                                    )
                                    
                                  ],
                                ),
                                subtitle: Row(
                                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                  children: [
                                    Container(
                                      width: 150,
                                      child: Text(
                                      '${product.product_description}',
                                      overflow: TextOverflow.ellipsis,
                                      maxLines: 2,
                                    ),
                                    ),
                                    Text(
                                      '${product.order_quantity.toString()} pc(s)'
                                    )
                                  ],
                                ),
                                onTap: (){
                                  
                                  },
                                )
                              );
                            },
                          ),
                        )
                        ),
                        Divider(
                          color: Color.fromRGBO(217, 217, 217, 1),
                          thickness: 2,
                        ),
                        Align(
                          alignment: Alignment.centerLeft,
                          child: Text(
                            'Payment Options',
                            style: TextStyle(
                                fontFamily: 'RadioCanada',
                                fontWeight: FontWeight.w500,
                                fontSize: 16
                              ),
                          ),
                        ),
                        SizedBox(
                          height: 10,
                        ),
                        Column(
                          children: [
                            InkWell(
                                onTap: () {
                                  setState(() {
                                    selectedPaymentMethod = 'cash';
                                  });
                                },
                                child: ListTile(
                                  title: const Text(
                                    'Cash'
                                  ),
                                  leading: Icon(
                                    Icons.account_balance_wallet_outlined
                                  ),
                                  trailing: selectedPaymentMethod == 'cash'
                                  ? Icon(
                                    Icons.check,
                                    color: Color.fromRGBO(88, 0, 146, 1),
                                  )
                                  : Icon(
                                    Icons.check,
                                    color: Colors.transparent,
                                  )
                                  ,
                                )
                            ),
                            Divider(
                              thickness: 2,
                              color: Color.fromRGBO(217, 217, 217, 1),
                            ),
                            InkWell(
                                onTap: () {
                                  setState(() {
                                    selectedPaymentMethod = 'card';
                                  });
                                },
                                child: ListTile(
                                  title: const Text(
                                    'Card'
                                  ),
                                  leading: Icon(
                                    Icons.credit_card
                                  ),
                                  trailing: selectedPaymentMethod == 'card'
                                  ? Icon(
                                    Icons.check,
                                    color: Color.fromRGBO(88, 0, 146, 1)
                                  )
                                  : Icon(
                                    Icons.check,
                                    color: Colors.transparent,
                                  )
                                  ,
                                )
                            ),
                          ],
                        ),
                        Divider(
                          thickness: 5,
                          color: Color.fromRGBO(217, 217, 217, 1),
                        ),
                        SizedBox(
                          height: 10
                        ),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              'Sub Total'
                            ),
                            Text(
                              orderTotalList.isNotEmpty ? '₱${orderTotalList[0].subTotal}' : '₱0.00',
                            )
                          ],
                        ),
                        SizedBox(
                          height: 20,
                        ),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              'Delivery Fee'
                            ),
                            Text(
                              '₱40.00'
                            )
                          ],
                        ),
                        Divider(
                          thickness: 2,
                          color: Color.fromRGBO(217, 217, 217, 1),
                        ),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              'Total',
                              style: TextStyle(
                                fontFamily: 'RadioCanada',
                                fontSize: 20,
                                fontWeight: FontWeight.w500
                              ),
                            ),
                            Text(
                              orderTotalList.isNotEmpty ? '₱${orderTotalList[0].total}' : '₱0.00',
                              style: TextStyle(
                                fontFamily: 'Radio Canada',
                                fontSize: 20,
                                fontWeight: FontWeight.w500
                              ),
                            )
                          ],
                        ),
                        SizedBox(
                          height: 20,
                        ),
                        ElevatedButton(
                          style: ElevatedButton.styleFrom(
                            minimumSize: Size(350, 50),
                            backgroundColor: Color.fromRGBO(88, 0, 146, 1),
                            foregroundColor: Colors.white,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(15)
                            )
                          ),
                          onPressed: (){
                            placeOrder();
                          },
                          child: Text('Pay Now')
                          )
                      ],
                    ),
                  )
                )
              ],
            ),
          ),
        ),
        )
        )
    );
  }
}