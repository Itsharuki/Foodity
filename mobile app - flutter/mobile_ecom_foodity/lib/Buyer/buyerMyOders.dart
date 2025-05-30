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

class BuyerMyOrdersPage extends StatefulWidget {
  BuyerMyOrdersPage({super.key});

  @override
  State<BuyerMyOrdersPage> createState() => _BuyerMyOrdersPagePageState();
}

class _BuyerMyOrdersPagePageState extends State<BuyerMyOrdersPage> {
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
        // title: _isSearching
        // ? TextField(
        //   onSubmitted: (value) {
        //     getSearchedOrders();
            
        //   },
        //   style: TextStyle(backgroundColor: Colors.transparent, color: Colors.white),
        //   controller: searchBox,
        //   decoration: InputDecoration(
        //     hintText: 'Search...', 
        //     hintStyle: TextStyle(color: Colors.white),
        //     border: InputBorder.none,
        //     prefixIcon: Icon(Icons.search, color: Colors.white, size: 30,) 
        //   ),
        // ): Text(''),
        actions: [
          // IconButton(
          //   onPressed: (){
          //     toggleSearch();
          // },
          // icon: Icon(_isSearching ? Icons.cancel: Icons.search), color: Colors.white, iconSize: 30,),

          IconButton(
            onPressed: (){
              
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
                        horizontal: 20,
                        vertical: 20
                      ),
                      child: Column(
                        children: [
                          Row(
                            
                            children: [
                              SizedBox(width: 10,),
                              Text(
                                'My orders',
                                style: TextStyle(
                                  fontFamily: 'RadioCanada',
                                  fontSize: 20,
                                  fontWeight: FontWeight.w500,
                                ),
                                )
                            ],
                          ),
                          SizedBox(height: 20,),
                          Container(
                            height: 500,
                            child: productList.isEmpty ? Center(child: CircularProgressIndicator())
                            : NotificationListener<ScrollNotification>(
                              onNotification: (ScrollNotification scrollInfo) {
                                if (!_isLoading && scrollInfo.metrics.pixels == scrollInfo.metrics.maxScrollExtent) {
                                  getMyOrderDetails(page: currentPage + 1);
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
                                      leading: Padding(
                                      padding: EdgeInsets.all(1),
                                      child: Image.memory(
                                        _safeDecodeImage(product.base64Image),
                                        width: 40,
                                        height: 40,
                                        fit: BoxFit.fill,
                                      ),
                                    ),
                                    title: Row(
                                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                      children: [
                                        Container(
                                          width: 80,
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
                                        width: 110,
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
                                    trailing: IconButton(
                                      onPressed: (){
                                        print(product.product_id);
                                        setState(() {
                                          removeProductId = product.product_id;
                                        });
                                        removeProduct();
                                      },
                                      icon: Icon(Icons.close_rounded)
                                      ),
                                    onTap: (){
                                    
                                    },
                                    )
                                  ),
                                  );
                                }
                                ),
                            ) 
                          )
                        ],
                      ),
                    ),
                  ),
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
                        orderTotalList.isNotEmpty ? '₱${orderTotalList[0].subTotal}' : '₱0.00',
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
                        orderTotalList.isNotEmpty ? '₱${orderTotalList[0].total}' : '₱0.00',
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
                    backgroundColor: Color.fromRGBO(88, 0, 146, 1),
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(15)
                    )
                  ),
                  onPressed: (){
                    Navigator.pushNamed(context, '/buyerCheckout');
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

