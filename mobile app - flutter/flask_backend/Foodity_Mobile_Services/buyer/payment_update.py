from app import app
from app import db
from flask import request, jsonify, session
import base64


##############################################
########  P A Y M E N T  U P D A T E  ########
##############################################


@app.route('/payment-update', methods= ['POST'])
def payment_udpate():
    data = request.get_json()
    order_id = data.get("productID")
    payment_status = data.get('payment_status')
    
    conn = db.get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('UPDATE orders SET payment_status = %s WHERE order_id = %s', (payment_status, order_id))
        conn.commit()
        return jsonify({'status': 'success', 'message': 'Payment Updated'}), 200 
    except Exception as e:
        print(f"Error in /payment-update: {e}")
        return jsonify({'status': 'error', 'message': str(e)})
    finally:
        conn.close()