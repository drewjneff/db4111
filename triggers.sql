/* 
    BUILDING TRIGGERS 
*/

CREATE FUNCTION set_Num_floorsf() RETURNS TRIGGER AS $$
BEGIN
    NEW.num_floors = array_length(NEW.floors,1);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER set_num_floors
BEFORE INSERT OR UPDATE ON building
FOR EACH ROW EXECUTE FUNCTION set_num_floorsf();


/*
    BATHROOM TRIGGERS 
*/



CREATE FUNCTION check_floor_existsf() RETURNS TRIGGER AS $$
BEGIN
    IF NOT EXISTS (
        SELECT *
        FROM building
        WHERE NEW.building_id = building.building_id AND NEW.floor = ANY(building.floors)
    ) THEN RAISE EXCEPTION 'Cannot add bathroom to floor that does not exist';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;



CREATE TRIGGER check_floor_exists
BEFORE INSERT OR UPDATE ON bathroom
FOR EACH ROW 
EXECUTE FUNCTION check_floor_existsf();


/*
NEW BATHROOM TRIGGER
*/

CREATE FUNCTION update_building_array_and_cntf() RETURNS TRIGGER AS $$
DECLARE
    br_ids INTEGER[];
BEGIN
    SELECT array_agg(br_id) INTO br_ids FROM bathroom WHERE building_id = NEW.building_id;
    UPDATE building 
    SET br_arr = br_ids,
        num_br = array_length(br_ids, 1)
    WHERE building_id = NEW.building_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_building_arr_and_cnt
BEFORE INSERT OR UPDATE OR DELETE ON bathroom
FOR EACH ROW 
EXECUTE FUNCTION update_building_array_and_cntf();

CREATE TRIGGER update_building_arr_and_cnt_unconfirmed
BEFORE INSERT OR UPDATE OR DELETE ON unconfirmed
FOR EACH ROW 
EXECUTE FUNCTION update_building_array_and_cntf();

CREATE TRIGGER update_building_arr_and_cnt_residence
BEFORE INSERT OR UPDATE OR DELETE ON residence
FOR EACH ROW 
EXECUTE FUNCTION update_building_array_and_cntf();




/*
DELETED FUNCTIONS AND TRIGGERS FROM BATHROOM
*/

CREATE TRIGGER increment_num_br
AFTER INSERT ON bathroom
FOR EACH ROW 
EXECUTE FUNCTION increment_num_brf();

CREATE TRIGGER decrement_num_br
AFTER DELETE ON bathroom
FOR EACH ROW 
EXECUTE FUNCTION decrement_num_brf();

CREATE FUNCTION increment_num_brf() RETURNS TRIGGER AS $$
BEGIN
    UPDATE building 
    SET num_br = num_br + 1 
    WHERE building.building_id = NEW.building_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE FUNCTION decrement_num_brf() RETURNS TRIGGER AS $$
BEGIN
    UPDATE building 
    SET num_br = num_br - 1 
    WHERE building.building_id = OLD.building_id;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;









/* 
    Review TRIGGERS 
*/ 

CREATE FUNCTION update_user_stats_on_insertupdatef() RETURNS TRIGGER AS $$
BEGIN
    UPDATE users 
    SET num_visits = (
        SELECT COUNT(br_id)
        FROM review NATURAL JOIN users
        WHERE (NEW.user_id ) = (users.user_id)
        )
    WHERE NEW.user_id = users.user_id; 

    UPDATE users 
    SET num_br_visited = (
        SELECT COUNT(DISTINCT br_id)
        FROM review NATURAL JOIN users
        WHERE (NEW.user_id) = (users.user_id)
    )
    WHERE NEW.user_id = users.user_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE FUNCTION update_user_stats_on_deletef() RETURNS TRIGGER AS $$
BEGIN
    UPDATE users 
    SET num_visits = (
        SELECT COUNT(br_id)
        FROM review NATURAL JOIN users
        WHERE (OLD.user_id ) = (users.user_id)
        )
    WHERE OLD.user_id = users.user_id; 

    UPDATE users 
    SET num_br_visited = (
        SELECT COUNT(DISTINCT br_id)
        FROM review NATURAL JOIN users
        WHERE (OLD.user_id) = (users.user_id)
    )
    WHERE OLD.user_id = users.user_id;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER update_user_stats_on_insertupdate
AFTER INSERT OR UPDATE ON review
FOR EACH ROW
EXECUTE FUNCTION update_user_stats_on_insertupdatef(); 

CREATE TRIGGER update_user_stats_on_delete
AFTER DELETE ON review
FOR EACH ROW
EXECUTE FUNCTION update_user_stats_on_deletef(); 



/* 
    Affirmation triggers
*/

CREATE FUNCTION update_confirmation_on_insertf() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.valid_br = true THEN
        UPDATE unconfirmed
        SET num_confirmations = num_confirmations + 1 
        WHERE (NEW.br_id)=(unconfirmed.br_id);
    END IF; 
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE FUNCTION update_confirmation_on_deletef() RETURNS TRIGGER AS $$
BEGIN
    IF OLD.valid_br = true THEN
        UPDATE unconfirmed
        SET num_confirmations = num_confirmations - 1 
        WHERE (OLD.br_id)=(unconfirmed.br_id);
    END IF; 
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_confirmation_on_insert
AFTER INSERT ON affirmation
FOR EACH ROW 
EXECUTE FUNCTION update_confirmation_on_insertf();

CREATE TRIGGER update_confirmation_on_delete
AFTER DELETE ON affirmation
FOR EACH ROW 
EXECUTE FUNCTION update_confirmation_on_deletef();


CREATE FUNCTION check_not_creatorf() RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT *
        FROM unconfirmed
        WHERE NEW.user_id = unconfirmed.creator AND NEW.br_id = unconfirmed.br_id 
    ) THEN RAISE EXCEPTION 'Cannot affirm existence of bathroom reported on user''s own';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER check_not_creator 
BEFORE INSERT ON affirmation
FOR EACH ROW 
EXECUTE FUNCTION check_not_creatorf();