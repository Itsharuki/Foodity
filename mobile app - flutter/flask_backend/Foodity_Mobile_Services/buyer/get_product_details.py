from app import app
from app import db
from flask import request, jsonify, session
import base64


###################################################################################################
###################################################################################################
##############################  G E T  P R O D U C T  D E T A I L S  ##############################
###################################################################################################
###################################################################################################

@app.route('/getProductDetails', methods= ['GET'])
def getProductDetails():
    
    conn = db.get_db_connection()
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