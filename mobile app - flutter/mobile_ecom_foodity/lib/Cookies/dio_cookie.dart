import 'package:dio/dio.dart';
import 'package:cookie_jar/cookie_jar.dart';
import 'package:dio_cookie_manager/dio_cookie_manager.dart';
import 'package:path_provider/path_provider.dart';

import 'dart:io';

class DioCookie {
  static late Dio dio;

  static Future<void> init() async{
    dio = Dio();


    // Store cookies
    Directory dir = await getApplicationDocumentsDirectory();

    final cookieJar = PersistCookieJar(storage: FileStorage('${dir.path}/.cookies/'));

    dio.interceptors.add(CookieManager(cookieJar));
  }
}