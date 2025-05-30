from app import app
from app import db
from flask import request, jsonify, session
from datetime import datetime
now = datetime.now()
current_date_time = now
from app import logged_users



#############################################
################  L O G I N  ################
#############################################

@app.route('/logout')
def logout():
    session['logged_out_time'] = current_date_time
    logged_users()
    session.clear()
    return jsonify({'status': 'success'}), 200