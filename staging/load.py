import psycopg2
import json
import os
from os.path import join, dirname
from source import main
from dotenv import load_dotenv


def connection():

    con = psycopg2.connect(
        database=os.getenv('DB'),
        user=os.getenv('USER'),
        password=os.getenv('PASSWORD'),
        host='localhost',
        port='5433'
    )

    return con


def insert_data(data: list):
    sql = 'INSERT INTO metadata_raw_folder VALUES (%s, %s, %s)'
    with connection() as con:
        curs = con.cursor()
        for i in data:
            try:
                curs.execute(sql, (i['path'], i['nbre_folders'], i['nbre_files']))
            except Exception as e:
                print(f'Couldn\'t insert the data: {e}')


def insert_raw_data(data: list):
    sql = "INSERT INTO raw_data(raw_json_data) VALUES (%s)"
    with connection() as con:
        curs = con.cursor()
        for i in data:
            try:
                curs.execute(sql, (json.dumps(i),))
            except Exception as e:
                print(f'Couldn\'t insert the data: {e}')



if __name__=='__main__':
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path=dotenv_path)
    insert_raw_data(main())
