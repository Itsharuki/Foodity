from app import app
from app import db
from flask import request, jsonify, session
import base64

################################################
##########  C A R T  C H E C K O U T  ##########
################################################

@app.route('/cart-checkout', methods=['get', 'post'])
def buyer_cart_checkout():
    message = ''
    data = request.get_json()
    selected_items = data.get('product_Ids', [])
    
    # Establish database connection
    conn= db.get_db_connection()
    uploader_email = session.get('uploader', None)
    active_email = session.get('email', None)
    
        
    #Fetch all users form the database
    cursor = conn.cursor(dictionary=True)
    
    for selected_values in selected_items:
        cursor.execute('INSERT INTO my_orders SELECT * FROM cart WHERE product_id = %s  AND buyer IN(SELECT buyer FROM cart WHERE product_id = %s)', (selected_values, selected_values))
        cursor.execute('DELETE FROM cart WHERE product_id = %s AND product_id = %s', (selected_values, selected_values))
        conn.commit()
        
    cursor.close()
    conn.close()
    
    return jsonify({"status": "success", "message": "Checkout complete"})