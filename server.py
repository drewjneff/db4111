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
from flask import Flask, request, render_template, g, session, jsonify, url_for, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app = Flask(__name__, static_folder='static')
app.secret_key = 'your_secret_key_here'

context = dict()
find_context = dict()


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

#Login page 
@app.route('/login')
def login():
	return render_template('login.html')


# On login submission
@app.route('/login_attempt', methods=['POST'])
def login_attempt():
    uname_form = request.form['login_uname']
    uname = uname_form.upper() 
    password = request.form['login_pw']
    check_login_credentials = '''SELECT uname FROM USERS WHERE (UPPER(uname),password)=(:uname,:password)'''
    cursor = g.conn.execute(text(check_login_credentials), {'uname': uname, 'password': password})
    row = cursor.fetchone()
    if row is None:
        print("No match")
        check_user_exists = '''SELECT uname FROM USERS WHERE UPPER(uname)=:uname'''
        cursor = g.conn.execute(text(check_user_exists),{'uname':uname})
        row = cursor.fetchone()
        if row is None:
            login_error_message = "Error: User Not Found"
        else:
            login_error_message = "Error: Invalid Password"
        return render_template('login.html',login_error_message=login_error_message)
    else:
        print("Found matching row:", row)
        session['username'] = uname_form 
        context.clear()
        context['success_message'] = "Welcome "+row[0]+"!"
        context['logout_status'] = "Logout "+uname_form
        return render_template('index.html',**context)


@app.route('/logout')
def logout():
	session.pop('username', None)
	return redirect(url_for('index'))

@app.route('/clear_add_error')
def clear_add_error():
     find_context.clear()
     return redirect(url_for('add'))
     


#Index page 
@app.route('/')
def index():
    username = session.get('username')
    if username is None:
        login_error_message = "Please Log In To Continue or"
        return render_template("login.html",login_error_message=login_error_message)
    else:
        logout_status = "Logout "+username
        find_context.clear()
        return render_template("index.html",logout_status=logout_status)

	

#Leaderboard page 	
@app.route('/leaderboard')
def another():
	username = session.get('username')
	if username is None:
		login_error_message = "Please Log In To Continue or"
		return render_template("login.html",login_error_message=login_error_message)
	else:
		leaderboard_query = "SELECT uname, num_br_visited FROM users WHERE num_br_visited >= 1 ORDER BY num_br_visited DESC LIMIT 10"
		cursor = g.conn.execute(text(leaderboard_query))
		results = cursor.fetchall()
		context.clear()
		context["results"] = results
		context["logout_status"] = "Logout "+username
		cursor.close()
		return render_template("leaderboard.html",**context)


#Review page
@app.route('/reviews')
def reviews():
	username = session.get('username')
	if username is None:
		login_error_message = "Please Log In To Continue or"
		return render_template("login.html",login_error_message=login_error_message)
	else:
		context.clear()
		context["logout_status"] = "Logout "+username
		return render_template("reviews.html",**context)
        
@app.route('/add')
def add():
    username = session.get('username')
    if username is None:
        login_error_message = "Please Log In To Continue or"
        return render_template("login.html", login_error_message=login_error_message)
    else:
        context.clear()
        if "success_message" in find_context:
            context["success_message"] = find_context["success_message"]
        if "query_error_message" in find_context:
            context["query_error_message"] = find_context["query_error_message"]
        get_buildings_query = "SELECT building_id, bname FROM building ORDER BY bname"
        cursor = g.conn.execute(text(get_buildings_query))
        buildings = cursor.fetchall()
        context["building_options"] = buildings
        context["logout_status"] = "Logout " + username
        cursor.close()
        return render_template("add.html", **context)



@app.route('/add_br', methods=['POST'])
def add_br():
    username = session.get('username')
    if username is None:
        login_error_message = "Please Log In To Continue or"
        return render_template("login.html", login_error_message=login_error_message)
    else:
        data = []
        fields = ['building', 'floor', 'gender', 'br_description', 'single_use', 'handicap', 'num_toilet', 'num_sink', 'num_urinal']
        for field in fields:
            value = request.form.get(field)
            if value:
                data.append(value)
            else:
                data.append(None)
        try:
            add_query_string = '''INSERT INTO bathroom(building_id, floor, gender, br_description,single_use,handicap,num_toilet,num_sink,num_urinal) 
               					  VALUES (:building, :floor, :gender, :br_description, :single_use, :handicap, :num_toilet, :num_sink, :num_urinal)
               				   '''
            g.conn.execute(text(add_query_string), {'building': data[0], 'floor': data[1], 'gender': data[2], 'br_description': data[3], 'single_use': data[4], 'handicap': data[5], 'num_toilet': data[6],'num_sink':data[7],'num_urinal':data[8]})
            g.conn.commit()
            find_context["success_message"] = "Success! Bathroom Added."
            return redirect(url_for('add'))
        except Exception as e:
            find_context["query_error_message"] = f"Error adding bathroom: {str(e)}"
            return redirect(url_for('add'))
            #return render_template('add.html', query_error_message=query_error_message)

      


@app.route('/find')
def find():
    username = session.get('username')
    if username is None:
        login_error_message = "Please Log In To Continue or"
        return render_template("login.html", login_error_message=login_error_message)
    else:
        get_buildings_query = "SELECT building_id, bname FROM building ORDER BY bname"
        context.clear()
        if "results" in find_context:
              context["results"] = find_context["results"]
              context["link_message"] = find_context["link_message"]
              context["query_message"] = find_context["query_message"]
        cursor = g.conn.execute(text(get_buildings_query))
        buildings = cursor.fetchall()
        context["building_options"] = buildings
        context["logout_status"] = "Logout " + username
        cursor.close()
        return render_template("find.html", **context)



#Gets second dropdown option of floors depending on the building selected in the first option 
@app.route('/get_second_dropdown/<building>')
def get_second_dropdown(building):
    get_floors_query = """SELECT floors FROM building WHERE building_id = :building"""
    cursor = g.conn.execute(text(get_floors_query), {'building': building})
    rows = cursor.fetchall()
    if len(rows) == 0:
        return jsonify([])
    if rows[0][0] is None:
        return jsonify([])
    floors = [floor.strip() for floor in rows[0][0]]
    return jsonify(floors)

	
@app.route('/find_query', methods=['POST'])
def find_query():
    username = session.get('username')
    if username is None:
        login_error_message = "Please Log In To Continue or"
        return render_template("login.html", login_error_message=login_error_message)
    else:
        data = []
        if request.form.get('building'):
            data.append(request.form['building'])
        else:
            data.append(None)
        if request.form.get('floor'):
           data.append(request.form['floor'])
        else:
            data.append(None)
        if request.form.get('gender'):
            data.append(request.form['gender'])
        else:
            data.append(None)

        for i in range(len(data)):
            if data[i] == '':
                data[i] = None
        find_query_str = """
        SELECT bname, floor, br_description, gender, 
               COALESCE(CAST(handicap AS VARCHAR), 'N/A'), 
               COALESCE(CAST(num_toilet AS VARCHAR), 'N/A'),
               COALESCE(CAST(num_sink AS VARCHAR), 'N/A'),
               COALESCE(CAST(num_urinal AS VARCHAR), 'N/A'),
               CASE 
                   WHEN single_use = true THEN 'yes'
                   WHEN single_use = false THEN 'no'
                   ELSE 'N/A'
               END
        FROM bathroom 
        NATURAL JOIN building
        WHERE building_id = :building 
          AND (floor = COALESCE(:floor, floor)) 
          AND (gender = COALESCE(:gender, gender))
        ORDER BY bname, floor;
        """
        cursor = g.conn.execute(text(find_query_str), {'building': data[0], 'floor': data[1], 'gender': data[2]})
        results = cursor.fetchall()
        context.clear()
        find_context["results"] = results
        find_context["logout_status"] = "Logout " + username
        get_bname_query = "SELECT bname FROM building WHERE building_id = :building"
        cursor = g.conn.execute(text(get_bname_query), {'building': data[0]})
        bname_result = cursor.fetchone()
        bname = bname_result[0]
        print(bname_result)
        cursor.close()
        find_context["link_message"] = "Add more."
        if not results:
              find_context["query_message"] = "No Bathrooms On Record For "+bname+". "
              find_context["link_message"] = "Be the first to add."
        elif len(results) == 1 :
              find_context["query_message"] = "Displaying 1 Bathroom On Record From "+bname+". "
        else:
              find_context["query_message"] = "Displaying "+str(len(results))+" Bathrooms On Record From "+bname+". "
        return redirect(url_for('find'))




#Random page
@app.route('/random')
def random():
	username = session.get('username')
	if username is None:
		login_error_message = "Please Log In To Continue or"
		return render_template("login.html",login_error_message=login_error_message)
	else:
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
		context.clear()
		context["results"] = results
		context["logout_status"] = "Logout "+username
		cursor.close()
		return render_template("random.html",**context)


# Register page 
@app.route('/register')
def register():
	return render_template('register.html')


# Register Submission
@app.route('/register_user', methods=['POST'])
def register_user():
    data = []
    data.append(request.form['uname'])
    data.append(request.form['password'])
    data.append(request.form['gender'])
    data.append(request.form['class_year'])
    data.append(request.form['favorite_br'])
    data.append(request.form['home_br'])

    for i in range(len(data)):
        if data[i] == '':
            data[i] = None

    try:
        g.conn.execute(text('INSERT INTO users(uname, password, gender, class_year, favorite_br, home_br) VALUES (:uname, :password, :gender, :class_year, :favorite_br, :home_br)'), {'uname': data[0], 'password': data[1], 'gender': data[2], 'class_year': data[3], 'favorite_br': data[4], 'home_br': data[5]})
        g.conn.commit()
        success_message = "Account Created! Welcome "+data[0]+"! Please login to continue."
        return render_template("login.html",success_message=success_message)
    except Exception as e:
        register_error_message = f"Error executing query: {str(e)}"
        print(register_error_message)
        return render_template('register.html', register_error_message=register_error_message)


#QUERY ON index.html 
@app.route('/query', methods=['GET'])
def query():
    username = session.get('username')
    sql_query = request.args.get('query')
    try:
        cursor = g.conn.execute(text(sql_query))
        results = cursor.fetchall()
        context.clear()
        context["results"] = results
        context["column_names"]=cursor.keys()
        context["query_display_text"]="Your Query: "
        context["logout_status"] = "Logout "+username
        context["query_display_data"]=sql_query
        #context["column_names"] = [desc[0] for desc in cursor.description]
        return render_template('index.html', **context)
        cursor.close()  
    except Exception as e:
        query_error_message = f"Error executing query: {str(e)}"
        print(query_error_message)
        return render_template('index.html', query_error_message=query_error_message)


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
