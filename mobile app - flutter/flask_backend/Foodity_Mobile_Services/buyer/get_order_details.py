from app import app
from app import db
from flask import request, jsonify, session
import base64



#######################################################
########  G E T  P R O D U C T  D E T A I L S  ########
#######################################################

@app.route('/get-order-details', methods= ['GET'])
def getOrderDetails():
    
    conn = db.get_db_connection()
    productId =session.get('order-product-id')
    productId_Int = int(productId)
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT order_id, product, order_date, payment_method, order_total, order_quantity, order_status, payment_status FROM orders WHERE order_id = %s', (productId_Int,))
        products = cursor.fetchall()
    
        return jsonify({'status': 'success', 'productDetails': products}), 200
    except Exception as e:
        print(f"Error in /getProducts: {e}")
        return jsonify({'status': 'error', 'message': str(e)})
    
    finally:
        conn.close()