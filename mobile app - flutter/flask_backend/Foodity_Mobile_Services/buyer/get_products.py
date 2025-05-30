from app import app
from app import db
from flask import request, jsonify, session
import base64


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
    conn = db.get_db_connection()
    
    
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