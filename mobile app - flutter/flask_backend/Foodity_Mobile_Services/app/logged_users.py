
from app import app
from app import db
from flask import request, jsonify, session
from datetime import datetime
now = datetime.now()
current_date_time = now


########################################################
###############  L O G G E D  U S E R S  ###############
########################################################

def logged_users():
    logged_in_time = session.get('logged_in_time', None)
    logged_out_time = session.get('logged_out_time', None)
    first_name = session.get('first_name', None)
    last_name = session.get('last_name', None)
    email = session.get('email', None)
    account_type = session.get('account_type', None)
    
    # Database connection
    conn = get_db_connection()
        
    if conn is None:
        msg2 = 'No database'
        return redirect(url_for('register'))
        
    cursor = conn.cursor(dictionary=True)
        
    # SQL query to insert data
    sql = "INSERT INTO user_logs (firstName, lastName, email, acc_type, logged_in, logged_out) VALUES (%s, %s, %s, %s, %s, %s);"
    values = (first_name, last_name, email, account_type, logged_in_time, logged_out_time)

    cursor.execute(sql, values)
    conn.commit()  # Save changes to the database
    cursor.close()
    conn.close()