
import mysql.connector
from config import *

def get_connection():

    connection=mysql.connector.connect(

        host=HOST,

        user=USER,

        password=PASSWORD,

        database=DATABASE

    )

    return connection
