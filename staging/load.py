import psycopg2
from psycopg2 import sql
import json
import os
from yaml import safe_load as yml
from os.path import join, dirname
from source import main, get_folder_structure
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path=dotenv_path)

def connection():

    con = psycopg2.connect(
        database=os.getenv('DB'),
        user=os.getenv('USER'),
        password=os.getenv('PASSWORD'),
        host='localhost',
        port='5433'
    )

    return con


def insert_data(table_name: str, data: tuple):
    with open("staging/inserts_sql.yaml") as r:
        file = yml(r)
    query = file['inserts'][table_name]

    with connection() as con:
        curs = con.cursor()
        curs.execute(query, data)

if __name__=='__main__':
    pass
