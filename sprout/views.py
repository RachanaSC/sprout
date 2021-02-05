"""
Routes and views for the flask application.
"""

import flask
from flask import request, jsonify
import sqlite3
import requests

app = flask.Flask(__name__)
app.config["DEBUG"] = True

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


@app.route('/', methods=['GET'])
def home():
    return '''<h1>Sprout API</h1>
<p>A prototype API for distant reading of sprout.</p>'''


@app.route('/api/get', methods=['GET'])
def get_data():
   url="https://api.publicapis.org/entries"
   
   x = requests.get(url)
   x = x.json()
   api_data = x['entries']
   print(type(api_data))

   conn = sqlite3.connect('database.db')   
   conn.row_factory = dict_factory
   cur = conn.cursor()
  
   
   flag=0
   for key in api_data:       
       flag=cur.execute("INSERT INTO public (API,Description,Auth,HTTPS,Cors,Link,Category) values (?,?,?,?,?,?,?);",(key['API'],key['Description'],key['Auth'],key['HTTPS'],key['Cors'],key['Link'],key['Category']))
      
   if flag:
       print("all data inserted")
   all_public = cur.execute('SELECT * FROM public;').fetchall()
   conn.close()
   return  jsonify(all_public)


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


@app.route('/api/v1/resources/books', methods=['GET'])
def api_filter():
    query_parameters = request.args

    id = query_parameters.get('id')
    published = query_parameters.get('published')
    author = query_parameters.get('author')

    query = "SELECT * FROM books WHERE"
    to_filter = []

    if id:
        query += ' id=? AND'
        to_filter.append(id)
    if published:
        query += ' published=? AND'
        to_filter.append(published)
    if author:
        query += ' author=? AND'
        to_filter.append(author)
    if not (id or published or author):
        return page_not_found(404)

    query = query[:-4] + ';'

    conn = sqlite3.connect('database.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()

    results = cur.execute(query, to_filter).fetchall()

    return jsonify(results)


app.run()

   #if conn:
      # print("Opened database successfully")

   #exe=conn.execute('CREATE TABLE public (API TEXT, Description TEXT, Auth TEXT,HTTPS TEXT,Cors TEXT,Link TEXT,Category Text)')
   #if exe:
        #print("Table created successfully")
   #requests.get(url, auth = ('myAPIkey', '')) 