from app import app
from app import db
from flask import request, jsonify, session
import base64

#############################################################################################
#############################################################################################
##############################  G E T  P R O F I L E  D E T A I L S  ##############################
#############################################################################################
#############################################################################################

@app.route('/getProfileDetails', methods= ['GET'])
def getProfileDetails():
    
    conn = db.get_db_connection()
    userEmail = session.get('email')
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT accounts_id, firstName, lastName, email, password, barangay, city, province, zip_code, account_type, profile_pic FROM accounts WHERE email = %s', (userEmail,))
        profileDetails = cursor.fetchall()
        
        for profile in profileDetails:
            if profile['profile_pic']:
                profile['profile_pic_decoded'] = base64.b64encode(profile['profile_pic']).decode('utf-8')
            else:
                profile['profile_pic_decoded'] = ''
            del profile['profile_pic']
    
        return jsonify({'status': 'success', 'profileDetails': profileDetails}), 200
    except Exception as e:
        print(f"Error in /getProfileDetails: {e}")
        return jsonify({'status': 'error', 'message': str(e)})
    
    finally:
        conn.close()