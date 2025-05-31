from flask import Flask, jsonify, session
from flask import request
import mysql.connector # Add this import
from mysql.connector import Error
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
import math, random
import os
from datetime import datetime
import io
import base64
import sys
import webbrowser
import array as arr
from flask_caching import Cache
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = 'Haruki'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 
now = datetime.now()
current_date_time = now
CORS(app, resources={r"/api/": {"origins": "http://10.0.2.2:5000"}})

##############################################################################################################################
##############################################################################################################################
###########################################  D A T A B A S E  C O N N E C T I O N  ###########################################
##############################################################################################################################
##############################################################################################################################

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",    # Change if your DB is hosted elsewhere
            user="root",         # Replace with your DB user
            password="",         # Replace with your DB password
            database="foodity"  # Your database name
        )
        return conn
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None


###################################################################################################
###################################################################################################
###########################################  L O G I N  ###########################################
###################################################################################################
###################################################################################################

@app.route('/loginMobile', methods = ['POST', 'GET'])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    
    conn = get_db_connection()
    if conn is None:
        return  msg =='no database'
    
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute('SELECT * FROM accounts WHERE email = %s AND password = %s;', (email, password))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        session['loggedIn'] = True
        session['accounts_id'] = user['accounts_id']
        session['email'] = user["email"]
        session['first_name'] = user["firstName"]
        session['last_name'] = user["lastName"]
        session['account_type'] = user["account_type"]
        session['status'] = user['status']
        session['logged_in_time'] = current_date_time
            
        if user['status'] == 0:
            msg = 'approval'
        elif user['status'] == 1:
            if user['account_type'] == 'buyer':
                msg = 'buyer'
            elif user['account_type'] == 'courier':
                msg = 'courier'
        elif user['status'] == 3:
            msg = 'restricted'
        else:
            pass
        
    else:
        msg = 'Invalid email or password.'
    
    return jsonify({'status': 'success', 'message': msg})

# def get_product_from_db():
    
    # products = []
    
    # for product in productList:
    #     product_id, product_name, product_description, product_price, product_stocks, product_photo1 = product
        
    #     if product_photo1 and isinstance(product_photo1, (bytes, bytearray)):
    #         base64_image = base64.b64encode(product_photo1).decode('utf-8')
    #     else:
    #         base64_image = ''
        
    #     products.append({
    #         'product_id': product_id,
    #         'product_name': product_name,
    #         'product_description': product_description,
    #         'product_price': product_price,
    #         'product_stocks': product_stocks,
    #         'product_photo': base64_image,
    #     })
        
    # conn.close()
        
    # return productList
    


#############################################################################################
#############################################################################################
##############################  G E T  A L L  P R O D U C T S  ##############################
#############################################################################################
#############################################################################################


@app.route('/getProducts', methods= ['GET'])
def getProducts():
    page = int(request.args.get('page', 1))
    per_page = 2
    offset = (page - 1) * per_page
    conn = get_db_connection()
    
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT product_id, product_name, product_description, product_price, product_stocks, product_photo1 FROM products LIMIT %s OFFSET %s', (per_page, offset))
        products = cursor.fetchall()
        
        
        for product in products:
            if product['product_photo1']:
                product['product_photo'] = base64.b64encode(product['product_photo1']).decode('utf-8')
            else:
                product['product_photo'] = ''
            del product['product_photo1']
        
    
        return jsonify({'status': 'success', 'products': products})
    except Exception as e:
        print(f"Error in /getProducts: {e}")
        return jsonify({'status': 'error', 'message': str(e)})
    
    finally:
        conn.close()

####################################################################################
####################################################################################
##############################  S E A R C H  D A T A  ##############################
####################################################################################
####################################################################################

# @app.route('/searchData', methods= ['POST'])
# def SearchData():
#     data = request.get_json()
#     productName = data.get("productName")
#     session['productSearched'] = productName
    
#     return jsonify({'status': 'success', 'message': 'Product name saved to session'})


#######################################################################################################
#######################################################################################################
##############################  G E T  S E A R C H E D  P R O D U C T S  ##############################
#######################################################################################################
#######################################################################################################

@app.route('/getProductsSearch', methods= ['POST', 'GET'])
def getProductsSearched():
    data = request.get_json()
    productName = data.get("productName")
    per_page = 1
    conn = get_db_connection()
    
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT product_id, product_name, product_description, product_price, product_stocks, product_photo1 FROM products WHERE LOWER(product_name) LIKE LOWER(%s) LIMIT %s', ('%' + productName + '%', per_page))
        products = cursor.fetchall()
        
        
        for product in products:
            if product['product_photo1']:
                product['product_photo'] = base64.b64encode(product['product_photo1']).decode('utf-8')
            else:
                product['product_photo'] = ''
            del product['product_photo1']
        
    
        return jsonify({'status': 'success', 'searched': products})
    except Exception as e:
        print(f"Error in /getProducts: {e}")
        return jsonify({'status': 'error', 'message': str(e)})
    
    finally:
        conn.close()
        

#############################################################################################
#############################################################################################
##############################  S T O R E  P R O D U C T  I D  ##############################
#############################################################################################
#############################################################################################

@app.route('/storeProductId', methods= ['POST'])
def storeProductId():
    data = request.get_json()
    session['clickedProduct'] = data.get("productID")
    
    return jsonify({'status': 'success', 'message': 'Product Id saved to session'}), 200 

#############################################################################################
#############################################################################################
##############################  S T O R E  O R D E R  C O U N T  ############################
#############################################################################################
#############################################################################################

@app.route('/storeOrderCount', methods= ['POST'])
def storeOrderCount():
    data = request.get_json()
    session['orderCount'] = data.get("orderCount")
    order_quantity = session.get('orderCount')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    productId =session.get('clickedProduct')
    productId_Int = int(productId)
    cursor.execute('SELECT product_stocks FROM products WHERE product_id = %s AND product_id = %s;', (productId_Int, productId_Int))
    product_stocks = cursor.fetchone()
    session['db_stocks'] = product_stocks['product_stocks']
    db_stocks = session.get('db_stocks')
    if int(order_quantity) > db_stocks:
        return jsonify({'status': 'error', 'message': 'Low Stocks'}), 404
    else:
        
        conn = get_db_connection()
        productId =session.get('clickedProduct')
        order_quantity = session.get('orderCount')
        productId_Int = int(productId)
        userEmail = session.get('email')
        conn = get_db_connection()
        df = 40
        
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute('SELECT uploader FROM products WHERE product_id= %s AND product_id = %s;', (productId_Int, productId_Int))
            uploader = cursor.fetchone()
            session['uploader'] = uploader['uploader']
            cursor.execute('SELECT product_id, product_name, product_description, product_price, product_stocks, product_photo1, product_photo2, product_photo3, product_photo4, product_categories, product_variants FROM products WHERE product_id= %s AND product_id = %s;', (productId_Int, productId_Int))
            my_order = cursor.fetchone()
            cursor.execute('SELECT product_name FROM my_orders WHERE buyer = %s AND buyer = %s;', (userEmail, userEmail))
            orders = cursor.fetchall()
            cursor.execute('SELECT product_stocks FROM products WHERE product_id = %s AND product_id = %s;', (productId_Int, productId_Int))
            product_stocks = cursor.fetchone()
            session['db_stocks'] = product_stocks['product_stocks']
            db_stocks = session.get('db_stocks', None)
            if int(order_quantity) > db_stocks:
                msg = 'Low or no stocks'
                return jsonify({'status': 'error', 'message': msg}), 400
            else:
                updated_stocks = db_stocks - int(order_quantity)
            cursor.execute('UPDATE products SET product_stocks = %s WHERE product_id=%s', (updated_stocks, productId_Int))
            conn.commit()
        
            if orders is not None:
                if my_order['product_name'] != orders:
                    session['my_order_name'] = my_order['product_name']
                    session['my_order_description'] = my_order['product_description']
                    session['my_order_price'] = my_order['product_price']
                    session['my_order_pieces'] = my_order['product_stocks']
                    session['my_order_photo1'] = my_order['product_photo1']
                    session['my_order_photo2'] = my_order['product_photo2']
                    session['my_order_photo3'] = my_order['product_photo3']
                    session['my_order_photo4'] = my_order['product_photo4']
                    session['my_order_categories'] = my_order['product_categories']
                    session['my_order_variants'] = my_order['product_variants']
                    
                    
                    my_order_name = session.get('my_order_name', None)
                    my_order_description = session.get('my_order_description', None)
                    my_order_price = session.get('my_order_price', None)
                    my_order_photo1 = session.get('my_order_photo1', None)
                    my_order_photo2 = session.get('my_order_photo2', None)
                    my_order_photo3 = session.get('my_order_photo3', None)
                    my_order_photo4 = session.get('my_order_photo4', None)
                    my_order_categories = session.get('my_order_categories', None)
                    my_order_variants = session.get('my_order_variants', None)
                    uploader_name = session.get('uploader')
                    
                    total_item_price = float(my_order_price) * float(order_quantity)
                    
                    sql = "INSERT INTO my_orders (product_name, product_description, order_price, order_quantity, product_photo1, product_photo2, product_photo3, product_photo4, product_categories, product_variants, buyer, delivery_fee, item_total_amount, uploader) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
                    values = (my_order_name, my_order_description, my_order_price, order_quantity, my_order_photo1, my_order_photo2, my_order_photo3, my_order_photo4, my_order_categories, my_order_variants, userEmail, df, total_item_price, uploader_name)
                    cursor.execute(sql, values)
                    conn.commit()
                    cursor.close()
                    conn.close()
                    session.pop('my_order_name', None)
                    session.pop('my_order_description', None)
                    session.pop('my_order_price', None)
                    session.pop('my_order_pieces', None)
                    session.pop('my_order_photo1', None)
                    session.pop('my_order_photo2', None)
                    session.pop('my_order_photo3', None)
                    session.pop('my_order_photo4', None)
                    session.pop('my_order_categories', None)
                    session.pop('my_order_categories', None)
                    
            return jsonify({'status': 'success', 'message': 'OrderCount saved to session'}), 200 
        except Exception as e:
            print(f"Error in /getProducts: {e}")
            return jsonify({'status': 'error', 'message': str(e)})
        finally:
                conn.close()

        
    
    

###################################################################################################
###################################################################################################
##############################  G E T  P R O D U C T  D E T A I L S  ##############################
###################################################################################################
###################################################################################################

@app.route('/getProductDetails', methods= ['GET'])
def getProductDetails():
    
    conn = get_db_connection()
    productId =session.get('clickedProduct')
    productId_Int = int(productId)
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT product_id, product_name, product_description, product_price, product_stocks, product_photo1 FROM products WHERE product_id = %s', (productId_Int,))
        products = cursor.fetchall()
        
        
        for product in products:
            if product['product_photo1']:
                product['product_photo'] = base64.b64encode(product['product_photo1']).decode('utf-8')
            else:
                product['product_photo'] = ''
            del product['product_photo1']
        
    
        return jsonify({'status': 'success', 'productDetails': products}), 200
    except Exception as e:
        print(f"Error in /getProducts: {e}")
        return jsonify({'status': 'error', 'message': str(e)})
    
    finally:
        conn.close()


####################################################################################################
####################################################################################################
##############################  G E T  M Y  O R D E R  D E T A I L S  ##############################
####################################################################################################
####################################################################################################

@app.route('/getMyOrderDetails', methods= ['GET'])
def getMyOrderDetails():
    
    conn = get_db_connection()
    userEmail = session.get('email')
    page = int(request.args.get('page', 1))
    per_page = 2
    offset = (page - 1) * per_page
    
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT product_id, product_name, product_description, item_total_amount, order_quantity, product_photo1 FROM my_orders WHERE buyer = %s LIMIT %s OFFSET %s', (userEmail ,per_page, offset))
        my_products = cursor.fetchall()

        for product in my_products:
            if product['product_photo1']:
                product['product_photo'] = base64.b64encode(product['product_photo1']).decode('utf-8')
            else:
                product['product_photo'] = ''
            del product['product_photo1']
        
    
        return jsonify({'status': 'success', 'myOrderDetails': my_products}), 200
    except Exception as e:
        print(f"Error in /getProducts: {e}")
        return jsonify({'status': 'error', 'message': str(e)})
    
    finally:
        conn.close()
        

################################################################################################
################################################################################################
##############################  G E T  M Y  O R D E R  T O T A L  ##############################
################################################################################################
################################################################################################

@app.route('/getMyOrderTotal', methods= ['GET'])
def getMyOrderTotal():
    
    conn = get_db_connection()
    userEmail = session.get('email')
    page = int(request.args.get('page', 1))
    per_page = 2
    offset = (page - 1) * per_page
    
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT SUM(item_total_amount) as subTotal, SUM(item_total_amount) + MAX(delivery_fee) as total, MAX(delivery_fee) FROM cart WHERE buyer = %s AND buyer = %s;', (userEmail, userEmail))
        order_total_value = cursor.fetchall()

    
        return jsonify({'status': 'success', 'orderTotal': order_total_value}), 200
    except Exception as e:
        print(f"Error in /getProducts: {e}")
        return jsonify({'status': 'error', 'message': str(e)})
    
    finally:
        conn.close()

#############################################################################################
#############################################################################################
##############################  G E T  U S E R  D E T A I L S  ##############################
#############################################################################################
#############################################################################################

@app.route('/getUserDetails', methods= ['GET'])
def getUserDetails():
    
    conn = get_db_connection()
    productId =session.get('clickedProduct')
    userEmail = session.get('email')
    productId_Int = int(productId)
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT accounts_id, firstName, lastName, email, password, barangay, city, province, zip_code, account_type FROM accounts WHERE email = %s', (userEmail,))
        userDetails = cursor.fetchall()
        
        
    
        return jsonify({'status': 'success', 'userDetails': userDetails}), 200
    except Exception as e:
        print(f"Error in /userDetails: {e}")
        return jsonify({'status': 'error', 'message': str(e)})
    
    finally:
        conn.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True, use_reloader=False, processes=1, request_handler=None)
