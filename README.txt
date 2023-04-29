Project Title: Columbia University Bathroom Database 
Authors: Drew Neff & Ashton Reimer
Date Last Modified: April 29th, 2023

Project Description: 

This project builds and populates a database of all bathrooms on Columbia's campus. The database stores meaningful data such as building, floor, handicap accessibility, and gender inclusivity, as well as more superfluous data such as the number of stalls, sinks, and visits from active database users. Bathrooms are located by building and are easily searchable so that users can find bathrooms when in need, in addition to seeking out obscure bathrooms to review or verify for our database.

Our ER diagram includes three strong entities (Building, Bathroom, and User), one weak entity (Review), and two additional overlapping specializations of Bathroom (Residential and Unconfirmed). There are also nine relationships that we integrate into our design.

Initially, we populated the database by physically walking through a few buildings on campus and making note of each bathroom and all of its attributes. Once we confirmed our database functioned with a small amount of data, we imported bathroom data we obtained from the CU Service Request Homepage (for a select number of buildings on campus). We know this method does not always provide us with data for all of the attributes, so we allow some attributes to be NULL or populate the database with fake data if necessary. In the long run, users can submit their own new bathrooms, which are stored as an Unconfirmed specialization of bathroom until a threshold of confirmations is reached through additional user verification.

We implemented a Web Front-End Interface using Flask and Jinja for part three, which allows users to interact with the database on a UI that lets them submit reviews for bathrooms they have visited as well as interact with other user reviews by rating them or setting their own home bathrooms for others to rate. Our interface specifies a difference in access for regular users and administrators. Users can only create and rate reviews, suggest new bathrooms, and set their home bathroom. Administrators have the ability to delete reviews as well as read and write access to all data in the database in addition to basic functionalities. Our interface has a leaderboard, which automatically queries and displays both users and bathrooms ranked by some of their attributes or other qualities we have yet to determine. We also implement a button that returns to the user a randomized bathroom that the user has never visited within constraints of whether the bathroom is accessible for the user.

Getting Started with the Web UI:

To run this program you must have Python 3.0 installed on your machine. 

1. Clone this repository to your local machine
2. Ensure the proper dependencies have been installed using "pip install sqlalchemy flask psycopg2-binary"
2. Navigate to src/Web_src and execute the command "Python3 server.py" 
3. Open a browser and navigate to localhost:8111
4. Close server connection with Ctrl-C once finished


NOTE: There is no guarantee of the persistence of the POSTGRESQL database beyond August 01 2023, however SQL table and trigger construction schema is provided in src/SQL_src 
