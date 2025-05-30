from app import app
from app import db
from flask import request, jsonify, session
import base64

#############################################################################################
#############################################################################################
##############################  G E T  U S E R  D E T A I L S  ##############################
#############################################################################################
#############################################################################################

@app.route('/getUserDetails', methods= ['GET'])
def getUserDetails():
    
    conn = db.get_db_connection()
    productId =session.get('clickedProduct')
    userEmail = session.get('email')
    productId_Int = int(productId)
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT accounts_id, firstName, lastName, email, password, barangay, city, province, zip_code, account_type FROM accounts WHERE email = %s', (userEmail,))
        userDetails = cursor.fetchall()
        
        
        
    
        return jsonify({'status': 'success', 'userDetails': userDetails}), 200
    except Exception as e:
        print(f"Error in /userDetails: {e}")
        return jsonify({'status': 'error', 'message': str(e)})
    
    finally:
        conn.close()