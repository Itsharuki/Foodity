from flask import Flask, render_template, redirect, url_for, session, flash
from flask import request
import mysql.connector # Add this import
from mysql.connector import Error
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
import math, random
import os
from datetime import datetime
import io
import base64
import sys
import webbrowser
import array as arr
from flask_caching import Cache

config = {
    "DEBUG": True,
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 300
}

app = Flask(__name__)
app.config.from_mapping(config)
cache = Cache(app)
app.secret_key = 'Haruki'

now = datetime.now()
current_date_time = now

##############################################################################################################################
##############################################################################################################################
###########################################  D A T A B A S E  C O N N E C T I O N  ###########################################
##############################################################################################################################
##############################################################################################################################

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",    # Change if your DB is hosted elsewhere
            user="root",         # Replace with your DB user
            password="haruki1315",         # Replace with your DB password
            database="foodity"  # Your database name
        )
        return conn
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None
    

###################################################################################################
###################################################################################################
###########################################  L O G I N  ###########################################
###################################################################################################
###################################################################################################

@app.route('/')
def home():
    return render_template('login.html')


@app.route('/login', methods=['GET' ,'POST'])
def login():
    msg = ''
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['pass']
        
        # Database connection
        conn = get_db_connection()
        if conn is None:
            flash('Database connection failed.', 'danger')
            return render_template('login.html')
        
        cursor = conn.cursor(dictionary=True)
        
        #Database Command
        cursor.execute('SELECT * FROM accounts WHERE email = %s AND password = %s;', (email, password))
        user = cursor.fetchone()
        
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
                msg = 'Account still for approval'
                return render_template('login.html', msg = msg)
            elif user['status'] == 1:
                if user['account_type'] == 'admin':
                    return redirect(url_for('admin'))
                elif user['account_type'] == 'seller':
                    return redirect(url_for('seller_dashboard'))
                elif user['account_type'] == 'buyer':
                    return redirect(url_for('buyer_home'))
                elif user['account_type'] == 'courier':
                    return redirect(url_for('foodity_express_dashboard'))
            elif user['status'] == 3:
                msg = 'Account is restricted'
                return render_template('login.html', msg = msg)
            else:
                pass
            
        else:
            msg = 'Invalid email or password.'
            
    return render_template('login.html', msg = msg)

########################################################################################################
###########################################  M A I L  O T P  ###########################################
########################################################################################################

def generateOTP():
    random_pass = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    length = len(random_pass)
    OneTimePass = ''
    
    for i  in range(6):
        OneTimePass += random_pass[math.floor(random.random() * length)]
        
    return OneTimePass

# FLASK MAIL CONFIGURATION
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'foodity2024@gmail.com'
app.config['MAIL_PASSWORD'] = 'ieuh galc cbgf kmbk'  
app.config['MAIL_DEFAULT_SENDER'] = 'foodity2024@gmail.com'

mail = Mail(app)

@app.route('/resetOTP', methods=['GET', 'POST'])
def send_mail():
    if request.method == 'POST':
        recipient = request.form['email']
        subject = 'RESET PASSWORD CODE'
        message_body = generateOTP()
        session['emailOTP'] = recipient
        session['One_Time_Password'] = message_body
        # Database connection
        conn = get_db_connection()
        
        if conn is None:
            msg2 = 'No database'
            return redirect(url_for('send_mail'))
        
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('SELECT * FROM accounts WHERE email =%s AND email=%s;', (recipient, recipient))
        user = cursor.fetchone()
        
        if  user is None:
            msg2 = 'Account does not exists.'
            cursor.close()
            conn.close()
            return render_template('login.html', msg = msg2)
        else:
            # Compose the message
            msg = Message(
                subject=subject,
                recipients=[recipient],
                body=message_body)
            
            # Send the email
            try:
                mail.send(msg)
                cursor.close()
                conn.close()
            except Exception as e:
                message = 'failed'
                cursor.close()
                conn.close()
            return redirect(url_for('send_mail'))

    return render_template('password_otp.html')

############################################################################################################
###########################################  S U B M I T  O T P  ###########################################
############################################################################################################

@app.route('/submit_otp', methods=['GET', 'POST'])
def submit_otp():
    if request.method == 'POST':
        otp_input = request.form['otp_code']
        OneTimePass = session.get('One_Time_Password', None)
        
        if OneTimePass == otp_input:
            return redirect(url_for('new_pass'))
        else:
            message = "Invalid OTP code"
            return render_template('password_otp.html', msg = message)
        

    return render_template('password_otp.html')

################################################################################################################
###########################################  N E W  P A S S W O R D  ###########################################
################################################################################################################

@app.route('/new_pass', methods=['GET', 'POST'])
def new_pass():
    if request.method == 'POST':
        emailOTP = session.get('emailOTP', None)
        new_password = request.form['new_pass']
        confirm_new_password = request.form['confirm_new_pass']
        
        
        # Database connection
        conn = get_db_connection()
        
        if conn is None:
            msg2 = 'No database'
            return redirect(url_for('new_pass'))
        
        if new_password == confirm_new_password:
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute('UPDATE accounts SET password = %s WHERE email=%s;', (new_password, emailOTP))
            conn.commit()  # Save changes to the database
            cursor.close()
            conn.close()
            message = 'Password Updated Successfully'
            return render_template('login.html', msg2 = message)
    

    return render_template('new_pass.html')

#########################################################################################################
###########################################  R E G I S T E R  ###########################################
#########################################################################################################

@app.route('/register')
def register():
    return render_template('registration.html')


@app.route('/register', methods=['GET', 'POST'])
def sign_up():
    msg2 = ''
    if request.method == 'POST':
        fName = request.form['firstName']
        lName = request.form['lastName']
        email = request.form['email']
        password = request.form['password']
        confirm_password =  request.form['confirm_password']
        barangay = request.form['brgy']
        city = request.form['city']
        province = request.form['province']
        zip_code = request.form['region']
        account_type = request.form['account_type_dropdown']
        buyer_valid_id = request.files['buyer_valid_id']
        seller_valid_id = request.files['seller_valid_id']
        seller_documents = request.files['seller_documents']
        
        seller_status = 0
        buyer_status = 1
        
        filename =secure_filename(seller_documents.filename)
        mimetype = seller_documents.mimetype
        
        
        # Database connection
        conn = get_db_connection()
        
        if conn is None:
            msg2 = 'No database'
            return redirect(url_for('register'))
        
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('SELECT * FROM accounts WHERE email = %s AND email=%s;', (email, email))
        user = cursor.fetchone()
        
        if user is not None:
            msg2 = 'Account already exists.'
            return render_template('registration.html', msg2 = msg2)
        else:
            if password == confirm_password:
                if account_type == 'seller':
                    # SQL query to insert data
                    sql = "INSERT INTO accounts (firstName, lastName, email, password, barangay, city, province, zip_code, account_type, valid_id, documents, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
                    values = (fName, lName, email, password, barangay, city, province, zip_code, account_type, seller_valid_id.read(), seller_documents.read(), seller_status)
                    msg2 = 'Account Created Successfully!'

                    cursor.execute(sql, values)
                    conn.commit()  # Save changes to the database
                    cursor.close()
                    conn.close()
                    return render_template('login.html', msg2 = msg2)
                
                elif account_type == 'buyer':
                    # SQL query to insert data
                    sql = "INSERT INTO accounts (firstName, lastName, email, password, barangay, city, province, zip_code, account_type, valid_id, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
                    values = (fName, lName, email, password, barangay, city, province, zip_code, account_type, buyer_valid_id.read(), buyer_status)
                    msg2 = 'Account Created Successfully!'


                    cursor.execute(sql, values)
                    conn.commit()  # Save changes to the database
                    cursor.close()
                    conn.close()
                    return render_template('login.html', msg2 = msg2)
                elif account_type == 'courier':
                    # SQL query to insert data
                    sql = "INSERT INTO accounts (firstName, lastName, email, password, barangay, city, province, zip_code, account_type, valid_id, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
                    values = (fName, lName, email, password, barangay, city, province, zip_code, account_type, buyer_valid_id.read(), buyer_status)
                    msg2 = 'Account Created Successfully!'


                    cursor.execute(sql, values)
                    conn.commit()  # Save changes to the database
                    cursor.close()
                    conn.close()
                    return render_template('login.html', msg2 = msg2)
            else:
                msg2 = 'Password does not match'
                return render_template('registration.html', msg2 = msg2)

######################################################################################################
###########################################  L O G  O U T  ###########################################
######################################################################################################

@app.route('/logout')
def logout():
    session['logged_out_time'] = current_date_time
    logged_users()
    session.clear()
    return redirect(url_for('login'))

######################################################################################################################
######################################################################################################################
###########################################  A D M I N  D A S H B O A R D  ###########################################
######################################################################################################################
######################################################################################################################

@app.route('/dashboard')
def admin():
    message = ''
    if 'accounts_id' in session and session['account_type'] == 'admin':
        # Establish database connection
        conn= get_db_connection()
        
        active_user = session.get('accounts_id', None)
        
        # Handle failed connection gracefully
        if conn is None:
            message = 'Database connection failed.'
            return redirect(url_for('dashboard'))
            
        #Fetch all users form the database
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT email, profile_pic FROM accounts WHERE accounts_id=%s AND accounts_id=%s', (active_user, active_user))
        user = cursor.fetchall()
        cursor.execute('SELECT CONCAT(firstName ," ",  lastName) as name, email, account_type FROM accounts WHERE account_type = "Buyer"')
        buyers = cursor.fetchall()
        cursor.execute('SELECT CONCAT(firstName ," ",  lastName) as name, email, account_type FROM accounts WHERE account_type = "Seller"')
        sellers = cursor.fetchall()
        cursor.execute('SELECT SUM(order_total) as orders FROM orders')
        order = cursor.fetchall()
        cursor.execute('SELECT SUM(admin_com) as commission FROM orders')
        admin_com = cursor.fetchall()
        cursor.close()
        conn.close()
        
        for profile in user:
            if profile['profile_pic']:
                profile['profile_pic'] = base64.b64encode(profile['profile_pic']).decode('utf-8')
        
        # Render the template with the users data
        return render_template('admin_dashboard.html', buyers = buyers, sellers = sellers, users = user, order=order, admin_com=admin_com)
    
    else:
        # If user is not a super admin, deny access
        message = 'You do not have permission to view this page!'
        return redirect(url_for('login'))

###############################################################################################################################
###############################################################################################################################
###########################################  A D M I N  U S E R  M A N A G E M E T  ###########################################
###############################################################################################################################
###############################################################################################################################

@app.route('/user_management')
def admin_user_management():
    messages = ''
    if 'accounts_id' in session and session['account_type'] == 'admin':
        # Establish database connection
        conn= get_db_connection()
        active_user = session.get('accounts_id', None)
        
        # Handle failed connection gracefully
        if conn is None:
            messages = 'Database connection failed.'
            return redirect(url_for('admin_user_management'))
            
        #Fetch all users form the database
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT email, profile_pic FROM accounts WHERE accounts_id=%s AND accounts_id=%s', (active_user, active_user))
        user = cursor.fetchall()
        cursor.execute('SELECT accounts_id, CONCAT(firstName ," ",  lastName) as name, email, account_type, status, documents, valid_id FROM accounts WHERE account_type = "Seller" OR account_type = "Buyer" OR account_type = "courier" ORDER BY status')
        accounts = cursor.fetchall()
        cursor.execute('SELECT accounts_id, CONCAT(firstName ," ",  lastName) as name, email, account_type, status FROM accounts WHERE account_type = "Seller" AND status = "1" OR account_type = "Buyer" AND status = "1" OR account_type = "courier" AND status = "1"')
        approved_accounts = cursor.fetchall()
        cursor.execute('SELECT accounts_id, CONCAT(firstName ," ",  lastName) as name, email, account_type, status FROM accounts WHERE account_type = "Seller" AND status = "3" OR account_type = "Buyer" AND status = "3" OR account_type = "courier" AND status = "3"')
        restricted_accounts = cursor.fetchall()
        cursor.close()
        conn.close()
        
        for documents in accounts:
            if documents['documents']:
                documents['documents'] = base64.b64encode(documents['documents']).decode('utf-8')
                
        for valid_id in accounts:
            if valid_id['valid_id']:
                valid_id['valid_id'] = base64.b64encode(valid_id['valid_id']).decode('utf-8')
                
        for profile in user:
            if profile['profile_pic']:
                profile['profile_pic'] = base64.b64encode(profile['profile_pic']).decode('utf-8')
        
        # Render the template with the users data
        return render_template('admin_user_management.html', accounts = accounts, approved_accounts = approved_accounts, restricted_accounts = restricted_accounts, users = user)
    
    else:
        # If user is not a super admin, deny access
        message = 'You do not have permission to view this page!'
        return redirect(url_for('login'))
    
##########################################################
###############   V A L I D  I D  V I E W  ###############
##########################################################

@app.route('/user_management/valid_id/<accounts_id>')
def valid_id_view(accounts_id):
    if 'accounts_id' in session and session['account_type'] == 'admin':
        # Establish database connection
        conn= get_db_connection()
        
        # Handle failed connection gracefully
        if conn is None:
            messages = 'Database connection failed.'
            return redirect(url_for('admin_user_management'))
        
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT valid_id FROM accounts WHERE accounts_id = %s and accounts_id = %s', (accounts_id, accounts_id))
    accounts = cursor.fetchall()
    
    for valid_id in accounts:
            if valid_id['valid_id']:
                valid_id['valid_id'] = base64.b64encode(valid_id['valid_id']).decode('utf-8')
        
    
    return render_template('admin_valid_id.html', accounts = accounts)

#############################################################
###############   D O C U M E N T S  V I E W  ###############
#############################################################

@app.route('/user_management/documents/<accounts_id>')
def documents_view(accounts_id):
    if 'accounts_id' in session and session['account_type'] == 'admin':
        # Establish database connection
        conn= get_db_connection()
        
        # Handle failed connection gracefully
        if conn is None:
            messages = 'Database connection failed.'
            return redirect(url_for('admin_user_management'))
        
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT documents FROM accounts WHERE accounts_id= %s and accounts_id= %s', (accounts_id, accounts_id))
    accounts = cursor.fetchall()
    
    for documents in accounts:
            if documents['documents']:
                documents['documents'] = base64.b64encode(documents['documents']).decode('utf-8')
        
    
    return render_template('admin_documents.html', accounts = accounts)

############################################################
###############  U S E R  A P P R O V A L S  ###############
############################################################

@app.route('/user_management/user_approve/<accounts_id>')
def admin_approval(accounts_id):
    messages = ''
    if 'accounts_id' in session and session['account_type'] == 'admin':
        
        subject = 'ACCOUNT APPROVED'
        email_message = 'Congratulations!! Your account is now approved and you may now login at FOODITY!!!'
        # Establish database connection
        conn= get_db_connection()
        
        
        
        # Handle failed connection gracefully
        if conn is None:
            messages = 'Database connection failed.'
            return redirect(url_for('admin_user_management'))
        
        #Fetch all users form the database
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM accounts WHERE accounts_id =%s AND accounts_id =%s;', (accounts_id, accounts_id))
        user = cursor.fetchone()
        cursor.execute('UPDATE accounts SET status = 1 WHERE accounts_id=%s AND accounts_id=%s', (accounts_id, accounts_id))
        conn.commit()
        
        msg = Message(
            subject=subject,
            recipients=[user['email']],
            body=email_message)

            # Send the email
        try:
            mail.send(msg)
            cursor.close()
            conn.close()
        except Exception as e:
            message = 'failed'
            cursor.close()
            conn.close()
        return redirect(url_for('admin_user_management'))
        
        
    return redirect(url_for('admin_user_management'))

##############################################################
###############  U S E R  D I S A P P R O V E  ###############
##############################################################

@app.route('/user_management/user_disapprove/<accounts_id>')
def admin_disapprove(accounts_id):
    messages = ''
    if 'accounts_id' in session and session['account_type'] == 'admin':
        
        subject = 'ACCOUNT DISAPPROVED'
        email_message = 'Sorry your account is disapproved for failing the verification process you may email us your documents at foodity2024@gmail.com'
        # Establish database connection
        conn= get_db_connection()
        
        # Handle failed connection gracefully
        if conn is None:
            messages = 'Database connection failed.'
            return redirect(url_for('admin_user_management'))
            
        #Fetch all users form the database
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM accounts WHERE accounts_id =%s AND accounts_id =%s;', (accounts_id, accounts_id))
        user = cursor.fetchone()
        cursor.execute('UPDATE accounts SET status = 2 WHERE accounts_id=%s AND accounts_id=%s', (accounts_id, accounts_id))
        conn.commit()
        
        msg = Message(
            subject=subject,
            recipients=[user['email']],
            body=email_message)

            # Send the email
        try:
            mail.send(msg)
            cursor.close()
            conn.close()
        except Exception as e:
            message = 'failed'
            cursor.close()
            conn.close()
            return redirect(url_for('admin_user_management'))
        
    return redirect(url_for('admin_user_management'))

##########################################################
###############  U S E R  R E S T R I C T  ###############
##########################################################

@app.route('/user_management/user_restrict/<accounts_id>')
def admin_restrict(accounts_id):
    messages = ''
    if 'accounts_id' in session and session['account_type'] == 'admin':
        # Establish database connection
        conn= get_db_connection()
        
        # Handle failed connection gracefully
        if conn is None:
            messages = 'Database connection failed.'
            return redirect(url_for('admin_user_management'))
            
        #Fetch all users form the database
        cursor = conn.cursor(dictionary=True)
        cursor.execute('UPDATE accounts SET status = 3 WHERE accounts_id=%s AND accounts_id=%s', (accounts_id, accounts_id))
        conn.commit()
        cursor.close()
        conn.close()
        
    return redirect(url_for('admin_user_management'))

########################################################
###############  F I L T E R  B U Y E R  ###############
########################################################

@app.route('/user_management/filter_buyer')
def user_management_filter_buyer():
    message = ''
    if 'accounts_id' in session and session['account_type'] == 'admin':
        # Establish database connection
        conn= get_db_connection()
        
        # Handle failed connection gracefully
        if conn is None:
            message = 'Database connection failed.'
            return redirect(url_for('dashboard'))
            
        #Fetch all users form the database
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT CONCAT(firstName ," ",  lastName) as name, email, account_type, status, documents, valid_id FROM accounts WHERE account_type = "buyer"')
        filtered_buyers = cursor.fetchall()
        cursor.execute('SELECT CONCAT(firstName ," ",  lastName) as name, email, account_type, status FROM accounts WHERE account_type = "Buyer" AND status = 1')
        approved_accounts_buyers = cursor.fetchall()
        cursor.execute('SELECT CONCAT(firstName ," ",  lastName) as name, email, account_type, status FROM accounts WHERE account_type = "Buyer" AND status = 3')
        restricted_accounts_buyers = cursor.fetchall()
        cursor.close()
        conn.close()
        
        for documents in filtered_buyers:
            if documents['documents']:
                documents['documents'] = base64.b64encode(documents['documents']).decode('utf-8')
                
        for valid_id in filtered_buyers:
            if valid_id['valid_id']:
                valid_id['valid_id'] = base64.b64encode(valid_id['valid_id']).decode('utf-8')
        
        # Render the template with the users data
        return render_template('admin_user_management.html', accounts = filtered_buyers, approved_accounts = approved_accounts_buyers, restricted_accounts = restricted_accounts_buyers)
    
    else:
        # If user is not a super admin, deny access
        message = 'You do not have permission to view this page!'
        return redirect(url_for('login'))

##########################################################
###############  F I L T E R  S E L L E R  ###############
##########################################################

@app.route('/user_management/filter_seller')
def user_management_filter_seller():
    message = ''
    if 'accounts_id' in session and session['account_type'] == 'admin':
        # Establish database connection
        conn= get_db_connection()
        
        # Handle failed connection gracefully
        if conn is None:
            message = 'Database connection failed.'
            return redirect(url_for('dashboard'))
            
        #Fetch all users form the database
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT CONCAT(firstName ," ",  lastName) as name, email, account_type, status, documents, valid_id FROM accounts WHERE account_type = "seller"')
        filtered_sellers = cursor.fetchall()
        cursor.execute('SELECT CONCAT(firstName ," ",  lastName) as name, email, account_type, status FROM accounts WHERE account_type = "seller" AND status = 1')
        approved_accounts_buyers = cursor.fetchall()
        cursor.execute('SELECT CONCAT(firstName ," ",  lastName) as name, email, account_type, status FROM accounts WHERE account_type = "seller" AND status = 3')
        restricted_accounts_buyers = cursor.fetchall()
        cursor.close()
        conn.close()
        
        for documents in filtered_sellers:
            if documents['documents']:
                documents['documents'] = base64.b64encode(documents['documents']).decode('utf-8')
                
        for valid_id in filtered_sellers:
            if valid_id['valid_id']:
                valid_id['valid_id'] = base64.b64encode(valid_id['valid_id']).decode('utf-8')
        
        # Render the template with the users data
        return render_template('admin_user_management.html', accounts = filtered_sellers, approved_accounts = approved_accounts_buyers, restricted_accounts = restricted_accounts_buyers)
    
    else:
        # If user is not a super admin, deny access
        message = 'You do not have permission to view this page!'
        return redirect(url_for('login'))

#####################################################################################################################
#####################################################################################################################
###########################################  A D M I N  U S E R  L O G S  ###########################################
#####################################################################################################################
#####################################################################################################################

@app.route('/user_logs')
def admin_user_logs():
    messages = ''
    if 'accounts_id' in session and session['account_type'] == 'admin':
        # Establish database connection
        conn= get_db_connection()
        
        active_user = session.get('accounts_id', None)
        
        # Handle failed connection gracefully
        if conn is None:
            messages = 'Database connection failed.'
            return redirect(url_for('admin_user_logs'))
            
        #Fetch all users form the database
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT email, profile_pic FROM accounts WHERE accounts_id=%s AND accounts_id=%s', (active_user, active_user))
        user = cursor.fetchall()
        cursor.execute('SELECT CONCAT(firstName ," ",  lastName) as name, email, acc_type, logged_in, logged_out FROM user_logs WHERE acc_type = "Seller" OR acc_type = "Buyer" ORDER BY logged_in')
        accounts = cursor.fetchall()
        cursor.close()
        conn.close()
        
        for profile in user:
            if profile['profile_pic']:
                profile['profile_pic'] = base64.b64encode(profile['profile_pic']).decode('utf-8')
        
        # Render the template with the users data
        return render_template('admin_user_logs.html', accounts = accounts, users = user)
    
    else:
        # If user is not a super admin, deny access
        message = 'You do not have permission to view this page!'
        return redirect(url_for('login'))

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


######################################################################################################################
######################################################################################################################
###########################################  A D M I N  F E E D B A C K S  ###########################################
######################################################################################################################
######################################################################################################################

@app.route('/feedbacks')
def feedbacks():
    messages = ''
    if 'accounts_id' in session and session['account_type'] == 'admin':
        # Establish database connection
        conn= get_db_connection()
        
        active_user = session.get('accounts_id', None)
        
        # Handle failed connection gracefully
        if conn is None:
            messages = 'Database connection failed.'
            return redirect(url_for('feedbacks'))
            
        #Fetch all users form the database
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT email, profile_pic FROM accounts WHERE accounts_id=%s AND accounts_id=%s', (active_user, active_user))
        user = cursor.fetchall()
        cursor.execute('SELECT CONCAT(firstName ," ",  lastName) as name, email, account_type FROM accounts WHERE account_type = "Seller" OR account_type = "Buyer"')
        accounts = cursor.fetchall()
        cursor.close()
        conn.close()
        
        for profile in user:
            if profile['profile_pic']:
                profile['profile_pic'] = base64.b64encode(profile['profile_pic']).decode('utf-8')
        
        # Render the template with the users data
        return render_template('admin_feedback.html', accounts = accounts, users = user)
    
    else:
        # If user is not a super admin, deny access
        message = 'You do not have permission to view this page!'
        return redirect(url_for('login'))

####################################################################################################################
####################################################################################################################
###########################################  A D M I N  S E T T I N G S  ###########################################
####################################################################################################################
####################################################################################################################

@app.route('/admin_settings')
def admin_settings():
    message_setting = ''
    if 'accounts_id' in session and session['account_type'] == 'admin':
        # Establish database connection
        conn= get_db_connection()
        
        # Handle failed connection gracefully
        if conn is None:
            messages = 'Database connection failed.'
            return redirect(url_for('admin_settings'))
    return render_template('admin_settings.html')

###########################################################################################################################
###########################################################################################################################
###########################################  A D M I N  S A L E S  R E P O R T  ###########################################
###########################################################################################################################
###########################################################################################################################

@app.route('/admin_sales_report')
def admin_sales_report():
    message = ''
    if 'accounts_id' in session and session['account_type'] == 'admin':
        # Establish database connection
        conn= get_db_connection()
        
        active_user = session.get('accounts_id', None)
        
        # Handle failed connection gracefully
        if conn is None:
            message = 'Database connection failed.'
            return redirect(url_for('admin_sales_report'))
            
        #Fetch all users form the database
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT firstName, lastName, email, password, profile_pic FROM accounts WHERE accounts_id=%s AND accounts_id=%s', (active_user, active_user))
        user = cursor.fetchall()
        cursor.execute('SELECT * FROM sales_report')
        report = cursor.fetchall()
        cursor.close()
        conn.close()
        
        for profile in user:
            if profile['profile_pic']:
                profile['profile_pic'] = base64.b64encode(profile['profile_pic']).decode('utf-8')
        
        # Render the template with the users data
        return render_template('admin_sales_report.html', users = user, report=report)
    
    else:
        # If user is not a super admin, deny access
        message = 'You do not have permission to view this page!'
        return redirect(url_for('login'))

###########################################################################################################################
###########################################################################################################################
###########################################  A D M I N  E D I T  P R O F I L E  ###########################################
###########################################################################################################################
###########################################################################################################################

@app.route('/admin_edit_profile')
def edit_profile():
    message = ''
    if 'accounts_id' in session and session['account_type'] == 'admin':
        # Establish database connection
        conn= get_db_connection()
        
        active_user = session.get('accounts_id', None)
        
        # Handle failed connection gracefully
        if conn is None:
            message = 'Database connection failed.'
            return redirect(url_for('edit_profile'))
            
        #Fetch all users form the database
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT firstName, lastName, email, password, profile_pic FROM accounts WHERE accounts_id=%s AND accounts_id=%s', (active_user, active_user))
        user = cursor.fetchall()
        cursor.close()
        conn.close()
        
        for profile in user:
            if profile['profile_pic']:
                profile['profile_pic'] = base64.b64encode(profile['profile_pic']).decode('utf-8')
        
        # Render the template with the users data
        return render_template('admin_edit_profile.html', users = user)
    
    else:
        # If user is not a super admin, deny access
        message = 'You do not have permission to view this page!'
        return redirect(url_for('login'))
    
########################################################
###############  S A V E  P R O F I L E  ###############
########################################################

@app.route('/admin_edit_profile/save', methods=['GET', 'POST'])
def save_profile():
    message = ''
    if 'accounts_id' in session and session['account_type'] == 'admin':
        if request.method == 'POST':
            firstName = request.form['first_name']
            lastName = request.form['last_name']
            password = request.form['pass']
            confirm_pass = request.form['confirm_pass']
            profile_picture = request.files['profile_pics']
            active_user = session.get('accounts_id', None)
            # Establish database connection
            conn= get_db_connection()
            
            active_user = session.get('accounts_id', None)
            
            # Handle failed connection gracefully
            if conn is None:
                message = 'Database connection failed.'
                return redirect(url_for('edit_profile'))
            
            if password == confirm_pass:
                #Fetch all users form the database
                cursor = conn.cursor(dictionary=True)
                cursor.execute('UPDATE accounts SET firstName = %s, lastName = %s, password = %s, profile_pic = %s WHERE accounts_id=%s;', (firstName, lastName, password, profile_picture.read(),active_user))
                conn.commit()
                cursor.close()
                conn.close()
                return redirect(url_for('edit_profile'))
            else:
                message = 'Password does not match!'
                return render_template('admin_edit_profile.html', message = message)
    else:
        # If user is not a super admin, deny access
        message = 'You do not have permission to view this page!'
        return redirect(url_for('login'))

########################################################################################################################
########################################################################################################################
###########################################  S E L L E R  D A S H B O A R D  ###########################################
########################################################################################################################
########################################################################################################################

@app.route('/seller_dashboard')
def seller_dashboard():
    message = ''
    if 'accounts_id' in session and session['account_type'] == 'seller':
        # Establish database connection
        conn= get_db_connection()
        
        active_user = session.get('accounts_id', None)
        active_email = session.get('email', None)
        delivered = 2
        cancelled = 3
        
        # Handle failed connection gracefully
        if conn is None:
            message = 'Database connection failed.'
            return redirect(url_for('seller_dashboard'))
            
        #Fetch all users form the database
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT email, profile_pic, barangay, city, province, zip_code FROM accounts WHERE accounts_id=%s AND accounts_id=%s', (active_user, active_user))
        user = cursor.fetchall()
        cursor.execute('SELECT * FROM orders WHERE uploader=%s AND uploader=%s', (active_email, active_email))
        uploaders = cursor.fetchall()
        cursor.execute('SELECT COUNT(*) as total FROM orders WHERE uploader=%s AND uploader=%s', (active_email, active_email))
        totalOrders = cursor.fetchall()
        cursor.execute('SELECT COUNT(order_status) as delivered FROM orders WHERE order_status=%s AND uploader=%s', (delivered, active_email))
        deliver = cursor.fetchall()
        cursor.execute('SELECT COUNT(order_status) as cancelled FROM orders WHERE order_status=%s AND order_status=%s', (cancelled, cancelled))
        cancel = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        for profile in user:
            if profile['profile_pic']:
                profile['profile_pic'] = base64.b64encode(profile['profile_pic']).decode('utf-8')
        
        # Render the template with the users data
        return render_template('seller_dashboard.html', users=user, uploaders=uploaders, totalOrders=totalOrders, deliver=deliver, cancel=cancel)
    
    else:
        # If user is not a super admin, deny access
        message = 'You do not have permission to view this page!'
        return redirect(url_for('login'))

##################################################################################################################
##################################################################################################################
###########################################  S E L L E R  O R D E R S  ###########################################
##################################################################################################################
##################################################################################################################

@app.route('/seller_orders')
def seller_orders():
    message = ''
    if 'accounts_id' in session and session['account_type'] == 'seller':
        # Establish database connection
        conn= get_db_connection()
        
        active_user = session.get('accounts_id', None)
        active_email = session.get('email', None)
        
        # Handle failed connection gracefully
        if conn is None:
            message = 'Database connection failed.'
            return redirect(url_for('seller_orders'))
            
        #Fetch all users form the database
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT email, profile_pic, barangay, city, province, zip_code FROM accounts WHERE accounts_id=%s AND accounts_id=%s', (active_user, active_user))
        user = cursor.fetchall()
        cursor.execute('SELECT * FROM orders WHERE uploader=%s AND uploader=%s ORDER BY order_status, payment_status ASC', (active_email, active_email))
        uploaders = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        for profile in user:
            if profile['profile_pic']:
                profile['profile_pic'] = base64.b64encode(profile['profile_pic']).decode('utf-8')
        
        # Render the template with the users data
        return render_template('seller_orders.html', users=user, uploaders=uploaders)
    
    else:
        # If user is not a super admin, deny access
        message = 'You do not have permission to view this page!'
        return redirect(url_for('login'))
    
######################################################################################################################
######################################################################################################################
###########################################  S E L L E R  P R O D U C T S  ###########################################
######################################################################################################################
######################################################################################################################

@app.route('/seller_products')
def seller_products():
    message = ''
    if 'accounts_id' in session and session['account_type'] == 'seller':
        # Establish database connection
        conn= get_db_connection()
        
        active_email = session.get('email', None)
        active_user = session.get('accounts_id', None)
        # Handle failed connection gracefully
        if conn is None:
            message = 'Database connection failed.'
            return redirect(url_for('seller_products'))
        #Fetch all products form the database
        
        # The above code is creating a cursor object for executing SQL queries on a database
        # connection `conn` with the option `dictionary=True`, which specifies that the cursor should
        # return each row as a dictionary where the keys are the column names. This allows you to
        # access the query results using column names instead of numerical indices.
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT product_id, product_name, product_description, product_price, product_photo1, product_categories, product_variants FROM products WHERE uploader=%s AND uploader=%s', (active_email, active_email))
        all_products = cursor.fetchall()
        cursor.execute('SELECT firstName, lastName, email, password, profile_pic FROM accounts WHERE accounts_id=%s AND accounts_id=%s', (active_user, active_user))
        user = cursor.fetchall()
        cursor.execute('SELECT product_id, product_name, product_description, product_price ,product_stocks , product_photo1, product_photo2, product_photo3, product_photo4, product_categories, product_variants FROM products WHERE uploader=%s AND uploader=%s', (active_email, active_email))
        edit_product = cursor.fetchall()
        
        
        cursor.close()
        conn.close()
        
        for products in all_products:
            if products['product_photo1']:
                products['product_photo1'] = base64.b64encode(products['product_photo1']).decode('utf-8')
        
        for profile in user:
                    if profile['profile_pic']:
                        profile['profile_pic'] = base64.b64encode(profile['profile_pic']).decode('utf-8')
        
        
        # Render the template with the users data
        return render_template('seller_products.html', edit_product = edit_product, products = all_products, message = message, users = user)
    
    else:
        # If user is not a super admin, deny access
        message = 'You do not have permission to view this page!'
        return redirect(url_for('login'))
    
########################################################
###############  A D D  P R O D U C T S  ###############
########################################################

@app.route('/seller_products/add_product', methods=['GET', 'POST'])
def add_products():
    message = ''
    if 'accounts_id' in session and session['account_type'] == 'seller':
        
        if request.method == 'POST':
            product_name = request.form['productName']
            product_description = request.form['product_description']
            product_price = request.form['productPrice']
            product_stocks = request.form['productStocks']
            product_photo1 = request.files['productImage1']
            product_photo2 = request.files['productImage2']
            product_photo3 = request.files['productImage3']
            product_photo4 = request.files['productImage4']
            product_category = request.form['product_categories_dropdown']
            product_variant = request.form['variant']
            
            # Establish database connection
            conn= get_db_connection()
            active_user = session.get('accounts_id', None)
            active_email = session.get('email', None)
            
            # Handle failed connection gracefully
            if conn is None:
                message = 'Database connection failed.'
                return redirect(url_for('add_products'))
            
            cursor = conn.cursor(dictionary=True)
            cursor.execute('SELECT firstName, lastName, email, password, profile_pic FROM accounts WHERE accounts_id=%s AND accounts_id=%s', (active_user, active_user))
            user = cursor.fetchall()
            cursor.execute('SELECT * FROM products WHERE product_name=%s AND product_categories=%s AND uploader=%s;', (product_name, product_category, active_email))
            product_duplicate = cursor.fetchone()
            
            if product_duplicate is not None:
                message = "Product Already Exists"
                cursor = conn.cursor(dictionary=True)
                cursor.execute('SELECT product_id, product_name, product_description, product_price ,product_stocks , product_photo1, product_categories, product_variants FROM products WHERE uploader=%s AND uploader=%s', (active_email, active_email))
                all_products = cursor.fetchall()
                cursor.close()
                conn.close()
                
                for products in all_products:
                    if products['product_photo1']:
                        products['product_photo1'] = base64.b64encode(products['product_photo1']).decode('utf-8')
                        
                for profile in user:
                    if profile['profile_pic']:
                        profile['profile_pic'] = base64.b64encode(profile['profile_pic']).decode('utf-8')
                
                return render_template('seller_products.html', products = all_products, message = message)
            else:
            # sql database query
                sql = "INSERT INTO products (product_name, product_description, product_price, product_stocks, product_photo1, product_photo2, product_photo3, product_photo4, product_categories, product_variants, uploader) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
                values = (product_name, product_description, product_price, product_stocks, product_photo1.read(), product_photo2.read(), product_photo3.read(), product_photo4.read(), product_category, product_variant, active_email)
                cursor.execute(sql, values)
                conn.commit()  # Save changes to the database
                cursor.close()
                conn.close()
            
            
            
        
    return redirect(url_for('seller_products'))


##########################################################
###############  E D I T  P R O D U C T S  ###############
##########################################################

@app.route('/seller_products/edit_product/<product_id>')
def edit_product(product_id):
    message = ''
    if 'accounts_id' in session and session['account_type'] == 'seller':
        
        session['edit_product_id'] = product_id
        # Establish database connection
        conn= get_db_connection()
        active_user = session.get('accounts_id', None)
        active_email = session.get('email', None)
        
        # Handle failed connection gracefully
        if conn is None:
            message = 'Database connection failed.'
            return redirect(url_for('add_products'))
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT firstName, lastName, email, password, profile_pic FROM accounts WHERE accounts_id=%s AND accounts_id=%s', (active_user, active_user))
        user = cursor.fetchall()
        cursor.execute('SELECT * FROM products WHERE uploader=%s AND product_id=%s', (active_email, product_id))
        edit_product = cursor.fetchall()
        cursor.close()
        conn.close()
        
        for products in edit_product:
            if products['product_photo1']:
                products['product_photo1'] = base64.b64encode(products['product_photo1']).decode('utf-8')
                
        for products in edit_product:
            if products['product_photo2']:
                products['product_photo2'] = base64.b64encode(products['product_photo2']).decode('utf-8')
                
        for products in edit_product:
            if products['product_photo3']:
                products['product_photo3'] = base64.b64encode(products['product_photo3']).decode('utf-8')
                
        for products in edit_product:
            if products['product_photo4']:
                products['product_photo4'] = base64.b64encode(products['product_photo4']).decode('utf-8')
                
        for profile in user:
            if profile['profile_pic']:
                profile['profile_pic'] = base64.b64encode(profile['profile_pic']).decode('utf-8')
        
        return render_template('seller_products_update.html', edit_product = edit_product, users = user)
    

###################################################################
###############  S A V E  E D I T  P R O D U C T S  ###############
###################################################################

@app.route('/seller_products/save_edit_product')
def save_edit_product():
    message = ''
    if 'accounts_id' in session and session['account_type'] == 'seller':
        
        if request.method == 'POST':
            product_name = request.form['productName']
            product_description = request.form['product_description']
            product_price = request.form['productPrice']
            product_stocks = request.form['productStocks']
            product_photo1 = request.files['productImage1']
            product_photo2 = request.files['productImage2']
            product_photo3 = request.files['productImage3']
            product_photo4 = request.files['productImage4']
            product_category = request.form['product_categories_dropdown']
            product_variant = request.form['variant']
            
            # Establish database connection
            conn= get_db_connection()
            active_user = session.get('accounts_id', None)
            active_email = session.get('email', None)
            product_id = session.get('edit_product_id', None)
            
            # Handle failed connection gracefully
            if conn is None:
                message = 'Database connection failed.'
                return redirect(url_for('seller_products'))
            
            cursor = conn.cursor(dictionary=True)
            cursor.execute('UPDATE products SET product_name = %s, product_description = %s, product_price = %s, product_stocks = %s, product_photo1 = %s, product_photo2 = %s, product_photo3 = %s, product_photo4 = %s, product_category = %s, product_variant = %s  WHERE product_id=%s AND uploader=%s', (product_name, product_description, product_price, product_stocks, product_photo1, product_photo2, product_photo3,product_photo4, product_category, product_variant,product_id, active_email))
            conn.commit()  # Save changes to the database
            cursor.close()
            conn.close()
            return render_template('seller_products_update.html')
        return redirect(url_for('seller_products'))

################################################################
###############  A R C H I V E  P R O D U C T S  ###############
################################################################

@app.route('/seller_products/archive_product/<product_id>')
def archive_products(product_id):
    if 'accounts_id' in session and session['account_type'] == 'seller':
        
        # Establish database connection
        conn= get_db_connection()
        
        # Handle failed connection gracefully
        if conn is None:
            messages = 'Database connection failed.'
            return redirect(url_for('seller_products'))
            
        #Fetch all users form the database
        cursor = conn.cursor(dictionary=True)
        cursor.execute('DELETE FROM products WHERE product_id=%s AND product_id=%s', (product_id, product_id))
        conn.commit()
        cursor.close()
        conn.close()
        
    return redirect(url_for('seller_products'))

################################################################################################################
################################################################################################################
###########################################  S E L L E R  S A L E S  ###########################################
################################################################################################################
################################################################################################################

@app.route('/seller_sales')
def seller_sales():
    message = ''
    if 'accounts_id' in session and session['account_type'] == 'seller':
        # Establish database connection
        conn= get_db_connection()
        
        active_user = session.get('accounts_id', None)
        active_email = session.get('email', None)
        
        # Handle failed connection gracefully
        if conn is None:
            message = 'Database connection failed.'
            return redirect(url_for('seller_sales'))
            
        #Fetch all users form the database
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT email, profile_pic, barangay, city, province, zip_code FROM accounts WHERE accounts_id=%s AND accounts_id=%s', (active_user, active_user))
        user = cursor.fetchall()
        cursor.execute('SELECT * FROM sales_report WHERE uploader=%s AND uploader=%s', (active_email, active_email))
        report = cursor.fetchall()


        
        
        for profile in user:
            if profile['profile_pic']:
                profile['profile_pic'] = base64.b64encode(profile['profile_pic']).decode('utf-8')
        
        cursor.close()
        conn.close()
        
        # Render the template with the users data
        return render_template('seller_sales.html', users = user, report=report)
    
    else:
        # If user is not a super admin, deny access
        message = 'You do not have permission to view this page!'
        return redirect(url_for('login'))
    
######################################################################################################################
######################################################################################################################
###########################################  S E L L E R  D E L I V E R Y  ###########################################
######################################################################################################################
######################################################################################################################

@app.route('/seller_delivery')
def seller_delivery():
    message = ''
    if 'accounts_id' in session and session['account_type'] == 'seller':
        # Establish database connection
        conn= get_db_connection()
        
        active_user = session.get('accounts_id', None)
        active_email = session.get('email', None)
        
        # Handle failed connection gracefully
        if conn is None:
            message = 'Database connection failed.'
            return redirect(url_for('seller_delivery'))
            
        #Fetch all users form the database
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT email, profile_pic, barangay, city, province, zip_code FROM accounts WHERE accounts_id=%s AND accounts_id=%s', (active_user, active_user))
        user = cursor.fetchall()
        cursor.execute('SELECT * FROM orders WHERE uploader=%s AND uploader=%s ORDER BY order_status, payment_status ASC', (active_email, active_email))
        uploader = cursor.fetchall()
        
        
        conn.close()
        
        for profile in user:
            if profile['profile_pic']:
                profile['profile_pic'] = base64.b64encode(profile['profile_pic']).decode('utf-8')
        
        # Render the template with the users data
        return render_template('seller_delivery.html', users=user, uploader=uploader)
    
    else:
        # If user is not a super admin, deny access
        message = 'You do not have permission to view this page!'
        return redirect(url_for('login'))


#########################################
###############  S H I P  ###############
#########################################

@app.route('/seller_delivery/ship/<order_id>')
def ship(order_id):
    message = ''
    if 'accounts_id' in session and session['account_type'] == 'seller':
        # Establish database connection
        conn= get_db_connection()
        
        active_user = session.get('accounts_id', None)
        active_email = session.get('email', None)
        
        # Handle failed connection gracefully
        if conn is None:
            message = 'Database connection failed.'
            return redirect(url_for('seller_delivery'))
            
        #Fetch all users form the database
        cursor = conn.cursor(dictionary=True)
        cursor.execute('UPDATE orders SET order_status = 1 WHERE order_id=%s AND order_id=%s', (order_id, order_id))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        # Render the template with the users data
        return redirect(url_for('seller_delivery'))
    
    else:
        # If user is not a super admin, deny access
        message = 'You do not have permission to view this page!'
        return redirect(url_for('login'))


###############################################
###############  D E L I V E R  ###############
###############################################

@app.route('/seller_delivery/deliver/<order_id>')
def deliver(order_id):
    message = ''
    if 'accounts_id' in session and session['account_type'] == 'seller':
        # Establish database connection
        conn= get_db_connection()
        
        active_user = session.get('accounts_id', None)
        
        # Handle failed connection gracefully
        if conn is None:
            message = 'Database connection failed.'
            return redirect(url_for('seller_delivery'))
            
        #Fetch all users form the database
        cursor = conn.cursor(dictionary=True)
        cursor.execute('UPDATE orders SET order_status = 2 WHERE order_id=%s AND order_id=%s', (order_id, order_id))
        conn.commit()
        cursor.execute('SELECT * FROM orders WHERE order_id=%s AND order_id=%s ORDER BY order_status, payment_status ASC', (order_id, order_id))
        sales_report = cursor.fetchone()

        session['order_name'] = sales_report['product']
        session['name_of_buyer'] = sales_report['buyer_name']
        session['active_email'] = sales_report['buyer_email']
        session['buyer_loc'] = sales_report['buyer_location']
        session['date_time'] = sales_report['order_date']
        session['payment_type'] = sales_report['payment_method']
        session['order_price'] = sales_report['order_price']
        session['order_total'] = sales_report['order_total']
        session['count_of_order'] = sales_report['order_quantity']
        session['order_status'] = sales_report['order_status']
        session['payment_status'] = sales_report['payment_status']
        session['uploader_email'] = sales_report['uploader']
        session['admin_com'] = sales_report['admin_com']

        order_name = session.get('order_name', None)
        name_of_buyer = session.get('name_of_buyer', None)
        active_email = session.get('active_email', None)
        buyer_loc = session.get('buyer_loc', None)
        admin_com = session.get('admin_com', None)
        date_time = session.get('date_time', None)
        payment_type = session.get('payment_type', None)
        order_price = session.get('order_price', None)
        order_total = session.get('order_total', None)
        count_of_order = session.get('count_of_order', None)
        order_status = session.get('order_status', None)
        payment_status = session.get('payment_status', None)
        uploader_email = session.get('uploader_email', None)

        sql = "INSERT INTO sales_report (product ,buyer_name, buyer_email, buyer_location, order_date, payment_method, order_price, order_total, order_quantity, order_status, payment_status, uploader, admin_com) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
        values = (order_name ,name_of_buyer, active_email, buyer_loc, date_time, payment_type, order_price, order_total, count_of_order, order_status, payment_status, uploader_email, admin_com)
        cursor.execute(sql, values)
        conn.commit()
        
        cursor.close()
        conn.close()

        session.pop('order_name', None)
        session.pop('name_of_buyer', None)
        session.pop('active_email', None)
        session.pop('buyer_loc', None)
        session.pop('admin_com', None)
        session.pop('date_time', None)
        session.pop('payment_type', None)
        session.pop('order_price', None)
        session.pop('order_total', None)
        session.pop('count_of_order', None)
        session.pop('order_status', None)
        session.pop('payment_status', None)
        session.pop('uploader_email', None)
        
        # Render the template with the users data
        return redirect(url_for('seller_delivery'))
    
    else:
        # If user is not a super admin, deny access
        message = 'You do not have permission to view this page!'
        return redirect(url_for('login'))

######################################################################################################################
######################################################################################################################
###########################################  S E L L E R  M E S S A G E  #############################################
######################################################################################################################
######################################################################################################################

@app.route('/seller_message')
def seller_message():
    message = ''
    if 'accounts_id' in session and session['account_type'] == 'seller':
        # Establish database connection
        conn= get_db_connection()
        
        # Handle failed connection gracefully
        if conn is None:
            message = 'Database connection failed.'
            return redirect(url_for('seller_message'))
            
        #Fetch all users form the database
        
        # Render the template with the users data
        return render_template('seller_message.html')
    
    else:
        # If user is not a super admin, deny access
        message = 'You do not have permission to view this page!'
        return redirect(url_for('login'))
    
#############################################################################################################################
#############################################################################################################################
###########################################  S E L L E R  E D I T  P R O F I L E  ###########################################
#############################################################################################################################
#############################################################################################################################

@app.route('/seller_edit_profile')
def seller_edit_profile():
    message = ''
    if 'accounts_id' in session and session['account_type'] == 'seller':
        # Establish database connection
        conn= get_db_connection()
        
        active_user = session.get('accounts_id', None)
        
        # Handle failed connection gracefully
        if conn is None:
            message = 'Database connection failed.'
            return redirect(url_for('seller_edit_profile'))
            
        #Fetch all users form the database
        cursor = conn.cursor(dictionary=True, buffered=True)
        cursor.execute('SELECT firstName, lastName, email, password, profile_pic FROM accounts WHERE accounts_id=%s AND accounts_id=%s', (active_user, active_user))
        user = cursor.fetchall()
        cursor.close()
        conn.close()
        
        for profile in user:
            if profile['profile_pic']:
                profile['profile_pic'] = base64.b64encode(profile['profile_pic']).decode('utf-8')
        
        # Render the template with the users data
        return render_template('seller_edit_profile.html', users = user)
    
    else:
        # If user is not a super admin, deny access
        message = 'You do not have permission to view this page!'
        return redirect(url_for('login'))
    
########################################################
###############  S A V E  P R O F I L E  ###############
########################################################

@app.route('/seller_edit_profile/save', methods=['GET', 'POST'])
def seller_save_profile():
    message = ''
    if 'accounts_id' in session and session['account_type'] == 'seller':
        if request.method == 'POST':
            firstName = request.form['first_name']
            lastName = request.form['last_name']
            password = request.form['pass']
            confirm_pass = request.form['confirm_pass']
            profile_picture = request.files['profile_pics']
            
            active_user = session.get('accounts_id', None)
            # Establish database connection
            conn= get_db_connection()
            
            active_user = session.get('accounts_id', None)
            
            # Handle failed connection gracefully
            if conn is None:
                message = 'Database connection failed.'
                return redirect(url_for('seller_save_profile'))
            
            if password == confirm_pass:
                #Fetch all users form the database
                cursor = conn.cursor(dictionary=True)
                cursor.execute('UPDATE accounts SET firstName = %s, lastName = %s, password = %s, profile_pic = %s WHERE accounts_id=%s;', (firstName, lastName, password, profile_picture.read(),active_user))
                conn.commit()
                cursor.close()
                conn.close()
                return redirect(url_for('seller_edit_profile'))
            else:
                message = 'Password does not match!'
                return render_template('seller_edit_profile.html', message = message)
    else:
        # If user is not a super admin, deny access
        message = 'You do not have permission to view this page!'
        return redirect(url_for('login'))

############################################################################################################
############################################################################################################
###########################################  B U Y E R  H O M E  ###########################################
############################################################################################################
############################################################################################################

@app.route('/buyer_home')
def buyer_home():
    message = ''
    if 'accounts_id' in session and session['account_type'] == 'buyer':
        
        active_user = session.get('accounts_id', None)
        active_email = session.get('email', None)
        
        conn= get_db_connection()
        
        # Handle failed connection gracefully
        if conn is None:
            message = 'Database connection failed.'
            return redirect(url_for('buyer_home'))
        
        #Fetch all users form the database
        cursor = conn.cursor(dictionary=True, buffered=True)
        
        
        
        cursor.execute('SELECT email, profile_pic, barangay, city, province, zip_code FROM accounts WHERE accounts_id=%s AND accounts_id=%s', (active_user, active_user))
        user = cursor.fetchall()
        cursor.execute('SELECT product_id, product_name, product_description, product_price, product_photo1, product_categories, product_variants FROM products')
        all_products = cursor.fetchall()
        cursor.execute('SELECT product_id ,product_name, product_photo1, order_price, order_quantity, order_price * order_quantity as total_price_item FROM my_orders WHERE buyer = %s AND buyer = %s;', (active_email, active_email))
        order_display = cursor.fetchall()
        cursor.execute('SELECT SUM(item_total_amount) as subTotal, SUM(item_total_amount) + MAX(delivery_fee)  as total, MAX(delivery_fee) as delivery FROM my_orders WHERE buyer = %s AND buyer = %s GROUP BY product_name;', (active_email, active_email))
        order_total_value = cursor.fetchall()
        cursor.execute('SELECT product_id, product_name, product_description, product_price, product_photo1, product_categories, product_variants FROM products WHERE product_categories = 1')
        fnv = cursor.fetchall()
        cursor.execute('SELECT product_id, product_name, product_description, product_price, product_photo1, product_categories, product_variants FROM products WHERE product_categories = 2')
        confectionery = cursor.fetchall()
        cursor.execute('SELECT product_id, product_name, product_description, product_price, product_photo1, product_categories, product_variants FROM products WHERE product_categories = 3')
        cereals = cursor.fetchall()
        cursor.execute('SELECT product_id, product_name, product_description, product_price, product_photo1, product_categories, product_variants FROM products WHERE product_categories = 4')
        edible_ices = cursor.fetchall()
        cursor.execute('SELECT product_id, product_name, product_description, product_price, product_photo1, product_categories, product_variants FROM products WHERE product_categories = 5')
        dairy = cursor.fetchall()
        cursor.execute('SELECT product_id, product_name, product_description, product_price, product_photo1, product_categories, product_variants FROM products WHERE product_categories = 6')
        bakery = cursor.fetchall()
        cursor.execute('SELECT product_id, product_name, product_description, product_price, product_photo1, product_categories, product_variants FROM products WHERE product_categories = 7')
        nonperishable = cursor.fetchall()
        cursor.execute('SELECT product_id, product_name, product_description, product_price, product_photo1, product_categories, product_variants FROM products WHERE product_categories = 8')
        sweet_beverages = cursor.fetchall()
        
        #Fruits and vegetables
        for products in fnv:
            if products['product_photo1']:
                products['product_photo1'] = base64.b64encode(products['product_photo1']).decode('utf-8')
        
        #Confectionery
        for products in confectionery:
            if products['product_photo1']:
                products['product_photo1'] = base64.b64encode(products['product_photo1']).decode('utf-8')
        
        #Cereals
        for products in cereals:
            if products['product_photo1']:
                products['product_photo1'] = base64.b64encode(products['product_photo1']).decode('utf-8')
        
        #Edible Ices
        for products in edible_ices:
            if products['product_photo1']:
                products['product_photo1'] = base64.b64encode(products['product_photo1']).decode('utf-8')
        
        #Dairy
        for products in dairy:
            if products['product_photo1']:
                products['product_photo1'] = base64.b64encode(products['product_photo1']).decode('utf-8')
                
        #Bakery
        for products in bakery:
            if products['product_photo1']:
                products['product_photo1'] = base64.b64encode(products['product_photo1']).decode('utf-8')
                
        #Nonperishable Items
        for products in nonperishable:
            if products['product_photo1']:
                products['product_photo1'] = base64.b64encode(products['product_photo1']).decode('utf-8')
                
        #Sweet Beverages
        for products in sweet_beverages:
            if products['product_photo1']:
                products['product_photo1'] = base64.b64encode(products['product_photo1']).decode('utf-8')
        
        #All Products
        for products in all_products:
            if products['product_photo1']:
                products['product_photo1'] = base64.b64encode(products['product_photo1']).decode('utf-8')
        
        #Profile Picture
        for profile in user:
            if profile['profile_pic']:
                profile['profile_pic'] = base64.b64encode(profile['profile_pic']).decode('utf-8')
        
        #My_orders
        for photo1 in order_display:
            if photo1['product_photo1']:
                photo1['product_photo1'] = base64.b64encode(photo1['product_photo1']).decode('utf-8')
        
        
        # Render the template with the users data
        return render_template(
            'buyer_home.html',
            products = all_products,
            users = user,
            my_order = order_display,
            order_total_value = order_total_value,
            fnv = fnv,
            confectionery = confectionery,
            cereals = cereals,
            edible_ices=edible_ices,
            dairy=dairy,
            bakery=bakery,
            nonperishable=nonperishable,
            sweet_beverages=sweet_beverages
            )
    
    else:
        # If user is not a buyer, deny access
        message = 'You do not have permission to view this page!'
        return redirect(url_for('login'))

########################################################
###############  B U Y E R  O R D E R S  ###############
########################################################

@app.route('/buyer_order_details/<product_id>', methods=['GET', 'POST'])
def buyer_order_details(product_id):
    message = ''
    if 'accounts_id' in session and session['account_type'] == 'buyer':
        # Establish database connection
        conn= get_db_connection()
        
        # Handle failed connection gracefully
        if conn is None:
            message = 'Database connection failed.'
            return redirect(url_for('buyer_home'))
        
        session['buyer_order'] = product_id
        active_user = session.get('accounts_id', None)
        
        
        #Fetch all users form the database  
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT uploader FROM products WHERE product_id= %s AND product_id = %s;', (product_id, product_id))
        uploader = cursor.fetchone()
        session['uploader'] = uploader['uploader']
        uploader_name = session.get('uploader', None)
        cursor.execute('SELECT CONCAT(firstName ," ",  lastName) as name, email, CONCAT("Barangay"," ", barangay ,", ", city ,",", province ,", ", zip_code) as address, profile_pic, status FROM accounts WHERE email= %s AND email = %s;', (uploader_name, uploader_name))
        seller_details = cursor.fetchall()
        cursor.execute('SELECT COUNT(*) as product_count FROM products WHERE uploader= %s AND uploader = %s;', (uploader_name, uploader_name))
        product_count = cursor.fetchall()
        cursor.execute('SELECT product_id, product_name, product_description, product_price, product_stocks, product_photo1, product_photo2, product_photo3, product_photo4, product_categories, product_variants FROM products WHERE product_id= %s AND product_id = %s;', (product_id, product_id))
        all_products = cursor.fetchall()
        cursor.execute('SELECT email, profile_pic, barangay, city, province, zip_code FROM accounts WHERE accounts_id=%s AND accounts_id=%s', (active_user, active_user))
        user = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        for PP in seller_details:
            if PP['profile_pic']:
                PP['profile_pic'] = base64.b64encode(PP['profile_pic']).decode('utf-8')
        
        for photo1 in all_products:
            if photo1['product_photo1']:
                photo1['product_photo1'] = base64.b64encode(photo1['product_photo1']).decode('utf-8')
        
        for photo2 in all_products:
            if photo2['product_photo2']:
                photo2['product_photo2'] = base64.b64encode(photo2['product_photo2']).decode('utf-8')
        
        for photo3 in all_products:
            if photo3['product_photo3']:
                photo3['product_photo3'] = base64.b64encode(photo3['product_photo3']).decode('utf-8')
        
        for photo4 in all_products:
            if photo4['product_photo4']:
                photo4['product_photo4'] = base64.b64encode(photo4['product_photo4']).decode('utf-8')
                
        #Profile Picture
        for profile in user:
            if profile['profile_pic']:
                profile['profile_pic'] = base64.b64encode(profile['profile_pic']).decode('utf-8')
        # Render the template with the users data
        return render_template('buyer_order_details.html', products = all_products, seller_details = seller_details, product_count = product_count, users = user)
    else:
        # If user is not a buyer, deny access
        message = 'You do not have permission to view this page!'
        return redirect(url_for('login'))
    
##################################################################################
###############  B U Y E R  O R D E R  C A R T  C O N D I T I O N  ###############
##################################################################################

@app.route('/order_condition', methods=['get', 'post'])
def order_condition():
    message = ''
    if 'accounts_id' in session and session['account_type'] == 'buyer':
        if request.method == 'POST':
            order_quantity = request.form['order_quantity']
            active_email = session.get('email', None)
            session['order_quantity'] = order_quantity
            if 'buy' in request.form:
                return buyer_my_orders()
            elif 'cart' in request.form:
                return buyer_cart()

#############################################################
###############  B U Y E R  M Y  O R D E R S  ###############
#############################################################

@app.route('/buyer_home')
def buyer_my_orders():
    message = ''
    if 'accounts_id' in session and session['account_type'] == 'buyer':
        order_quantity = session.get('order_quantity', None)
        active_email = session.get('email', None)
        my_orders = session.get('buyer_order', None)
        df = 40
        uploader_name = session.get('uploader', None)
        
        conn= get_db_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
        cursor.execute('SELECT product_id, product_name, product_description, product_price, product_stocks, product_photo1, product_photo2, product_photo3, product_photo4, product_categories, product_variants FROM products WHERE product_id= %s AND product_id = %s;', (my_orders, my_orders))
        my_order = cursor.fetchone()
        cursor.execute('SELECT product_name FROM my_orders WHERE buyer = %s AND buyer = %s;', (active_email, active_email))
        orders = cursor.fetchall()
        cursor.execute('SELECT product_stocks FROM products WHERE product_id = %s AND product_id = %s;', (my_orders, my_orders))
        product_stocks = cursor.fetchone()
        session['db_stocks'] = product_stocks['product_stocks']
        db_stocks = session.get('db_stocks', None)
        if int(order_quantity) > db_stocks:
            return redirect(url_for('buyer_home'))
        else:
            updated_stocks = db_stocks - int(order_quantity)
        cursor.execute('UPDATE products SET product_stocks = %s WHERE product_id=%s', (updated_stocks, my_orders))
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
                
                total_item_price = float(my_order_price) * float(order_quantity)
                
                sql = "INSERT INTO my_orders (product_name, product_description, order_price, order_quantity, product_photo1, product_photo2, product_photo3, product_photo4, product_categories, product_variants, buyer, delivery_fee, item_total_amount, uploader) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
                values = (my_order_name, my_order_description, my_order_price, order_quantity, my_order_photo1, my_order_photo2, my_order_photo3, my_order_photo4, my_order_categories, my_order_variants, active_email, df, total_item_price, uploader_name)
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
                    
        return redirect(url_for('buyer_home'))


##########################################################################
###############  B U Y E R  M Y  O R D E R S  R E M O V E  ###############
##########################################################################

@app.route('/buyer_home/remove_orders/<product_id>')
def buyer_my_orders_remove(product_id):
    message = ''
    if 'accounts_id' in session and session['account_type'] == 'buyer':
        
        # Establish database connection
        conn= get_db_connection()
        my_orders = session.get('buyer_order', None)
        uploader_email = session.get('uploader', None)
        
        # Handle failed connection gracefully
        if conn is None:
            messages = 'Database connection failed.'
            return redirect(url_for('buyer_home'))
            
        #Fetch all users form the database
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT order_quantity FROM my_orders WHERE product_id = %s AND product_id = %s;', (product_id, product_id))
        order_quantity = cursor.fetchone()
        session['order_quantity'] = order_quantity['order_quantity']
        order_stocks = session.get('order_quantity', None)
        cursor.execute('SELECT product_stocks FROM products WHERE product_id = %s AND product_id = %s;', (my_orders, my_orders))
        product_stocks = cursor.fetchone()
        session['product_stocks'] = product_stocks['product_stocks']
        product_stock = session.get('product_stocks', None)
        updated_stocks = product_stock + order_stocks
        cursor.execute('UPDATE products SET product_stocks = %s WHERE product_id=%s AND uploader=%s', (updated_stocks, my_orders, uploader_email))
        conn.commit()
        cursor.execute('DELETE FROM my_orders WHERE product_id=%s AND product_id=%s', (product_id, product_id))
        conn.commit()
        cursor.close()
        conn.close()
        
        
    return redirect(url_for('buyer_home'))



#####################################################################################################################
#####################################################################################################################
###########################################  B U Y E R  C H E C K  O U T  ###########################################
#####################################################################################################################
#####################################################################################################################

@app.route('/condition')
def buyer_checkout_condition():
    message = ''
    if 'accounts_id' in session and session['account_type'] == 'buyer':
            
        active_email = session.get('email', None)
        
        
        conn= get_db_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
        cursor.execute('SELECT product_name FROM my_orders WHERE buyer = %s AND buyer = %s;', (active_email, active_email))
        my_orders = cursor.fetchone()
        
        if my_orders is None:
            return buyer_home()
        else:
            return buyer_checkout()


@app.route('/buyer_checkout')
def buyer_checkout():
    message = ''
    if 'accounts_id' in session and session['account_type'] == 'buyer':
        # Establish database connection
        conn= get_db_connection()
        
        # Handle failed connection gracefully
        if conn is None:
            message = 'Database connection failed.'
            return redirect(url_for('buyer_checkout'))
        
        active_user = session.get('accounts_id', None)
        active_email = session.get('email', None)
        uploader_email = session.get('uploader', None)
        
        #Fetch all users form the database
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT CONCAT(firstName ," ",  lastName) as name, profile_pic FROM accounts WHERE email=%s AND email=%s', (uploader_email, uploader_email))
        uploader = cursor.fetchall()
        cursor.execute('SELECT email, profile_pic, barangay, city, province, zip_code FROM accounts WHERE accounts_id=%s AND accounts_id=%s', (active_user, active_user))
        user = cursor.fetchall()
        cursor.execute('SELECT CONCAT(firstName ," ",  lastName) as name, email, CONCAT("Barangay"," ", barangay ,", ", city ,",", province ,", ", zip_code) as address, status FROM accounts WHERE accounts_id=%s AND accounts_id=%s', (active_user, active_user))
        checkout_details = cursor.fetchall()
        cursor.execute('SELECT product_id ,product_name, product_photo1, order_price, order_quantity, order_price * order_quantity as total_price_item FROM my_orders WHERE buyer = %s AND buyer = %s;', (active_email, active_email))
        order_display = cursor.fetchall()
        cursor.execute('SELECT SUM(order_quantity) as order_count FROM my_orders WHERE buyer = %s AND buyer = %s;', (active_email, active_email))
        order_count = cursor.fetchall()
        cursor.execute('SELECT SUM(item_total_amount) as subTotal, SUM(item_total_amount) + MAX(delivery_fee) as total, MAX(delivery_fee) FROM my_orders WHERE buyer = %s AND buyer = %s;', (active_email, active_email))
        order_total_value = cursor.fetchall()
        
        #Profile Picture
        for profile in uploader:
            if profile['profile_pic']:
                profile['profile_pic'] = base64.b64encode(profile['profile_pic']).decode('utf-8')
        
        #Profile Picture
        for profile in user:
            if profile['profile_pic']:
                profile['profile_pic'] = base64.b64encode(profile['profile_pic']).decode('utf-8')

        #My_orders
        for photo1 in order_display:
            if photo1['product_photo1']:
                photo1['product_photo1'] = base64.b64encode(photo1['product_photo1']).decode('utf-8')
        
        
        # Render the template with the users data
        return render_template('buyer_checkout.html', users= user, checkout_details = checkout_details, order_display=order_display, order_count =order_count, order_total_value=order_total_value, uploader=uploader)
    
    else:
        # If user is not a buyer, deny access
        message = 'You do not have permission to view this page!'
        return redirect(url_for('login'))

#################################################################
###############  B U Y E R  P L A C E  O R D E R  ###############
#################################################################

@app.route('/buyer_checkout/place_order', methods=['get', 'post'])
def buyer_place_order():
    message = ''
    if 'accounts_id' in session and session['account_type'] == 'buyer':
        if request.method =='POST':
            payment_type = request.form['payment']
        # Establish database connection
            conn= get_db_connection()
            
            active_email = session.get('email', None)
            active_user = session.get('accounts_id', None)
            uploader_email = session.get('uploader', None)
            order_status = 0
            
            if payment_type == 'cash':
                payment_status = 0
            else:
                payment_status = 1
            
            # Handle failed connection gracefully
            if conn is None:
                messages = 'Database connection failed.'
                return redirect(url_for('buyer_checkout'))
            
            #Fetch all users form the database
            cursor = conn.cursor(dictionary=True)
            cursor.execute('SELECT CONCAT(firstName ," ",  lastName) as name, email, CONCAT("Barangay"," ", barangay ,", ", city ,",", province ,", ", zip_code) as address, status FROM accounts WHERE accounts_id=%s AND accounts_id=%s', (active_user, active_user))
            checkout_details = cursor.fetchone()
            cursor.execute('SELECT GROUP_CONCAT(product_name) as products FROM my_orders WHERE buyer = %s AND buyer = %s;', (active_email, active_email))
            order_display = cursor.fetchone()
            cursor.execute('SELECT SUM(order_quantity) as order_count FROM my_orders WHERE buyer = %s AND buyer = %s;', (active_email, active_email))
            order_count = cursor.fetchone()
            cursor.execute('SELECT SUM(item_total_amount) as subTotal, SUM(item_total_amount) + MAX(delivery_fee) as total, MAX(delivery_fee) FROM my_orders WHERE buyer = %s AND buyer = %s;', (active_email, active_email))
            order_total_value = cursor.fetchone()
            
            session['buyer_name'] = checkout_details['name']
            session['buyer_loc'] = checkout_details['address']
            session['order_price'] = order_total_value['subTotal']
            session['order_total'] = order_total_value['total']
            session['order_count'] = order_count['order_count']
            session['order_display'] = order_display['products']
            
            name_of_buyer = session.get('buyer_name', None)
            buyer_loc = session.get('buyer_loc', None)
            order_price = session.get('order_price', None)
            order_total = session.get('order_total', None)
            count_of_order = session.get('order_count', None)
            order_name = session.get('order_display', None)
            admin_com = order_total * 0.05
            
            sql = "INSERT INTO orders (product ,buyer_name, buyer_email, buyer_location, order_date, payment_method, order_price, order_total, order_quantity, order_status, payment_status, uploader, admin_com) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
            values = (order_name ,name_of_buyer, active_email, buyer_loc, current_date_time, payment_type, order_price, order_total, count_of_order, order_status, payment_status, uploader_email, admin_com)
            cursor.execute(sql, values)
            conn.commit()
            
            cursor.execute('DELETE FROM my_orders WHERE buyer=%s AND buyer=%s', (active_email,active_email))
            conn.commit()
            cursor.close()
            conn.close()
            
            session.pop('buyer_name', None)
            session.pop('buyer_loc', None)
            session.pop('order_price', None)
            session.pop('order_total', None)
            session.pop('order_display', None)
            
            return redirect(url_for('buyer_home'))

####################################################################################################################
####################################################################################################################
###########################################  B U Y E R  M E S S A G E S  ###########################################
####################################################################################################################
####################################################################################################################

@app.route('/buyer_messages')
def buyer_messages():
    message = ''
    if 'accounts_id' in session and session['account_type'] == 'buyer':
        # Establish database connection
        conn= get_db_connection()
        
        active_user = session.get('accounts_id', None)
        
        # Handle failed connection gracefully
        if conn is None:
            message = 'Database connection failed.'
            return redirect(url_for('buyer_messages'))
            
        #Fetch all users form the database
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT email, profile_pic, barangay, city, province, zip_code FROM accounts WHERE accounts_id=%s AND accounts_id=%s', (active_user, active_user))
        user = cursor.fetchall()
        
        #Profile Picture
        for profile in user:
            if profile['profile_pic']:
                profile['profile_pic'] = base64.b64encode(profile['profile_pic']).decode('utf-8')
        
        # Render the template with the users data
        return render_template('buyer_messages.html', users= user)
    else:
        # If user is not a buyer, deny access
        message = 'You do not have permission to view this page!'
        return redirect(url_for('login'))

##############################################################################################################
##############################################################################################################
###########################################  B U Y E R  S A V E D  ###########################################
##############################################################################################################
##############################################################################################################

@app.route('/buyer_saved')
def buyer_saved():
    message = ''
    if 'accounts_id' in session and session['account_type'] == 'buyer':
        # Establish database connection
        conn= get_db_connection()
        active_user = session.get('accounts_id', None)
        
        # Handle failed connection gracefully
        if conn is None:
            message = 'Database connection failed.'
            return redirect(url_for('buyer_saved'))
            
        #Fetch all users form the database
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT email, profile_pic FROM accounts WHERE accounts_id=%s AND accounts_id=%s', (active_user, active_user))
        user = cursor.fetchall()
        
        for profile in user:
            if profile['profile_pic']:
                profile['profile_pic'] = base64.b64encode(profile['profile_pic']).decode('utf-8')
        
        # Render the template with the users data
        return render_template('buyer_saved.html', users = user)
    
    else:
        # If user is not a buyer, deny access
        message = 'You do not have permission to view this page!'
        return redirect(url_for('login'))
    
########################################################################################################################
########################################################################################################################
###########################################  B U Y E R  A D D  T O  C A R T  ###########################################
########################################################################################################################
########################################################################################################################

@app.route('/buyer_add_to_cart')
def buyer_add_to_cart():
    message = ''
    if 'accounts_id' in session and session['account_type'] == 'buyer':
        # Establish database connection
        conn= get_db_connection()
        active_email = session.get('email', None)
        active_user = session.get('accounts_id', None)
        
        # Handle failed connection gracefully
        if conn is None:
            message = 'Database connection failed.'
            return redirect(url_for('buyer_add_to_cart'))
            
        #Fetch all users form the database
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT email, profile_pic FROM accounts WHERE accounts_id=%s AND accounts_id=%s', (active_user, active_user))
        user = cursor.fetchall()
        cursor.execute('SELECT product_id ,product_name, product_photo1, order_price, order_quantity, order_price * order_quantity as total_price_item FROM cart WHERE buyer = %s AND buyer = %s;', (active_email, active_email))
        order_display = cursor.fetchall()
        cursor.execute('SELECT SUM(item_total_amount) as subTotal, SUM(item_total_amount) * order_quantity + delivery_fee as total, delivery_fee FROM cart WHERE buyer = %s AND buyer = %s;', (active_email, active_email))
        order_total_value = cursor.fetchall()
        
        for profile in user:
            if profile['profile_pic']:
                profile['profile_pic'] = base64.b64encode(profile['profile_pic']).decode('utf-8')
                
        for product in order_display:
            if product['product_photo1']:
                product['product_photo1'] = base64.b64encode(product['product_photo1']).decode('utf-8')
        
        # Render the template with the users data
        return render_template('buyer_add_to_cart.html', users = user, order_display=order_display, order_total_value=order_total_value)
    
    else:
        # If user is not a buyer, deny access
        message = 'You do not have permission to view this page!'
        return redirect(url_for('login'))

####################################################
###############  B U Y E R  C A R T  ###############
####################################################

@app.route('/buyer_add_to_cart', methods=['GET', 'POST'])
def buyer_cart():
    message = ''
    if 'accounts_id' in session and session['account_type'] == 'buyer':
        if request.method =='POST':
            order_quantity = request.form['order_quantity']
            
            active_email = session.get('email', None)
            my_orders = session.get('buyer_order', None)
            df = 40
            uploader_name = session.get('uploader', None)
            
            conn= get_db_connection()
            cursor = conn.cursor(dictionary=True, buffered=True)
            cursor.execute('SELECT product_id, product_name, product_description, product_price, product_stocks, product_photo1, product_photo2, product_photo3, product_photo4, product_categories, product_variants FROM products WHERE product_id= %s AND product_id = %s;', (my_orders, my_orders))
            my_order = cursor.fetchone()
            cursor.execute('SELECT product_name FROM cart WHERE buyer = %s AND buyer = %s;', (active_email, active_email))
            orders = cursor.fetchall()
            cursor.execute('SELECT product_stocks FROM products WHERE product_id = %s AND product_id = %s;', (my_orders, my_orders))
            product_stocks = cursor.fetchone()
            session['db_stocks'] = product_stocks['product_stocks']
            db_stocks = session.get('db_stocks', None)
            if int(order_quantity) > db_stocks:
                return redirect(url_for('buyer_home'))
            else:
                updated_stocks = db_stocks - int(order_quantity)
            cursor.execute('UPDATE products SET product_stocks = %s WHERE product_id=%s', (updated_stocks, my_orders))
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
                    
                    total_item_price = float(my_order_price) * float(order_quantity)
                    
                    sql = "INSERT INTO cart (product_name, product_description, order_price, order_quantity, product_photo1, product_photo2, product_photo3, product_photo4, product_categories, product_variants, buyer, delivery_fee, item_total_amount, uploader) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
                    values = (my_order_name, my_order_description, my_order_price, order_quantity, my_order_photo1, my_order_photo2, my_order_photo3, my_order_photo4, my_order_categories, my_order_variants, active_email, df, total_item_price, uploader_name)
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
                        
            return redirect(url_for('buyer_add_to_cart'))

######################################################
###############  C A R T  R E M O V E  ###############
######################################################

@app.route('/buyer_add_to_cart/remove_orders/<product_id>')
def buyer_cart_remove(product_id):
    message = ''
    if 'accounts_id' in session and session['account_type'] == 'buyer':
        
        # Establish database connection
        conn= get_db_connection()
        my_orders = session.get('buyer_order', None)
        uploader_email = session.get('uploader', None)
        
        # Handle failed connection gracefully
        if conn is None:
            messages = 'Database connection failed.'
            return redirect(url_for('buyer_home'))
            
        #Fetch all users form the database
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT order_quantity FROM cart WHERE product_id = %s AND product_id = %s;', (product_id, product_id))
        order_quantity = cursor.fetchone()
        session['order_quantity'] = order_quantity['order_quantity']
        order_stocks = session.get('order_quantity', None)
        cursor.execute('SELECT product_stocks FROM products WHERE product_id = %s AND product_id = %s;', (my_orders, my_orders))
        product_stocks = cursor.fetchone()
        session['product_stocks'] = product_stocks['product_stocks']
        product_stock = session.get('product_stocks', None)
        updated_stocks = product_stock + order_stocks
        cursor.execute('UPDATE products SET product_stocks = %s WHERE product_id=%s AND uploader=%s', (updated_stocks, my_orders, uploader_email))
        conn.commit()
        cursor.execute('DELETE FROM cart WHERE product_id=%s AND product_id=%s', (product_id, product_id))
        conn.commit()
        cursor.close()
        conn.close()
        
    return redirect(url_for('buyer_add_to_cart'))

###########################################################
###############  C A R T  C H E C K  O U T  ###############
###########################################################

@app.route('/buyer_add_to_cart/checkout/', methods=['get', 'post'])
def buyer_cart_checkout():
    message = ''
    if 'accounts_id' in session and session['account_type'] == 'buyer':
        if request.method == 'POST':
            selected_items = request.form.getlist('selected')
            
        # Establish database connection
            conn= get_db_connection()
            uploader_email = session.get('uploader', None)
            active_email = session.get('email', None)
            
            # Handle failed connection gracefully
            if conn is None:
                messages = 'Database connection failed.'
                return redirect(url_for('buyer_home'))
                
            #Fetch all users form the database
            cursor = conn.cursor(dictionary=True)
            
            for selected_values in selected_items:
                    cursor.execute('INSERT INTO my_orders SELECT * FROM cart WHERE product_id = %s  AND buyer IN(SELECT buyer FROM cart WHERE product_id = %s)', (selected_values, selected_values))
                    cursor.execute('DELETE FROM cart WHERE product_id = %s AND product_id = %s', (selected_values, selected_values))
                    conn.commit()
                
            cursor.close()
            conn.close()
        
        return redirect(url_for('buyer_checkout'))

###################################################################################################################################
###################################################################################################################################
###########################################  B U Y E R  P U R C H A S E  H I S T O R Y  ###########################################
###################################################################################################################################
###################################################################################################################################

@app.route('/buyer_MyPurchase')
def buyer_purchase_history():
    message = ''
    if 'accounts_id' in session and session['account_type'] == 'buyer':
        # Establish database connection
        conn= get_db_connection()
        
        active_user = session.get('accounts_id', None)
        active_email = session.get('email', None)
        
        # Handle failed connection gracefully
        if conn is None:
            message = 'Database connection failed.'
            return redirect(url_for('buyer_purchase_history'))
            
        #Fetch all users form the database
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM orders WHERE buyer_email=%s AND buyer_email=%s ORDER BY order_status, payment_status ASC', (active_email, active_email))
        orders = cursor.fetchall()
        cursor.execute('SELECT email, profile_pic FROM accounts WHERE accounts_id=%s AND accounts_id=%s', (active_user, active_user))
        user = cursor.fetchall()
        
        for profile in user:
            if profile['profile_pic']:
                profile['profile_pic'] = base64.b64encode(profile['profile_pic']).decode('utf-8')
        
        # Render the template with the users data
        return render_template('buyer_MyPurchase.html', users = user, orders=orders)
    
    else:
        # If user is not a buyer, deny access
        message = 'You do not have permission to view this page!'
        return redirect(url_for('login'))

###############################################
###############  P A Y M E N T  ###############
###############################################

@app.route('/buyer_MyPurchase/pay/<order_id>')
def pay(order_id):
    message = ''
    if 'accounts_id' in session and session['account_type'] == 'buyer':
        # Establish database connection
        conn= get_db_connection()
        
        active_user = session.get('accounts_id', None)
        active_email = session.get('email', None)
        
        # Handle failed connection gracefully
        if conn is None:
            message = 'Database connection failed.'
            return redirect(url_for('seller_delivery'))
            
        #Fetch all users form the database
        cursor = conn.cursor(dictionary=True)
        cursor.execute('UPDATE orders SET payment_status = 1 WHERE order_id=%s AND order_id=%s', (order_id, order_id))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        # Render the template with the users data
        return redirect(url_for('buyer_purchase_history'))
    
    else:
        # If user is not a super admin, deny access
        message = 'You do not have permission to view this page!'
        return redirect(url_for('login'))


###########################################################################################################################
###########################################################################################################################
###########################################  B U Y E R  E D I T  P R O F I L E  ###########################################
###########################################################################################################################
###########################################################################################################################

@app.route('/buyer_edit_profile')
def buyer_edit_profile():
    message = ''
    if 'accounts_id' in session and session['account_type'] == 'buyer':
        # Establish database connection
        conn= get_db_connection()
        
        active_user = session.get('accounts_id', None)
        
        # Handle failed connection gracefully
        if conn is None:
            message = 'Database connection failed.'
            return redirect(url_for('buyer_edit_profile'))
            
        #Fetch all users form the database
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT firstName, lastName, email, password, profile_pic FROM accounts WHERE accounts_id=%s AND accounts_id=%s', (active_user, active_user))
        user = cursor.fetchall()
        cursor.close()
        conn.close()
        
        for profile in user:
            if profile['profile_pic']:
                profile['profile_pic'] = base64.b64encode(profile['profile_pic']).decode('utf-8')
        
        # Render the template with the users data
        return render_template('buyer_edit_profile.html', users = user)
    
    else:
        # If user is not a super admin, deny access
        message = 'You do not have permission to view this page!'
        return redirect(url_for('login'))
    
########################################################
###############  S A V E  P R O F I L E  ###############
########################################################

@app.route('/buyer_edit_profile/save', methods=['GET', 'POST'])
def buyer_save_profile():
    message = ''
    if 'accounts_id' in session and session['account_type'] == 'buyer':
        if request.method == 'POST':
            firstName = request.form['first_name']
            lastName = request.form['last_name']
            password = request.form['pass']
            confirm_pass = request.form['confirm_pass']
            profile_picture = request.files['profile_pics']
            active_user = session.get('accounts_id', None)
            # Establish database connection
            conn= get_db_connection()
            
            active_user = session.get('accounts_id', None)
            
            # Handle failed connection gracefully
            if conn is None:
                message = 'Database connection failed.'
                return redirect(url_for('buyer_edit_profile'))
            
            if password == confirm_pass:
                #Fetch all users form the database
                cursor = conn.cursor(dictionary=True)
                cursor.execute('UPDATE accounts SET firstName = %s, lastName = %s, password = %s, profile_pic = %s WHERE accounts_id=%s;', (firstName, lastName, password, profile_picture.read(),active_user))
                conn.commit()
                cursor.close()
                conn.close()
                return redirect(url_for('buyer_edit_profile'))
            else:
                message = 'Password does not match!'
                return render_template('buyer_edit_profile.html', message = message)
    else:
        # If user is not a super admin, deny access
        message = 'You do not have permission to view this page!'
        return redirect(url_for('login'))
    
######################################################################################################################
######################################################################################################################
###########################################  F O O D I T Y  E X P R E S S  ###########################################
######################################################################################################################
######################################################################################################################

@app.route('/Foodity-express-dashboard')
def foodity_express_dashboard():
    message = ''
    if 'accounts_id' in session and session['account_type'] == 'courier':
        # Establish database connection
        conn= get_db_connection()
            
        active_user = session.get('accounts_id', None)
        active_email = session.get('email', None)
            
        # Handle failed connection gracefully
        if conn is None:
            message = 'Database connection failed.'
            return redirect(url_for('login'))
            
        cursor = conn.cursor(dictionary=True, buffered=True)
            
        cursor.execute('SELECT email, profile_pic, barangay, city, province, zip_code FROM accounts WHERE accounts_id=%s AND accounts_id=%s', (active_user, active_user))
        user = cursor.fetchall()
        
        #Profile Picture
        for profile in user:
            if profile['profile_pic']:
                profile['profile_pic'] = base64.b64encode(profile['profile_pic']).decode('utf-8')
                
            
        return render_template('foodity_express_dashboard.html', profile = profile)
    else:
        # If user is not a super admin, deny access
        message = 'You do not have permission to view this page!'
        return redirect(url_for('login'))

################################################################################################################
################################################################################################################
###########################################  F L A S K  R U N N E R  ###########################################
################################################################################################################
################################################################################################################

if __name__ == "__main__":
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['CACHE_TYPE'] = 'redis'
    
    
    app.run(debug=True, port=5003)
