from app import app
from app import db
from flask import request, jsonify, session
import base64


###############################################################################################
###############################################################################################
##############################  G E T  O R D E R S  T O  P A Y  ##############################
###############################################################################################
###############################################################################################

@app.route('/getOrdersToPay', methods= ['GET'])
def getOrdersToPay():
    
    conn = db.get_db_connection()
    userEmail = session.get('email')
    page = int(request.args.get('page', 1))
    per_page = 2
    offset = (page - 1) * per_page
    
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT order_id, product, order_date, payment_method, order_total, order_quantity, order_status, payment_status FROM orders WHERE buyer_email = %s AND order_status = 0 AND payment_status = 0 OR buyer_email = %s AND order_status = 0 AND payment_status = 1 LIMIT %s OFFSET %s', (userEmail , userEmail, per_page, offset))
        orders = cursor.fetchall()

        return jsonify({'status': 'success', 'orderDetails': orders}), 200
    except Exception as e:
        print(f"Error in /getProducts: {e}")
        return jsonify({'status': 'error', 'message': str(e)})
    
    finally:
        conn.close()


################################################################################################
################################################################################################
##############################  G E T  O R D E R S  T O  S H I P  ##############################
################################################################################################
################################################################################################

@app.route('/getOrdersToShip', methods= ['GET'])
def getOrdersToShip():
    
    conn = db.get_db_connection()
    userEmail = session.get('email')
    page = int(request.args.get('page', 1))
    per_page = 2
    offset = (page - 1) * per_page
    
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT order_id, product, order_date, payment_method, order_total, order_quantity, order_status, payment_status FROM orders WHERE buyer_email = %s AND order_status = 1 AND payment_status = 0 OR buyer_email = %s AND order_status = 1 AND payment_status = 1 LIMIT %s OFFSET %s', (userEmail , userEmail, per_page, offset))
        orders = cursor.fetchall()

        return jsonify({'status': 'success', 'orderDetails': orders}), 200
    except Exception as e:
        print(f"Error in /getProducts: {e}")
        return jsonify({'status': 'error', 'message': str(e)})
    
    finally:
        conn.close()

#####################################################################################################
#####################################################################################################
##############################  G E T  O R D E R S  C O M P L E T E D  ##############################
#####################################################################################################
#####################################################################################################

@app.route('/getOrdersCompleted', methods= ['GET'])
def getOrdersCompleted():
    
    conn = db.get_db_connection()
    userEmail = session.get('email')
    page = int(request.args.get('page', 1))
    per_page = 2
    offset = (page - 1) * per_page
    
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT order_id, product, order_date, payment_method, order_total, order_quantity, order_status, payment_status FROM orders WHERE buyer_email = %s AND order_status = 2 AND payment_status = 0 OR uyer_email = %s AND order_status = 2 AND payment_status = 1 LIMIT %s OFFSET %s', (userEmail , userEmail, per_page, offset))
        orders = cursor.fetchall()

        return jsonify({'status': 'success', 'orderDetails': orders}), 200
    except Exception as e:
        print(f"Error in /getProducts: {e}")
        return jsonify({'status': 'error', 'message': str(e)})
    
    finally:
        conn.close()