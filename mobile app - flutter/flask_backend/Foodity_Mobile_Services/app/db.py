import mysql.connector # Add this import
from mysql.connector import Error

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
            password="",         # Replace with your DB password
            database="foodity"  # Your database name
        )
        return conn
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None
