from app import app
from app import db
from flask import request, jsonify, session
import base64



###########################################################################################
###########################################################################################
##############################  S T O R E  C A R T  C O U N T  ############################
###########################################################################################
###########################################################################################

@app.route('/storeCartCount', methods= ['POST'])
def storeCartCount():
    data = request.get_json()
    session['cartCount'] = data.get("cartCount")
    cart_quantity = session.get('cartCount')
    conn = db.get_db_connection()
    cursor = conn.cursor(dictionary=True)
    productId =session.get('clickedProduct')
    productId_Int = int(productId)
    cursor.execute('SELECT product_stocks FROM products WHERE product_id = %s AND product_id = %s;', (productId_Int, productId_Int))
    product_stocks = cursor.fetchone()
    session['db_stocks'] = product_stocks['product_stocks']
    db_stocks = session.get('db_stocks')
    if int(cart_quantity) > db_stocks:
        return jsonify({'status': 'error', 'message': 'Low Stocks'}), 404
    else:
        
        conn = db.get_db_connection()
        productId =session.get('clickedProduct')
        order_quantity = session.get('cartCount')
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
            my_cart = cursor.fetchone()
            cursor.execute('SELECT product_name FROM cart WHERE buyer = %s AND buyer = %s;', (userEmail, userEmail))
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
                if my_cart['product_name'] != orders:
                    session['my_order_name'] = my_cart['product_name']
                    session['my_order_description'] = my_cart['product_description']
                    session['my_order_price'] = my_cart['product_price']
                    session['my_order_pieces'] = my_cart['product_stocks']
                    session['my_order_photo1'] = my_cart['product_photo1']
                    session['my_order_photo2'] = my_cart['product_photo2']
                    session['my_order_photo3'] = my_cart['product_photo3']
                    session['my_order_photo4'] = my_cart['product_photo4']
                    session['my_order_categories'] = my_cart['product_categories']
                    session['my_order_variants'] = my_cart['product_variants']
                    
                    
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
                    
                    sql = "INSERT INTO cart (product_name, product_description, order_price, order_quantity, product_photo1, product_photo2, product_photo3, product_photo4, product_categories, product_variants, buyer, delivery_fee, item_total_amount, uploader) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
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
                    
                elif my_cart['product_name'] == orders:
                    session['my_order_price'] = my_cart['product_price']
                    session['my_order_name'] = my_cart['product_name']
                    my_order_name = session.get('my_order_name', None)
                    uploader_name = session.get('uploader')
                    
                    my_order_price = session.get('my_order_price', None)
                    cursor.execute('SELECT order_quantity FROM cart WHERE product_name= %s AND uploader=%s AND buyer = %s;', (my_order_name, uploader_name, userEmail))
                    my_cart_quantity = cursor.fetchone()
                    cursor.execute('SELECT item_total_amount FROM cart WHERE product_name= %s AND uploader=%s AND buyer = %s;', (my_order_name, uploader_name, userEmail))
                    my_cart_amount = cursor.fetchone()
                    
                    total_item_price = float(my_order_price) * float(order_quantity)
                    
                    cart_quantity_update = order_quantity + int(my_cart_quantity)
                    cart_update_amount = total_item_price + float(my_cart_amount)
                    
                    cursor.execute('UPDATE cart SET order_quantity= %s AND item_total_amount=%s WHERE product_name= %s AND uploader=%s AND buyer = %s;', (cart_quantity_update, cart_update_amount, my_order_name, uploader_name, userEmail))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    
                    return jsonify({'status': 'success', 'message': 'cartCount saved to session'}), 200
                    
                    
                    
            return jsonify({'status': 'success', 'message': 'cartCount saved to session'}), 200 
        except Exception as e:
            print(f"Error in /getProducts: {e}")
            return jsonify({'status': 'error', 'message': str(e)})
        finally:
                conn.close()
