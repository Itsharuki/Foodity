import 'package:flutter/material.dart';
import 'package:mobile_ecom_foodity/Buyer/buyerHome.dart';
import 'package:mobile_ecom_foodity/Url/AllUrl.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:typed_data';
import 'package:mobile_ecom_foodity/Cookies/dio_cookie.dart';
import 'package:intl/intl.dart';

class Product {
  final int order_id;
  final String product;
  final String order_date;
  final String payment_method;
  final double order_total;
  final int order_quantity;
  final int order_status;
    final int payment_status;

  Product({
    required this.order_id,
    required this.product,
    required this.order_date,
    required this.payment_method,
    required this.order_total,
    required this.order_quantity,
    required this.order_status,
    required this.payment_status
    });

  factory Product.fromJson(Map <String, dynamic> json) {
    return Product(
      order_id: json['order_id'],
      product: json['product'],
      order_date: json['order_date'],
      payment_method: json['payment_method'],
      order_total: double.tryParse(json['order_total'].toString()) ?? 0.0,
      order_quantity: json['order_quantity'],
      order_status: json['order_status'],
      payment_status: json['payment_status'],
      );
  }

  Map<String, dynamic> toJson() {
    return {
      'order_id': order_id,
      'product': product,
      'order_date': order_date,
      'payment_method': payment_method,
      'order_total': order_total,
      'order_quantity': order_quantity,
      'order_status': order_status,
      'payment_status': payment_status,
    };
  }
}
class BuyerToPay extends StatefulWidget {
  const BuyerToPay({super.key});

  @override
  State<BuyerToPay> createState() => _BuyerToPayState();
}

class _BuyerToPayState extends State<BuyerToPay> {
  List<Product> productList = [];
  int currentPage = 1;
  bool _isLoading = false;
  int orderId_Value = 0;

//############################################//
//#############  B A C K  E N D  #############//
//############################################//

//#################################//
//###  S A V E  O R D E R  I D  ###//
//#################################//

Future<void> orderID() async{

    final response = await DioCookie.dio.post(
    '$globalurl/storeToPayId',

    data: {
      'productID': orderId_Value,
    },);
    print(response.statusCode);
    if (response.statusCode == 200){
      Navigator.pushNamed(context, '/orderDetailsPage');
    }

}

//#######################################//
//###  G E T  C A R T  D E T A I L S  ###//
//#######################################//

Future<void> getOrders({int page = 1}) async{
  if (_isLoading) return;

  setState(() {
    _isLoading = true;
  });

  try{
    final products = await DioCookie.dio.get(
    '$globalurl/getOrdersToPay?page=$page');
    DioCookie.dio.options.connectTimeout = Duration(seconds: 90);
    DioCookie.dio.options.receiveTimeout = Duration(seconds: 90);
    
    if (products.statusCode == 200){
    var decoded = (products.data);
    setState(() {
    if (page == 1){
      productList = List<Product>.from((decoded['orderDetails'] as List).map((product) => Product.fromJson(product)).toList());
    }else{
      productList.addAll(List<Product>.from((decoded['orderDetails'] as List).map((product) => Product.fromJson(product))));
    }
    currentPage = page;
    });
  }else{
    throw Exception('Failed loading products');
  }
  } catch (e){
    print("Error loading products: $e");
    await Future.delayed(Duration(seconds: 5));
    await getOrders(page: page);
  }
  setState(() {
    _isLoading = false;
  });
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


//#########################################//
//###  R U N  B A C K E N D  F I R S T  ###//
//#########################################//

@override
void initState() {
  super.initState();
    getOrders();
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
          'My Purchase',
          style: TextStyle(
            fontFamily: 'RadioCanada',
            color: Colors.white
          ),
          ),
        centerTitle: true,
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
                      topLeft: Radius.elliptical(20, 20),
                      topRight: Radius.elliptical(20, 20)
                    )
                  ),
                  child: Padding(
                    padding: EdgeInsets.symmetric(
                      horizontal: 30,
                      vertical: 20
                    ),
                    child: Column(
                    children: [
                      SizedBox(
                        height: 15,
                      ),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text(
                            'To Pay',
                            style: TextStyle(
                              fontFamily: 'RadioCanada',
                              fontWeight: FontWeight.w500,
                              fontSize: 15
                            ),
                          ),
                        ],
                      ),
                      Divider(
                        thickness: 1,
                      ),
                      SizedBox(
                        height: 10,
                      ),
                      Container(
                            height: 600,
                            child: productList.isEmpty ? Center(child: CircularProgressIndicator())
                            : NotificationListener<ScrollNotification>(
                              onNotification: (ScrollNotification scrollInfo) {
                                if (!_isLoading && scrollInfo.metrics.pixels == scrollInfo.metrics.maxScrollExtent) {
                                  getOrders(page: currentPage + 1);
                                  return true;
                                }
                                return false;
                              },
                              child: ListView.builder(
                                itemCount: productList.length,
                                itemBuilder: (context, index) {
                                  final product = productList[index];
                                  return InkWell(
                                    onTap: () {
                                      
                                    },
                                    child: Card(
                                    elevation: 2,
                                    margin: EdgeInsets.symmetric(vertical: 6),
                                    child: ListTile(
                                      leading: Flexible(
                                          child: Text(
                                            '${product.order_id}',
                                            overflow: TextOverflow.ellipsis,
                                            maxLines: 2,
                                            style: TextStyle(
                                              fontFamily: 'RadioCanada',
                                              fontSize: 15,
                                              fontWeight: FontWeight.w400
                                            ),
                                          ),
                                        ),
                                    title: Flexible(
                                      child: Row(
                                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                        children: [
                                          Container(
                                            width: 80,
                                            child: Text(
                                              product.product,
                                              overflow: TextOverflow.ellipsis,
                                              style: TextStyle(
                                                fontFamily: 'RadioCanada',
                                                fontSize: 15,
                                                fontWeight: FontWeight.w400
                                              ),
                                            ),
                                          ),
                                          Text(
                                              '₱${product.order_total.toStringAsFixed(2)}',
                                              style: TextStyle(
                                                color: Color.fromRGBO(88, 0, 146, 1)
                                              ),
                                          ),
                                        ],
                                      ),
                                    ),
                                    subtitle: Flexible(
                                      child: Row(
                                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                        children: [
                                          Column(
                                            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                                            children: [
                                              Text(
                                                '${product.order_status == 0 ? "Order Placed" : ""}',
                                                style: TextStyle(
                                                  color: Colors.red
                                                ),
                                              )
                                            ],
                                          ),
                                          Text(
                                                  '${product.order_quantity.toString()} pc(s)',
                                                  style: TextStyle(
                                                    fontSize: 12
                                                  ),
                                                ),
                                        ],
                                      ),
                                    ),
                                    trailing: Icon(Icons.arrow_forward_ios_rounded),
                                    onTap: (){
                                    setState(() {
                                        orderId_Value = product.order_id;
                                        print(" this isss  $orderId_Value");
                                      });
                                      orderID();
                                    },
                                    )
                                  ),
                                  );
                                }
                                ),
                            ) ,
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
    );
  }
}