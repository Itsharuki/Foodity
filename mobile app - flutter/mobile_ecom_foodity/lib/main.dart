import 'package:flutter/material.dart';
import 'package:mobile_ecom_foodity/Buyer/buyerCart.dart';
import 'package:mobile_ecom_foodity/Buyer/buyerCheckout.dart';
import 'package:mobile_ecom_foodity/Buyer/buyerCompleted.dart';
import 'package:mobile_ecom_foodity/Buyer/buyerHome.dart';
import 'package:mobile_ecom_foodity/Buyer/buyerMe.dart';
import 'package:mobile_ecom_foodity/Buyer/buyerMyOders.dart';
import 'package:mobile_ecom_foodity/Buyer/buyerProductPage.dart';
import 'package:mobile_ecom_foodity/Buyer/buyerToPay.dart';
import 'package:mobile_ecom_foodity/Buyer/buyerToShip.dart';
import 'package:mobile_ecom_foodity/Buyer/orderDetails.dart';
import 'package:mobile_ecom_foodity/Cookies/dio_cookie.dart';
import 'package:mobile_ecom_foodity/Courier/courierHome.dart';
import 'package:mobile_ecom_foodity/Login/LoginPage.dart';

// 

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  FlutterError.onError = (FlutterErrorDetails details) {
    FlutterError.dumpErrorToConsole(details);
  };
  await DioCookie.init();
  runApp(const Foodity());
}


class Foodity extends StatelessWidget {
  const Foodity({
    super.key,
    });
  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: ThemeData(fontFamily: 'RadioCanada'),
      initialRoute: '/',
      routes: {
        '/': (context) => LoginPage(),
        '/buyerHome': (context) => BuyerHome(),
        '/buyerProductPage': (context) => BuyerProductPage(),
        '/buyerCheckout' : (context) => BuyerCheckoutPage(),
        '/buyerMyOrders' : (context) => BuyerMyOrdersPage(),
        '/buyerCart' : (context) => BuyerCartPage(),
        '/buyerMe' : (context) => BuyerMyProfile(),
        '/buyerToPay' : (context) => BuyerToPay(),
        '/buyerToShip' : (context) => BuyerToShip(),
        '/buyerCompleted' : (context) => BuyerCompleted(),
        '/orderDetailsPage' : (context) => OrderDetailsPage(),
        '/courierHome' : (context) => CourierHome(),
      },
    );
    }
    }