Drew Neff, djn2119
Ashton Reimer, asr2221
Server database found under djn2119 in database 1 @34.148.107.47

We added a text attribute, an array, and new triggers. 

In order to introduce a new text attribute (we had already used text across two of our tables), we added is a new table called 'building_review' to hold reviews of different buildings on campus, we already had this functionality for bathrooms but we thought buildings were another item of interest to be reviewed. Building reviews are more relevent for text searches because buildings vary in uses so heavily that searching up terms in reviews could provide users good information for wht buildings to go to for future bathroom visits.

Second we addded an array of :

Below is an example query to find all builings names and the text of the reviews that say big. This could be relevent so a user can find a building with many potential bathrooms:

SELECT bname, body FROM building b, building_review r WHERE b.building_id = r.building_id AND to_tsvector(body) @@ to_tsquery('big');


