from app import app
from app import db
from flask import request, jsonify, session
import base64



#############################################################################################
#############################################################################################
##############################  S T O R E  O R D E R  C O U N T  ############################
#############################################################################################
#############################################################################################

@app.route('/storeOrderCount', methods= ['POST'])
def storeOrderCount():
    data = request.get_json()
    session['orderCount'] = data.get("orderCount")
    order_quantity = session.get('orderCount')
    conn = db.get_db_connection()
    cursor = conn.cursor(dictionary=True)
    productId =session.get('clickedProduct')
    productId_Int = int(productId)
    cursor.execute('SELECT product_stocks FROM products WHERE product_id = %s AND product_id = %s;', (productId_Int, productId_Int))
    product_stocks = cursor.fetchone()
    session['db_stocks'] = product_stocks['product_stocks']
    db_stocks = session.get('db_stocks')
    if int(order_quantity) > db_stocks:
        return jsonify({'status': 'error', 'message': 'Low Stocks'}), 404
    else:
        
        conn = db.get_db_connection()
        productId =session.get('clickedProduct')
        order_quantity = session.get('orderCount')
        productId_Int = int(productId)
        userEmail = session.get('email')
        conn = db.get_db_connection()
        df = 40
        
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute('SELECT uploader FROM products WHERE product_id= %s AND product_id = %s;', (productId_Int, productId_Int))
            uploader = cursor.fetchone()
            session['uploader'] = uploader['uploader']
            cursor.execute('SELECT product_id, product_name, product_description, product_price, product_stocks, product_photo1, product_photo2, product_photo3, product_photo4, product_categories, product_variants FROM products WHERE product_id= %s AND product_id = %s;', (productId_Int, productId_Int))
            my_order = cursor.fetchone()
            cursor.execute('SELECT product_name FROM my_orders WHERE buyer = %s AND buyer = %s;', (userEmail, userEmail))
            orders = cursor.fetchall()
            cursor.execute('SELECT product_stocks FROM products WHERE product_id = %s AND product_id = %s;', (productId_Int, productId_Int))
            product_stocks = cursor.fetchone()
            session['db_stocks'] = product_stocks['product_stocks']
            db_stocks = session.get('db_stocks', None)
            if int(order_quantity) > db_stocks:
                msg = 'Low or no stocks'
                return jsonify({'status': 'error', 'message': msg}), 400
            else:
                updated_stocks = db_stocks - int(order_quantity)
            cursor.execute('UPDATE products SET product_stocks = %s WHERE product_id=%s', (updated_stocks, productId_Int))
            conn.commit()
        
            if orders is not None:
                if my_order['product_name'] != orders:
                    session['my_order_name'] = my_order['product_name']
                    session['my_order_description'] = my_order['product_description']
                    session['my_order_price'] = my_order['product_price']
                    session['my_order_pieces'] = my_order['product_stocks']
                    session['my_order_photo1'] = my_order['product_photo1']
                    session['my_order_photo2'] = my_order['product_photo2']
                    session['my_order_photo3'] = my_order['product_photo3']
                    session['my_order_photo4'] = my_order['product_photo4']
                    session['my_order_categories'] = my_order['product_categories']
                    session['my_order_variants'] = my_order['product_variants']
                    
                    
                    my_order_name = session.get('my_order_name', None)
                    my_order_description = session.get('my_order_description', None)
                    my_order_price = session.get('my_order_price', None)
                    my_order_photo1 = session.get('my_order_photo1', None)
                    my_order_photo2 = session.get('my_order_photo2', None)
                    my_order_photo3 = session.get('my_order_photo3', None)
                    my_order_photo4 = session.get('my_order_photo4', None)
                    my_order_categories = session.get('my_order_categories', None)
                    my_order_variants = session.get('my_order_variants', None)
                    uploader_name = session.get('uploader')
                    
                    total_item_price = float(my_order_price) * float(order_quantity)
                    
                    sql = "INSERT INTO my_orders (product_name, product_description, order_price, order_quantity, product_photo1, product_photo2, product_photo3, product_photo4, product_categories, product_variants, buyer, delivery_fee, item_total_amount, uploader) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
                    values = (my_order_name, my_order_description, my_order_price, order_quantity, my_order_photo1, my_order_photo2, my_order_photo3, my_order_photo4, my_order_categories, my_order_variants, userEmail, df, total_item_price, uploader_name)
                    cursor.execute(sql, values)
                    conn.commit()
                    cursor.close()
                    conn.close()
                    session.pop('my_order_name', None)
                    session.pop('my_order_description', None)
                    session.pop('my_order_price', None)
                    session.pop('my_order_pieces', None)
                    session.pop('my_order_photo1', None)
                    session.pop('my_order_photo2', None)
                    session.pop('my_order_photo3', None)
                    session.pop('my_order_photo4', None)
                    session.pop('my_order_categories', None)
                    session.pop('my_order_categories', None)
                    
            return jsonify({'status': 'success', 'message': 'OrderCount saved to session'}), 200 
        except Exception as e:
            print(f"Error in /getProducts: {e}")
            return jsonify({'status': 'error', 'message': str(e)})
        finally:
                conn.close()
