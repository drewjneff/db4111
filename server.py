"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app = Flask(__name__, static_folder='static')

context = dict()


# XXX: The URI should be in the format of:
#     postgresql://USER:PASSWORD@34.73.36.248/project1
DATABASE_USERNAME = "djn2119"
DATABASE_PASSWRD = "8055"
DATABASE_HOST = "34.148.107.47" # change to 34.28.53.86 if you used database 2 for part 2
DATABASEURI = f"postgresql://djn2119:8055@34.148.107.47/project1"


# This line creates a database engine that knows how to connect to the URI above.
engine = create_engine(DATABASEURI)

@app.before_request
def before_request():
	"""
	This function is run at the beginning of every web request 
	(every time you enter an address in the web browser).
	We use it to setup a database connection that can be used throughout the request.

	The variable g is globally accessible.
	"""
	try:
		g.conn = engine.connect()
	except:
		print("uh oh, problem connecting to database")
		import traceback; traceback.print_exc()
		g.conn = None

@app.teardown_request
def teardown_request(exception):
	"""
	At the end of the web request, this makes sure to close the database connection.
	If you don't, the database could run out of memory!
	"""
	try:
		g.conn.close()
	except Exception as e:
		pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: https://flask.palletsprojects.com/en/1.1.x/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/



#Index page 
@app.route('/')
def index():
	
	print(request.args)
	return render_template("index.html")
	
	'''
	select_query = "SELECT name from test"
	cursor = g.conn.execute(text(select_query))
	names = []
	for result in cursor:
		names.append(result[0])
	cursor.close()
'''

#Leaderboard page 	
@app.route('/leaderboard')
def another():
	leaderboard_query = "SELECT uname, num_br_visited FROM users WHERE num_br_visited >= 1 ORDER BY num_br_visited DESC LIMIT 10"
	cursor = g.conn.execute(text(leaderboard_query))
	results = cursor.fetchall()
	context["results"] = results
	cursor.close()
	return render_template("leaderboard.html",**context)


#Review page
@app.route('/reviews')
def review():
	return render_template("reviews.html")


#Random page
@app.route('/random')
def random():
	rand_query = """ SELECT bname, floor, br_description, gender, 
       					COALESCE(CAST(handicap AS VARCHAR), 'N/A'), 
       					COALESCE(CAST(num_toilet AS VARCHAR),'N/A'),
       					COALESCE(CAST(num_sink AS VARCHAR),'N/A'),
       					COALESCE(CAST(num_urinal AS VARCHAR),'N/A'),
       					CASE 
							WHEN single_use = true THEN 'yes'
         					WHEN single_use = false THEN 'no'
         					ELSE 'N/A'
       					END
					 FROM bathroom NATURAL JOIN building 
					 ORDER BY RANDOM() 
					 LIMIT 1;"""
	cursor = g.conn.execute(text(rand_query))
	results = cursor.fetchall()
	context["results"] = results
	cursor.close()
	return render_template("random.html",**context)




"""
# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
	# accessing form inputs from user
	name = request.form['name']
	
	# passing params in for each variable into query
	params = {}
	params["new_name"] = name
	g.conn.execute(text('INSERT INTO test(name) VALUES (:new_name)'), params)
	g.conn.commit()
	return redirect('/')
"""

#QUERY ON index.html 
@app.route('/query', methods=['GET'])
def query():
    sql_query = request.args.get('query')
    try:
        cursor = g.conn.execute(text(sql_query))
        results = cursor.fetchall()
        context["results"] = results
        context["column_names"]=cursor.keys()
        context["query_display_text"]="Your Query: "
        context["query_display_data"]=sql_query
        #context["column_names"] = [desc[0] for desc in cursor.description]
        return render_template('index.html', **context)
        cursor.close()  
    except Exception as e:
        query_error_message = f"Error executing query: {str(e)}"
        print(query_error_message)
        return render_template('index.html', query_error_message=query_error_message)
        cursor.close()




if __name__ == "__main__":
	import click

	@click.command()
	@click.option('--debug', is_flag=True)
	@click.option('--threaded', is_flag=True)
	@click.argument('HOST', default='0.0.0.0')
	@click.argument('PORT', default=8111, type=int)
	def run(debug, threaded, host, port):
		"""
		This function handles command line parameters.
		Run the server using:

			python server.py

		Show the help text using:

			python server.py --help

		"""

		HOST, PORT = host, port
		print("running on %s:%d" % (HOST, PORT))
		app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

run()
