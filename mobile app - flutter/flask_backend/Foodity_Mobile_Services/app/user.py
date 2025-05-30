from app import app
from app import db
from flask import request, jsonify, session
from datetime import datetime
now = datetime.now()
current_date_time = now

###################################################################################################
###################################################################################################
###########################################  L O G I N  ###########################################
###################################################################################################
###################################################################################################

@app.route('/loginMobile', methods = ['POST', 'GET'])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    
    conn = db.get_db_connection()
    if conn is None:
        return  msg =='no database'
    
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute('SELECT * FROM accounts WHERE email = %s AND password = %s;', (email, password))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        session['loggedIn'] = True
        session['accounts_id'] = user['accounts_id']
        session['email'] = user["email"]
        session['first_name'] = user["firstName"]
        session['last_name'] = user["lastName"]
        session['account_type'] = user["account_type"]
        session['status'] = user['status']
        session['logged_in_time'] = current_date_time
            
        if user['status'] == 0:
            msg = 'approval'
        elif user['status'] == 1:
            if user['account_type'] == 'buyer':
                msg = 'buyer'
            elif user['account_type'] == 'courier':
                msg = 'courier'
        elif user['status'] == 3:
            msg = 'restricted'
        else:
            pass
        
    else:
        msg = 'Invalid email or password.'
    
    return jsonify({'status': 'success', 'message': msg})

# def get_product_from_db():
    
    # products = []
    
    # for product in productList:
    #     product_id, product_name, product_description, product_price, product_stocks, product_photo1 = product
        
    #     if product_photo1 and isinstance(product_photo1, (bytes, bytearray)):
    #         base64_image = base64.b64encode(product_photo1).decode('utf-8')
    #     else:
    #         base64_image = ''
        
    #     products.append({
    #         'product_id': product_id,
    #         'product_name': product_name,
    #         'product_description': product_description,
    #         'product_price': product_price,
    #         'product_stocks': product_stocks,
    #         'product_photo': base64_image,
    #     })
        
    # conn.close()
        
    # return productList
    