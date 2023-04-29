Project Part 2
Ashton Reimer and Drew Neff
asr2221 and djn2119

Database is found under djn2119 at 34.148.107.47


Three Queries


1. 

SELECT uname, num_br_visited
FROM users WHERE num_br_visited >= 1
ORDER BY num_br_visited DESC LIMIT 10;

Returns table of top 10 users ranked by bathrooms visited, our leaderboard. We want to incentivize
bathroom visits and reviews so we would display this to all users. Currently only 4 users with bathrooms
visited in our data.


2.

SELECT b.br_id AS "Bathroom ID", b.building_id AS "Building ID", b.floor AS "floor", b.br_description AS
"Bathroom Description", AVG(r.rating) AS "Average Rating"
FROM bathroom b NATURAL JOIN review r NATURAL JOIN building c
WHERE c.bname = 'Butler Library' AND b.floor = '6th' AND b.gender = 'female'
GROUP BY b.br_id, b.building_id, b.floor, b.br_description
HAVING AVG(r.rating) > 4;

Returns table of female bathrooms on the 6th floor of butler with average review of higher than 4. This is
the main functionality of our system in which users can easily find bathrooms meeting a variety of
constraints. In our limited data 1 bathroom meets these constraints but others meet subsets of these
constraints.


3.
SELECT v.uname AS "Username", c.comment_txt AS "Comment"
FROM users u, users v, comment c
WHERE u.user_id = c.reviewer AND v.user_id = c.commenter AND u.uname = 'ashton';

Returns the username and comment text of all comments made on reviews made by user ashton. This
would allow users to see who has been commenting on their reviews.
