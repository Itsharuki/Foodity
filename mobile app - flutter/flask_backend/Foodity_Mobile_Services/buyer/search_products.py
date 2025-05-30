from app import app
from app import db
from flask import request, jsonify, session
import base64

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
    conn = db.get_db_connection()
    
    
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
        