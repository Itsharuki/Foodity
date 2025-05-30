from flask import Flask, jsonify, session
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
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = 'Haruki'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 
now = datetime.now()
current_date_time = now
CORS(app, resources={r"/api/": {"origins": "http://10.0.2.2:5000"}})

from app import db
from app import user
from app import logged_users
from app import logout
from buyer import get_products
from buyer import search_products
from buyer import save_product_id
from buyer import get_product_details
from buyer import save_order_count
from buyer import save_cart_count
from buyer import get_myOrder_details
from buyer import get_user_details
from buyer import remove_product
from buyer import get_cart_details
from buyer import get_profile_details
from buyer import get_orders
from buyer import order_placement
from buyer import cart_checkout
from buyer import payment_update
from buyer import get_order_details