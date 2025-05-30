from app import app
from app import db
from flask import request, jsonify, session
import base64

##################################################################################################################
##################################################################################################################
##############################  R E M O V E  P R O D U C T  F R O M  M Y O R D E R  ##############################
##################################################################################################################
##################################################################################################################

@app.route('/remove_product', methods=['POST'])
def remove_product():
    data = request.get_json()
    product_id = data.get('remove_id')
    product_name = data.get('product_name')
    order_quantity = data.get('order_quantity')
    
    # Establish database connection
    conn= db.get_db_connection()
    
    #Fetch all users form the database
    cursor = conn.cursor(dictionary=True)
    cursor.execute('DELETE FROM my_orders WHERE product_id=%s AND product_id=%s', (product_id, product_id))
    conn.commit()
    
    cursor.execute('UPDATE products SET product_stocks = %s WHERE product_name=%s', (order_quantity, product_name))
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({'status': 'success', 'message': 'Product Removed'}), 200

############################################################################################################
############################################################################################################
##############################  R E M O V E  P R O D U C T  F R O M  C A R T  ##############################
############################################################################################################
############################################################################################################


@app.route('/remove_product_on_cart', methods=['POST'])
def remove_product_on_cart():
    data = request.get_json()
    product_id = data.get('remove_id')
    product_name = data.get('product_name')
    order_quantity = data.get('order_quantity')
    
    # Establish database connection
    conn= db.get_db_connection()
    
    #Fetch all users form the database
    cursor = conn.cursor(dictionary=True)
    cursor.execute('DELETE FROM cart WHERE product_id=%s AND product_id=%s', (product_id, product_id))
    conn.commit()
    
    cursor.execute('UPDATE products SET product_stocks = %s WHERE product_name=%s', (order_quantity, product_name))
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({'status': 'success', 'message': 'Product Removed'}), 200
