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
class OrderDetailsPage extends StatefulWidget {
  const OrderDetailsPage({super.key});

  @override
  State<OrderDetailsPage> createState() => _OrderDetailsPageState();
}

class _OrderDetailsPageState extends State<OrderDetailsPage> {
  List<Product> productList = [];
  int currentPage = 1;
  bool _isLoading = false;
  int orderId_Value = 0;
  int payment_status = 0;

//############################################//
//#############  B A C K  E N D  #############//
//############################################//

//#######################################//
//###  G E T  C A R T  D E T A I L S  ###//
//#######################################//

Future<void> getOrderDetails() async{

  try{
    final searched = await DioCookie.dio.get(
    '$globalurl/get-order-details');
    
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


//#################################//
//###  S A V E  O R D E R  I D  ###//
//#################################//

Future<void> paymentUpdate() async{

    final response = await DioCookie.dio.post(
    '$globalurl/payment-update',

    data: {
      'productID': orderId_Value,
      'payment_status' : payment_status
    },);
    print(response.statusCode);
    if (response.statusCode == 200){
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


//#########################################//
//###  R U N  B A C K E N D  F I R S T  ###//
//#########################################//

@override
void initState() {
  super.initState();
    getOrderDetails();
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
          'Order',
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
            child: ConstrainedBox(
            constraints: BoxConstraints(
              minHeight: MediaQuery.of(context).size.height,
              minWidth: MediaQuery.of(context).size.width,
            ),
            child: SizedBox(
              child: Column(
                children: [
                  SizedBox(
                  height: 100,
                ),
                ConstrainedBox(
                  constraints: BoxConstraints(
                    minHeight: MediaQuery.of(context).size.height,
                    minWidth: MediaQuery.of(context).size.width,
                  ) ,
                  child: Container(
                  height: 800,
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.only(
                      topLeft: Radius.elliptical(20, 20),
                      topRight: Radius.elliptical(20, 20)
                    )
                  ),
                  child:Padding(
                    padding: EdgeInsets.symmetric(
                      horizontal: 30,
                      vertical: 20
                    ),
                    child: Column(
                      children: [
                        Text(
                          'Order Details',
                          style: TextStyle(
                            fontFamily: 'RadioCanada',
                            fontSize: 15
                          ),
                          ),
                          Divider(),
                          SizedBox(
                            height: 10,
                          ),
                          Align(
                            alignment: Alignment.centerLeft,
                            child: Text(
                              'Orders:',
                              style: TextStyle(
                                fontFamily: 'RadioCanada',
                                fontSize: 18
                              ),
                            ),
                          ),
                          SizedBox(
                            height: 10,
                          ),
                          Align(
                            alignment: Alignment.centerLeft,
                            child: ConstrainedBox(
                              constraints: BoxConstraints(
                                minWidth: MediaQuery.of(context).size.width
                              ),
                              child: Text(
                                productList.isNotEmpty ? '${productList[0].product}' : 'Products'
                              ),
                            )
                          ),
                          SizedBox(
                            height: 50,
                          ),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text(
                                'Payment Method:',
                                style: TextStyle(
                                  fontFamily: 'RadioCanada',
                                  fontSize: 16,
                                ),
                              ),
                              Container(
                                padding: EdgeInsets.symmetric(
                                  horizontal: 20,
                                  vertical: 4
                                ),
                                decoration: BoxDecoration(
                                  color: Color.fromRGBO(133, 82, 187, 1),
                                  borderRadius: BorderRadius.circular(6)
                                ),
                                child: Text(
                                  productList.isNotEmpty ? '${productList[0].payment_method == 'cash' ? "Cash" : productList[0].payment_method == 'card' ? "Card" : ""}' : "N/A",
                                  style: TextStyle(
                                    color: Colors.white,
                                    fontFamily: 'RadioCanada',
                                    fontWeight: FontWeight.w600
                                  ),
                                ),
                              )
                            ],
                          ),
                          SizedBox(
                            height: 30,
                          ),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text(
                                'Payment Status:',
                                style: TextStyle(
                                  fontFamily: 'RadioCanada',
                                  fontSize: 16,
                                ),
                              ),
                              Container(
                                padding: EdgeInsets.symmetric(
                                  horizontal: 20,
                                  vertical: 4
                                ),
                                decoration: BoxDecoration(
                                  color: productList.isNotEmpty ? productList[0].payment_status == 0 ? Color.fromRGBO(187, 82, 84, 1) : productList[0].payment_status == 1 ? Color.fromRGBO(66, 153, 89, 1) : Color.fromRGBO(187, 82, 84, 1) : Color.fromRGBO(187, 82, 84, 1),
                                  borderRadius: BorderRadius.circular(6)
                                ),
                                child: Text(
                                  productList.isNotEmpty ? '${productList[0].payment_status == 0 ? "Unpaid" : productList[0].payment_status == 1 ? "Paid" : ""}' : "N/A",
                                  style: TextStyle(
                                    color: Colors.white,
                                    fontFamily: 'RadioCanada',
                                    fontWeight: FontWeight.w600
                                  ),
                                ),
                              )
                            ],
                          ),
                          SizedBox(
                            height: 30,
                          ),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text(
                                'Order Status:',
                                style: TextStyle(
                                  fontFamily: 'RadioCanada',
                                  fontSize: 16,
                                ),
                              ),
                              Container(
                                padding: EdgeInsets.symmetric(
                                  horizontal: 20,
                                  vertical: 4
                                ),
                                decoration: BoxDecoration(
                                  color: productList.isNotEmpty ? productList[0].order_status == 0 ? Color.fromRGBO(0, 88, 151, 1) : productList[0].order_status == 1 ? Color.fromRGBO(201, 161, 0, 1) : productList[0].order_status == 2 ? Color.fromRGBO(66, 153, 89, 1) :Color.fromRGBO(187, 82, 84, 1) : Color.fromRGBO(187, 82, 84, 1),
                                  borderRadius: BorderRadius.circular(6)
                                ),
                                child: Text(
                                  productList.isNotEmpty ? '${productList[0].order_status == 0 ? "Order Placed" : productList[0].order_status == 1 ? "To Ship" : productList[0].order_status == 2 ? "Delivered" : ""}' : "N/A",
                                  style: TextStyle(
                                    color: Colors.white,
                                    fontFamily: 'RadioCanada',
                                    fontWeight: FontWeight.w600
                                  ),
                                ),
                              )
                            ],
                          ),
                          SizedBox(
                            height: 30,
                          ),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text(
                                'Payment Method:',
                                style: TextStyle(
                                  fontFamily: 'RadioCanada',
                                  fontSize: 16,
                                ),
                              ),
                              Text(
                                  productList.isNotEmpty ? '₱${productList[0].order_total.toStringAsFixed(2)}' : "₱300.00",
                                  style: TextStyle(
                                    color: Color.fromRGBO(88, 0, 146, 1),
                                    fontFamily: 'RadioCanada',
                                    fontWeight: FontWeight.w600,
                                    fontSize: 25
                                  ),
                                ),
                            ],
                          )
                      ],
                    ),
                    ),
                  )
                )
              ],
              ),
            ),
          ),
        ),
      )),
      bottomNavigationBar: ConstrainedBox(
        constraints: BoxConstraints(
          minWidth: MediaQuery.of(context).size.width,
        ),
        child: SizedBox(
        child: Padding(
          padding: EdgeInsets.all(10),
          child: ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    minimumSize: Size(350, 50),
                    backgroundColor: productList.isNotEmpty ? productList[0].payment_method == 'Cash'  && productList[0].order_status == 2 ? Color.fromRGBO(66, 153, 89, 1) :  Colors.grey :Colors.grey,
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(15)
                    )
                  ),
                  onPressed: productList.isEmpty ? null : () {
                    if (productList[0].payment_method == 'Cash' && productList[0]. order_status == 2){
                      setState(() {
                        orderId_Value = productList[0].order_id;
                        payment_status = 1;
                      }
                      );
                      paymentUpdate();
                    }
                  },
                  child: Text('Pay')
                  )
        ),
      ) ,
      )
    );
  }
}