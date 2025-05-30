from app import app
from app import db
from flask import request, jsonify, session
import base64


#############################################################################################
#############################################################################################
##############################  S T O R E  P R O D U C T  I D  ##############################
#############################################################################################
#############################################################################################

@app.route('/storeProductId', methods= ['POST'])
def storeProductId():
    data = request.get_json()
    session['clickedProduct'] = data.get("productID")
    
    return jsonify({'status': 'success', 'message': 'Product Id saved to session'}), 200 


@app.route('/storeToPayId', methods= ['POST'])
def storeToPayID():
    data = request.get_json()
    session['order-product-id'] = data.get("productID")
    
    return jsonify({'status': 'success', 'message': 'Product Id saved to session'}), 200 