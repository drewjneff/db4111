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

app.debug = 'production'


# XXX: The URI should be in the format of:
#     postgresql://USER:PASSWORD@34.73.36.248/project1
DATABASE_USERNAME = "djn2119"
DATABASE_PASSWRD = "8055"
DATABASE_HOST = "34.148.107.47" # change to 34.28.53.86 if you used database 2 for part 2
DATABASEURI = f"postgresql://djn2119:8055@34.148.107.47/project1"


# This line creates a database engine that knows how to connect to the URI above.
engine = create_engine(DATABASEURI)


print("")
print("\033[32m_______________________________________")
print("|                                     |")
print("\033[32m|            SERVER OPENED            |")
print("|            SUCCESSFULLY             |")
print("|                                     |")
print("|           localhost:8111            |")
print("|_____________________________________|\033[37m")
print("")


@app.before_request
def before_request():
	try:
		g.conn = engine.connect()
	except:
		print("uh oh, problem connecting to database")
		import traceback; traceback.print_exc()
		g.conn = None

@app.teardown_request
def teardown_request(exception):
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
    check_login_credentials = '''SELECT user_id, uname FROM USERS WHERE (UPPER(uname),password)=(:uname,:password)'''
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
            login_error_message = "Error: Invalid Password. Try again or"
        return render_template('login.html',login_error_message=login_error_message)
    else:
        session['username'] = row[1]
        session['user_id'] = row[0]
        print("User "+str(row[0])+": "+row[1]+" logged in")
        context.clear()
        context['success_message'] = "Welcome "+str(row[1])+"!"
        context['logout_status'] = "Logout "+str(row[1])
        return render_template('index.html',**context)


@app.route('/logout')
def logout():
    username, user_id = session.get('username'),session.get('user_id')
    print("User "+str(user_id)+": "+username+" logged out")
    session.pop('user_id', None)
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
        return render_template("login.html", login_error_message=login_error_message)
    else:
        context.clear()
        if "results" in find_context:
            context["results"] = find_context["results"]
            context["query_message"] = find_context["query_message"]
            context["link_message"] = find_context["link_message"]
        get_users_query = "SELECT user_id, uname FROM users ORDER BY uname"
        cursor = g.conn.execute(text(get_users_query))
        users = cursor.fetchall()
        context["user_options"] = users
        get_buildings_query = "SELECT building_id, bname FROM building ORDER BY bname"
        cursor = g.conn.execute(text(get_buildings_query))
        buildings = cursor.fetchall()
        context["building_options"] = buildings
        context["logout_status"] = "Logout " + username
        cursor.close()
        return render_template("reviews.html", **context)
    


@app.route('/review_query', methods=['POST'])
def review_query():
    username = session.get('username')
    if username is None:
        login_error_message = "Please Log In To Continue or"
        return render_template("login.html", login_error_message=login_error_message)
    else:
        data = []
        fields = ['user', 'building']
        for field in fields:
            value = request.form.get(field)
            if value:
                data.append(value)
            else:
                data.append(None)
        review_query_str = """SELECT u.uname, b.bname, br.floor, '#' || br.br_id || ' ' || COALESCE(CAST(br.br_description AS VARCHAR), ''), 
                              		br.gender, COALESCE(CAST(r.body AS VARCHAR), '') AS body, r.rating, r.review_date 
							  FROM review r JOIN bathroom br ON r.br_id = br.br_id 
								    JOIN building b ON b.building_id = br.building_id 
									JOIN users u ON r.user_id = u.user_id
							  WHERE (u.user_id = COALESCE(:user,u.user_id)) AND (b.building_id = COALESCE(:building,b.building_id))
							  ORDER BY r.review_date DESC, u.user_id, b.building_id
       					   """
        cursor = g.conn.execute(text(review_query_str), {'user': data[0], 'building': data[1]})
        results = cursor.fetchall()
        context.clear()
        find_context["results"] = results
        find_context["logout_status"] = "Logout " + username
        cursor.close()
        find_context["link_message"] = "Add Review."
        if not results:
              find_context["query_message"] = "No Reviews On Record. "
              find_context["link_message"] = "Be the first to add."
        else:
              find_context["query_message"] = "Displaying "+str(len(results))+" Reviews On Record. "
        return redirect(url_for('reviews'))
    
@app.route('/add_review')
def add_review():
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
        get_buildings_query = "SELECT DISTINCT building.building_id, bname FROM building JOIN bathroom ON building.building_id = bathroom.building_id ORDER BY bname"
        cursor = g.conn.execute(text(get_buildings_query))
        buildings = cursor.fetchall()
        context["building_options"] = buildings
        context["logout_status"] = "Logout " + username
        cursor.close()
        return render_template("add_review.html", **context)

#Gets bathroom dropdown option of depending on the building and floor selected
#followed this tutorial for cascading dropdown https://www.youtube.com/watch?v=jIAPewyzrp0
@app.route('/get_br_dropdown/<building>/<floor>')
def get_br_dropdown(building, floor):
    get_br_query = """
        SELECT br_id AS id, (floor || ' floor ' || COALESCE(CAST(br_description AS VARCHAR), '') || ' ' || gender) AS label
        FROM bathroom WHERE (building_id = :building) and (floor = :floor)
    """
    cursor = g.conn.execute(text(get_br_query), {'building': building, 'floor': floor})
    rows = cursor.fetchall()
    if len(rows) == 0:
        result = []
    else:
        result = [dict(id=row.id, label=row.label) for row in rows]
    return jsonify(result)

@app.route('/get_floor_dropdown/<building>')
def get_floor_dropdown(building):
    get_floors_query = """SELECT DISTINCT br.floor,
               CAST(CASE WHEN br.floor ~ '\d+' 
                         THEN regexp_replace(CAST(br.floor AS TEXT), '\D', '', 'g')::INTEGER
                         ELSE NULL
                    END AS INTEGER) AS floor_order
        FROM building b
        JOIN bathroom br ON b.building_id = br.building_id
        WHERE b.building_id = :building
        ORDER BY floor_order NULLS FIRST, br.floor;


                       """
    cursor = g.conn.execute(text(get_floors_query), {'building': building})
    rows = cursor.fetchall()
    if len(rows) == 0 or rows[0][0] is None:
        return jsonify([])  # Return empty list if no rows are found or if the first row's floor value is null
    floors = [row[0] for row in rows]  # Extract the floor values from the result rows
    floors = [floor.strip() for floor in floors if floor is not None]  # Remove whitespace and None values
    return jsonify(floors)



@app.route('/add_review_query', methods=['POST'])
def add_review_query():
    username = session.get('username')
    user_id = session.get('user_id')
    if username is None:
        login_error_message = "Please Log In To Continue or"
        return render_template("login.html", login_error_message=login_error_message)
    else:
        data = []
        fields = ['bathroom', 'body', 'rating']
        for field in fields:
            value = request.form.get(field)
            if value:
                data.append(value)
            else:
                data.append(None)
        data.append(user_id)
        try:
            add_review_string = '''INSERT INTO review(br_id, body, rating, user_id) 
               					  VALUES (:br_id, :body, :rating, :user_id)
               				   '''
            g.conn.execute(text(add_review_string), {'br_id': data[0], 'body': data[1], 'rating': data[2], 'user_id': data[3],})
            g.conn.commit()
            find_context["success_message"] = "Success! Review posted."
            return redirect(url_for('add_review'))
        except Exception as e:
            find_context["query_error_message"] = f"Error posting review: {str(e)}"
            return redirect(url_for('add_review'))
            #return render_template('add.html', query_error_message=query_error_message)
    
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
#followed this tutorial for cascading dropdown https://www.youtube.com/watch?v=jIAPewyzrp0
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
        fields = ['building', 'floor', 'gender']
        for field in fields:
            value = request.form.get(field)
            if value:
                data.append(value)
            else:
                data.append(None)
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
        WHERE (building_id = COALESCE(:building, building_id)) 
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
        if bname_result:
             bname = bname_result[0]
        else:
             bname = "Database"
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
    fields = ['uname', 'password', 'gender','class_year','favorite_br','home_br']
    for field in fields:
        value = request.form.get(field)
        if value:
            data.append(value)
        else:
            data.append(None)
    try:
        g.conn.execute(text('INSERT INTO users(uname, password, gender, class_year, favorite_br, home_br) VALUES (:uname, :password, :gender, :class_year, :favorite_br, :home_br)'), {'uname': data[0], 'password': data[1], 'gender': data[2], 'class_year': data[3], 'favorite_br': data[4], 'home_br': data[5]})
        g.conn.commit()
        success_message = "Account Created! Welcome "+data[0]+"! Please login to continue."
        return render_template("login.html",success_message=success_message)
    except Exception as e:
        error_str = str(e)
        if "duplicate key value violates unique constraint \"idx_users_uname_upper\"" in error_str:
             error_str = "User with that username already exists"
        register_error_message = "Error Registering: "+error_str
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
        #print(query_error_message)
        return render_template('index.html', query_error_message=query_error_message)


if __name__ == "__main__":
    import click
    @click.command()
    @click.option('--debug', is_flag=False)
    @click.option('--threaded', is_flag=True)
    @click.argument('HOST', default='0.0.0.0')
    @click.argument('PORT', default=8111, type=int)
    def run(debug, threaded, host, port):
        HOST, PORT = host, port
        app.run(host=HOST, port=PORT, debug=False, threaded=threaded)
        print("")
        print("\033[32m_______________________________________")
        print("|                                     |")
        print("\033[32m|            SERVER CLOSED            |")
        print("|             SUCCESSFULLY            |")
        print("|_____________________________________|\033[37m")
        print("")
    run()
   


run(debug=False)

