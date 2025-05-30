from app import app
from app import db
from flask import request, jsonify, session
import base64

#############################################################################################
#############################################################################################
##############################  G E T  C A R T  D E T A I L S  ##############################
#############################################################################################
#############################################################################################

@app.route('/getCartDetails', methods= ['GET'])
def getCartDetails():
    
    conn = db.get_db_connection()
    userEmail = session.get('email')
    page = int(request.args.get('page', 1))
    per_page = 2
    offset = (page - 1) * per_page
    
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT product_id, product_name, product_description, item_total_amount, order_quantity, product_photo1 FROM cart WHERE buyer = %s LIMIT %s OFFSET %s', (userEmail ,per_page, offset))
        my_cart = cursor.fetchall()

        for product in my_cart:
            if product['product_photo1']:
                product['product_photo'] = base64.b64encode(product['product_photo1']).decode('utf-8')
            else:
                product['product_photo'] = ''
            del product['product_photo1']
        
    
        return jsonify({'status': 'success', 'myCartDetails': my_cart}), 200
    except Exception as e:
        print(f"Error in /getProducts: {e}")
        return jsonify({'status': 'error', 'message': str(e)})
    
    finally:
        conn.close()
        

##########################################################################################################
##########################################################################################################
##############################  G E T  C A R T  T O T A L  S E L E C T E D  ##############################
##########################################################################################################
##########################################################################################################

@app.route('/getMyCartTotal', methods= ['GET'])
def getMyCartTotal():
    
    conn = db.get_db_connection()
    userEmail = session.get('email')
    page = int(request.args.get('page', 1))
    per_page = 2
    offset = (page - 1) * per_page
    
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT SUM(item_total_amount) as subTotal, SUM(item_total_amount) + MAX(delivery_fee) as total, MAX(delivery_fee) FROM my_orders WHERE buyer = %s AND buyer = %s;', (userEmail, userEmail))
        order_total_value = cursor.fetchall()

    
        return jsonify({'status': 'success', 'orderTotal': order_total_value}), 200
    except Exception as e:
        print(f"Error in /getProducts: {e}")
        return jsonify({'status': 'error', 'message': str(e)})
    
    finally:
        conn.close()