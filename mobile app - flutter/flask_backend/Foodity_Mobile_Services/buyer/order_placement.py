from app import app
from app import db
from flask import request, jsonify, session
import base64
from datetime import datetime
now = datetime.now()
current_date_time = now

############################################################################################
############################################################################################
##############################  O R D E R  P L A C E M E N T  ##############################
############################################################################################
############################################################################################

@app.route('/orderPlacement', methods=['get', 'post'])
def orderPlacement():
    message = ''

    data = request.get_json()
    payment_type = data.get('selectedPaymentMethod')
    # Establish database connection
    conn= db.get_db_connection()
    
    active_email = session.get('email', None)
    active_user = session.get('accounts_id', None)
    uploader_email = session.get('uploader', None)
    order_status = 0
    
    if payment_type == 'cash':
        payment_status = 0
    else:
        payment_status = 1
    
    # Handle failed connection gracefully
    if conn is None:
        print('Database connection failed.')
    
    #Fetch all users form the database
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT CONCAT(firstName ," ",  lastName) as name, email, CONCAT("Barangay"," ", barangay ,", ", city ,",", province ,", ", zip_code) as address, status FROM accounts WHERE accounts_id=%s AND accounts_id=%s', (active_user, active_user))
    checkout_details = cursor.fetchone()
    cursor.execute('SELECT GROUP_CONCAT(product_name) as products FROM my_orders WHERE buyer = %s AND buyer = %s;', (active_email, active_email))
    order_display = cursor.fetchone()
    cursor.execute('SELECT SUM(order_quantity) as order_count FROM my_orders WHERE buyer = %s AND buyer = %s;', (active_email, active_email))
    order_count = cursor.fetchone()
    cursor.execute('SELECT SUM(item_total_amount) as subTotal, SUM(item_total_amount) + MAX(delivery_fee) as total, MAX(delivery_fee) FROM my_orders WHERE buyer = %s AND buyer = %s;', (active_email, active_email))
    order_total_value = cursor.fetchone()
    
    session['buyer_name'] = checkout_details['name']
    session['buyer_loc'] = checkout_details['address']
    session['order_price'] = order_total_value['subTotal']
    session['order_total'] = order_total_value['total']
    session['order_count'] = order_count['order_count']
    session['order_display'] = order_display['products']
    
    name_of_buyer = session.get('buyer_name', None)
    buyer_loc = session.get('buyer_loc', None)
    order_price = session.get('order_price', None)
    order_total = session.get('order_total', None)
    count_of_order = session.get('order_count', None)
    order_name = session.get('order_display', None)
    admin_com = order_total * 0.05
    
    sql = "INSERT INTO orders (product ,buyer_name, buyer_email, buyer_location, order_date, payment_method, order_price, order_total, order_quantity, order_status, payment_status, uploader, admin_com) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
    values = (order_name ,name_of_buyer, active_email, buyer_loc, current_date_time, payment_type, order_price, order_total, count_of_order, order_status, payment_status, uploader_email, admin_com)
    cursor.execute(sql, values)
    conn.commit()
    
    cursor.execute('DELETE FROM my_orders WHERE buyer=%s AND buyer=%s', (active_email,active_email))
    conn.commit()
    cursor.close()
    conn.close()
    
    session.pop('buyer_name', None)
    session.pop('buyer_loc', None)
    session.pop('order_price', None)
    session.pop('order_total', None)
    session.pop('order_display', None)
    
    return jsonify({'status': 'success'}), 200