Drew Neff, djn2119
Ashton Reimer, asr2221
Server database found under djn2119 in database 1 @34.148.107.47

We added a text attribute, an array, and new triggers. 

1.

In order to introduce a new text attribute (we had already used text across two of our tables), we added is a new table called 'building_review' to hold reviews of different buildings on campus. We already had this functionality for bathrooms but we thought buildings were another item of interest to be reviewed. Building reviews are more relevent for text searches because buildings vary in uses so heavily that searching up terms in reviews could provide users good information for what buildings to visit in the future. 

2.

We also had already implemented the array type in our previous schema to record the floors present in each building. In order to meet the new criteria, we added a new attribute to the 'building' table called 'br_arr'. This attribute is an array of integers that contains the unique set of bathroom ids (br_id) for every bathroom in the building. This new array type is helpful for keeping track of which bathrooms are present in which building without needing to scan through every row of the bathroom table. Although our database is small enough for every query to be processed in negligible time, the br_arr could allow a more efficient return of all bathrooms in a particular building should the bathroom table become inordinately large. 

3.

Since we had already implemented multiple triggers acting on a few different tables, the last modification we made to the database was to implement what is effectively one new trigger (technically three but each is almost identical). The function called by this trigger, 'update_building_array_and_cntf', sets the br_arr attribute of a building to an array containing the br_ids of every bathroom in that building. Additioinally, the function sets the building attribute 'num_br' to the length of the resulting array which will properly increment or decrement the number of bathrooms for insert and delete operations respectively. 

The function begins by creating an array of integers as a temporary variable. It then selects all of the bathroom ids from the desired building, aggregates them into an array using the array_agg() function, and sets the temporary variable equal to that array. The function then updates the respective row of the building table by setting br_arr to the temp variable and num_br to the length of the temp variable. 

This function is called by the 'update_building_arr_and_cnt' trigger which is triggered on any insert, update, or delete on the bathroom table. We also reasoned that the two child tables of bathroom, 'unconfirmed' and 'residence', should also be able to call the function. Therefore, we added two more triggers that are linked to insert, delete, and update on those respective tables. 

For example, if a user adds a table to the building with a building_id equal to 1 (Butler Library), that insert operation calls the trigger which will add the bathroom id (br_id) of that new bathroom to the br_arr value of Butler Library. Likewise, if a user deletes a bathroom from the table, that bathroom id will be removed from the array for the respective building. 

QUERIES: 

Here is an example query to find all builings names and the text of the reviews that say big. This could be relevent so a user can find a building with many potential bathrooms:

SELECT bname AS "Building Name", body AS "Review" 
FROM building b, building_review r 
WHERE b.building_id = r.building_id AND to_tsvector(body) @@ to_tsquery('big');

Here is an example query that finds and returns all the bathrooms in Butler (b.building_id = 1). If we assume (for hilarity) that our bathroom table has 10^10 rows, this query is helpful to a user who is in Butler Library and needs to find a bathroom immediately because scanning through the entire table could take hours in the worst case and they CAN'T hold it that long. Instead, by using the br_arr attribute, the relevant bathrooms are more easily available and the information can be returned. 

SELECT floor AS "Floor", br_description AS "Description", gender AS "Gender", 
       CASE WHEN single_use = true THEN 'yes' WHEN single_use = false THEN 'no' END AS "Single Use?"
FROM building b JOIN bathroom br ON b.building_id = br.building_id
WHERE br_id = ANY (br_arr) AND b.building_id = 1
ORDER BY floor;

