import 'package:dio/dio.dart';
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
  bool isSelected;

  Product({
    required this.product_id,
    required this.product_name,
    required this.product_description,
    required this.item_total_amount,
    required this.order_quantity,
    required this.base64Image,
    this.isSelected = false
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


class BuyerCartPage extends StatefulWidget {
  const BuyerCartPage({super.key});

  @override
  State<BuyerCartPage> createState() => _BuyerCartPageState();
}

class _BuyerCartPageState extends State<BuyerCartPage> {
  List<dynamic> selectedID = [];
  List<dynamic> selectedProducts = [];
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

//#######################################//
//###  G E T  C A R T  D E T A I L S  ###//
//#######################################//

Future<void> getCartDetails({int page = 1}) async{
  if (_isLoading) return;

  setState(() {
    _isLoading = true;
  });

  try{
    final products = await DioCookie.dio.get(
    '$globalurl/getCartDetails?page=$page');
    DioCookie.dio.options.connectTimeout = Duration(seconds: 90);
    DioCookie.dio.options.receiveTimeout = Duration(seconds: 90);
    
    if (products.statusCode == 200){
    var decoded = (products.data);
    setState(() {
    if (page == 1){
      productList = List<Product>.from((decoded['myCartDetails'] as List).map((product) => Product.fromJson(product)).toList());
    }else{
      productList.addAll(List<Product>.from((decoded['myCartDetails'] as List).map((product) => Product.fromJson(product))));
    }
    currentPage = page;
    });
  }else{
    throw Exception('Failed loading products');
  }
  } catch (e){
    print("Error loading products: $e");
    await Future.delayed(Duration(seconds: 5));
    await getCartDetails(page: page);
  }
  setState(() {
    _isLoading = false;
  });
}

//##################################################//
//###  R E M O V E  P R O D U C T  O N  C A R T  ###//
//##################################################//

Future<void> removeCartProduct() async{

    final response = await DioCookie.dio.post(
    '$globalurl/remove_product_on_cart',

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

//####################################//
//###  S E L E C T E D  T O T A L  ###//
//####################################//

double computeSelectedTotal(){
  return selectedProducts.fold(0.0, (sum, item) => sum + item.item_total_amount);
}

double selectedTotalWithDeliveryFee(){
  return computeSelectedTotal() + 40.00;
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

//##################################//
//###  C A R T  C H E C K O U T  ###//
//##################################//

Future<void> cartCheckout() async{

  try{
    final response = await DioCookie.dio.post(
    '$globalurl/cart-checkout',
    data: {
      'product_Ids': selectedID,
    },
    options: Options(
      headers: {
        'Content-Type': 'application/json',
      }
    )
    );
    print(response.statusCode);
    if (response.statusCode == 200){
      print('success');
      Navigator.pushNamed(context, '/buyerCheckout');
    }
  }catch (e){
    print ('Error sending product IDs: $e');
  }
}

//#########################################//
//###  R U N  B A C K E N D  F I R S T  ###//
//#########################################//

@override
void initState() {
  super.initState();
    getCartDetails();
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
          'Cart',
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
                        topLeft: Radius.elliptical(20, 20),
                        topRight: Radius.elliptical(20, 20)
                      )
                    ),
                    child: Padding(
                      padding: EdgeInsets.all(10),
                      child: Column(
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text(''),
                            ],
                          ),
                          Container(
                            height: 600,
                            child: productList.isEmpty ? Center(child: CircularProgressIndicator())
                            : NotificationListener<ScrollNotification>(
                              onNotification: (ScrollNotification scrollInfo) {
                                if (!_isLoading && scrollInfo.metrics.pixels == scrollInfo.metrics.maxScrollExtent) {
                                  getCartDetails(page: currentPage + 1);
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
                                      leading: Container(
                                      width: 90,
                                      child: Row(
                                        children: [
                                          Transform.scale(
                                          scale: 1,
                                          child: Checkbox(
                                            value: product.isSelected,
                                            onChanged: (bool? value){
                                              if (value != null){
                                                setState(() {
                                                product.isSelected = value;

                                                if (value){
                                                  if(!selectedID.contains(product.product_id)){
                                                    selectedID.add(product.product_id);
                                                  }
                                                }else{
                                                  selectedID.remove(product.product_id);
                                                }
                                                
                                                if (value){
                                                  if(!selectedProducts.contains(product)){
                                                    selectedProducts.add(product);
                                                  }
                                                }else{
                                                  selectedProducts.remove(product);
                                                }
                                              });
                                              }
                                            },
                                          ),
                                        ),
                                          Image.memory(
                                              _safeDecodeImage(product.base64Image),
                                              width: 40,
                                              height: 40,
                                              fit: BoxFit.fill,
                                            ),
                                        ],
                                      )
                                    ),
                                    title: Row(
                                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                      children: [
                                        Container(
                                          width: 50,
                                          child: Text(
                                            product.product_name,
                                            overflow: TextOverflow.ellipsis,
                                            style: TextStyle(
                                              fontFamily: 'RadioCanada',
                                              fontSize: 15,
                                              fontWeight: FontWeight.w400
                                            ),
                                          ),
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
                                        width: 50,
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
                                    trailing: Row(
                                      mainAxisSize: MainAxisSize.min,
                                      children: [
                                        
                                          IconButton(
                                            onPressed: (){
                                              print(product.product_id);
                                              setState(() {
                                                removeProductId = product.product_id;
                                              });
                                              removeCartProduct();
                                              getCartDetails();
                                            },
                                            icon: Icon(Icons.close_rounded, size: 20,)
                                          ),
                                      ],
                                    ),
                                    onTap: (){
                                    
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
          ) 
        ),
      bottomNavigationBar: Container(
        height: 250,
            decoration: BoxDecoration(
              color: const Color.fromARGB(255, 255, 255, 255),
              boxShadow: [
                BoxShadow(
                  offset: Offset(0, -2),
                  color: Colors.black54,
                  blurRadius: 10 
                )
              ],
              borderRadius: BorderRadius.only(
                topLeft: Radius.elliptical(20,20),
                topRight: Radius.elliptical(20,20)
              )
            ),
            child: Padding(
              padding: EdgeInsets.all(20),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Sub Total',
                        style: TextStyle(
                          fontFamily: 'RadioCanada',
                          fontSize: 15,
                          fontWeight: FontWeight.w400
                        ),
                      ),
                      Text(
                        selectedProducts.isNotEmpty ? '₱${computeSelectedTotal().toStringAsFixed(2)}' : '₱0.00',
                        style: TextStyle(
                          fontFamily: 'RadioCanada',
                          fontSize: 15,
                          fontWeight: FontWeight.w400
                        ),
                      )
                    ],
                  ),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Delivery fee',
                        style: TextStyle(
                          fontFamily: 'RadioCanada',
                          fontSize: 15,
                          fontWeight: FontWeight.w400
                        ),
                      ),
                      Text(
                        '₱40.00',
                        style: TextStyle(
                          fontFamily: 'RadioCanada',
                          fontSize: 15,
                          fontWeight: FontWeight.w400
                        ),
                      )
                    ],
                  ),
                  Divider(
                    thickness: 2,
                  ),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Total',
                        style: TextStyle(
                          fontFamily: 'RadioCanada',
                          fontSize: 15,
                          fontWeight: FontWeight.w400
                        ),
                      ),
                      Text(
                        selectedProducts.isNotEmpty ? '₱${selectedTotalWithDeliveryFee().toStringAsFixed(2)}': '₱0.00',
                        style: TextStyle(
                          fontFamily: 'RadioCanada',
                          fontSize: 15,
                          fontWeight: FontWeight.w400
                        ),
                      )
                    ],
                  ),
                  SizedBox(
                    height: 10,
                  ),
                  ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    minimumSize: Size(350, 50),
                    backgroundColor: selectedProducts.isEmpty ? Colors.grey : Color.fromRGBO(88, 0, 146, 1),
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(15)
                    )
                  ),
                  onPressed: selectedProducts.isEmpty
                    ? null :(){
                    if(selectedProducts.isEmpty){
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(content: Text('Please select atleast one product.'))
                      );
                      return;
                    }
                    cartCheckout();
                    
                  },
                  child: Text('Check Out')
                  )
                ],
              )
            ),
          ),
    );
  }
}