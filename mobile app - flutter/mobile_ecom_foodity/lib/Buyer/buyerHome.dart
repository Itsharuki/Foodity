import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:typed_data'; //image bytes
import 'package:flutter/services.dart'; //decode image
import 'package:cached_network_image/cached_network_image.dart';
import 'package:mobile_ecom_foodity/Url/AllUrl.dart';
import 'package:mysql1/mysql1.dart';
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

class BuyerHome extends StatefulWidget {
  const BuyerHome({super.key});

  @override
  State<BuyerHome> createState() => _BuyerHomeState();
}

class _BuyerHomeState extends State<BuyerHome> {

  bool _isSearching = false;
  TextEditingController searchBox = TextEditingController();

//############################################//
//#############  B A C K  E N D  #############//
//############################################//

List<dynamic> productList = [];
int currentPage = 1;
bool _isLoading = false;
int productId_Value = 0;


void toggleSearch(){ //search products icons
  setState(() {
    _isSearching = !_isSearching;
    if(!_isSearching){
      searchBox.clear();
    }
  });
}

Future<void> productID() async{

    final response = await DioCookie.dio.post(
    '$globalurl/storeProductId',

    data: {
      'productID': productId_Value,
    },);
    print(response.statusCode);
    if (response.statusCode == 200){
      Navigator.pushNamed(context, '/buyerProductPage');
    }

}


Future<void> getProductSearched() async{
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


Future<void> getProducts({int page = 1}) async{ 
  if (_isLoading) return;

  setState(() {
    _isLoading = true;
  });
  final url = Uri.parse('$globalurl/getProducts?page=$page');

  try{
    final products = await http.get(
    url,
    headers: {
      'Accept': 'application/json'
    }
    ).timeout(
      Duration(
        seconds: 500
      )
    );

  if (products.statusCode == 200){
    var decoded = jsonDecode(products.body);
    setState(() {
    if (page == 1){
      productList = List<Product>.from((decoded['products'] as List).map((product) => Product.fromJson(product)).toList());
    }else{
      productList.addAll(List<Product>.from((decoded['products'] as List).map((product) => Product.fromJson(product))));
    }
    currentPage = page;
    });
  }else{
    throw Exception('Failed loading products');
  }
  } catch (e){
    print("Error loading products: $e");
    await Future.delayed(Duration(seconds: 2));
    await getProducts(page: page);
  }

  setState(() {
    _isLoading = false;
  });
  
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
void initState() {
  super.initState();
  getProducts(page: currentPage);
}

//##############################################//
//#############  F R O N T  E N D  #############//
//##############################################//


  @override
  Widget build(BuildContext context) {
    return Scaffold(
      extendBodyBehindAppBar: true,
      appBar: AppBar(
        automaticallyImplyLeading: false,
        backgroundColor: Colors.transparent,
        title: _isSearching
        ? TextField(
          onSubmitted: (value) {
            getProductSearched();
            
          },
          style: TextStyle(backgroundColor: Colors.transparent, color: Colors.white),
          controller: searchBox,
          decoration: InputDecoration(
            hintText: 'Search...', 
            hintStyle: TextStyle(color: Colors.white),
            border: InputBorder.none,
            prefixIcon: Icon(Icons.search, color: Colors.white, size: 30,) 
          ),
        ): Text(''),
        actions: [
          IconButton(
            onPressed: (){
              toggleSearch();
          },
          icon: Icon(_isSearching ? Icons.cancel: Icons.search), color: Colors.white, iconSize: 30,),

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
          color: Colors.white,
          image: DecorationImage(image: AssetImage('assets/login/all_bg.png'), fit: BoxFit.cover)
        ),
        child: productList.isEmpty ? Center(child: CircularProgressIndicator())
        : NotificationListener<ScrollNotification>(
          onNotification: (ScrollNotification scrollInfo) {
            if (!_isLoading && scrollInfo.metrics.pixels == scrollInfo.metrics.maxScrollExtent) {
              getProducts(page: currentPage + 1);
              return true;
            }
            return false;
          },
        child: Column(
          children: [
            Container(height: 50,),
            Expanded(child: Padding(
          padding: const EdgeInsets.all(8.0),
          child: GridView.builder(
            itemCount: productList.length ,
            gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: 2,
              crossAxisSpacing: 10,
              mainAxisSpacing: 10,
              childAspectRatio: 3 / 4,
              ),
            itemBuilder: (context, index){
              final product = productList[index];
              return InkWell(
                onTap: (){
                  print(product.product_id);
                  setState(() {
                    productId_Value = product.product_id;
                  });
                  productID();
                },
                child: Card(
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(10)),
                  elevation: 4,
                  child: Padding(
                    padding: const EdgeInsets.all(8.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Expanded(child: ClipRRect(
                          borderRadius: BorderRadius.circular(8),
                          child: Image.memory( //image
                            _safeDecodeImage(product.base64Image),
                            width: double.infinity,
                            fit: BoxFit.cover,
                          ),
                        ),
                        ),
                        SizedBox(height: 8,),
                        Text(
                          product.product_name,
                          style: TextStyle(
                            fontWeight: FontWeight.bold
                          ),),
                        Align(alignment: Alignment.centerRight,
                        child: Text(
                            '₱${product.product_price.toStringAsFixed(2)}',
                            style: TextStyle(
                              color: Colors.purple
                            ),),)
                        
                      ],
                    ),),
                    
              ),
              );
            }),),),
            Container(
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
                        getProducts();
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
                        Navigator.pushNamed(context, '/buyerMyOrders');
                      }, icon: Container(
                        width: 30,
                        height: 30,
                        child: Image(image: AssetImage('assets/icons/basket.png'), fit: BoxFit.contain,),
                      ),
                      iconSize: 20,
                      ),
                      Text(
                        'My orders',
                        style: TextStyle(fontFamily: 'RadioCanada', fontSize: 12, fontWeight: FontWeight.bold),),
                      Spacer()
                    ],
                  ),
                  Spacer(),
                  Column(
                    children: [
                      Spacer(),
                      IconButton(onPressed: (){
                        Navigator.pushNamed(context, '/buyerMe');
                      }, icon: Container(
                        width: 30,
                        height: 30,
                        child: Image(image: AssetImage('assets/icons/user.png'), fit: BoxFit.contain,),
                      ),
                      iconSize: 20,
                      ),
                      Text(
                        'Me',
                        style: TextStyle(fontFamily: 'RadioCanada', fontSize: 12, fontWeight: FontWeight.bold),),
                      Spacer()
                    ],
                  ),
                  Spacer(),
                ],
              ),
              )
          ],
        ) 
        )
        )
    );
  }
}