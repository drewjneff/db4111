CREATE TABLE building (
    building_id SERIAL,
    bname VARCHAR(20) NOT NULL,
    campus VARCHAR(20) NOT NULL,
    floors VARCHAR(10)[] NOT NULL,
    hour_open TIME,
    hour_closed TIME,
    num_floors INTEGER DEFAULT NULL,
    br_arr INTEGER[], 
    num_br INTEGER DEFAULT 0, 
    PRIMARY KEY (building_id)
);  


CREATE TABLE bathroom (
    br_id SERIAL PRIMARY KEY,
    building_id INTEGER NOT NULL REFERENCES building(building_id) ON DELETE CASCADE,
    floor VARCHAR(10) NOT NULL,
    br_description VARCHAR(20), 
    lat DOUBLE PRECISION,
    long DOUBLE PRECISION,
    elevation DOUBLE PRECISION,
    num_toilet INTEGER,
    num_sink INTEGER,
    num_urinal INTEGER,
    single_use BOOLEAN,
    handicap BOOLEAN,
    gender VARCHAR(8),
    CHECK (num_toilet > 0),
    CHECK (num_sink > 0),
    CHECK (num_urinal >= 0),
    CHECK (gender IN ('male','female','co-ed'))
);

CREATE TABLE residence ( 
num_shower INTEGER,
privacy BOOLEAN NOT NULL, 
visibility BOOLEAN NOT NULL,
CHECK (num_shower >= 0)
) INHERITS (bathroom);

CREATE TABLE unconfirmed (
    num_confirmations INTEGER DEFAULT 0,
    creator INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    num_shower INTEGER,
    privacy BOOLEAN,
    visibility BOOLEAN DEFAULT false, 
    PRIMARY KEY (br_id),
    CHECK (num_shower >= 0)
) INHERITS (bathroom);

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    gender VARCHAR(8),
    uname VARCHAR(20) UNIQUE NOT NULL,
    password VARCHAR(20) NOT NULL DEFAULT 'password',
    class_year INTEGER,
    favorite_br REFERENCES bathroom(br_id) ON DELETE NULL,
    home_br REFERENCES bathroom(br_id) ON DELETE NULL,
    num_visits INTEGER DEFAULT 0,
    num_br_visited INTEGER DEFAULT 0,
    CHECK (class_year >= 2023)
);


CREATE TABLE review ( 
rnumber SERIAL NOT NULL PRIMARY KEY,
br_id INTEGER NOT NULL REFERENCES bathroom(br_id) ON DELETE CASCADE,
user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
body TEXT,
rating INTEGER NOT NULL,
review_date DATE DEFAULT CURRENT_DATE,
CHECK (rating >= 0),
CHECK (rating <=5)
);


CREATE TABLE comment ( 
commenter INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
reviewer INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
br_id INTEGER NOT NULL REFERENCES bathroom(br_id) ON DELETE CASCADE,
rnumber INTEGER NOT NULL REFERENCES review(rnumber) ON DELETE CASCADE, 
comment_txt TEXT NOT NULL,
PRIMARY KEY (commenter, reviewer, br_id, rnumber)
);

CREATE TABLE rating ( 
rater INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
ratee INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
br_id INTEGER NOT NULL REFERENCES bathroom(br_id) ON DELETE CASCADE, 
rnumber INTEGER NOT NULL REFERENCES review(rnumber) ON DELETE CASCADE,
rating BOOLEAN NOT NULL,
PRIMARY KEY (rater, ratee, br_id, rnumber)
);

CREATE TABLE affirmation (
br_id INTEGER NOT NULL REFERENCES unconfirmed(br_id) ON DELETE CASCADE,
user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
valid_br boolean NOT NULL,
PRIMARY KEY (br_id, user_id)
);


CREATE TABLE building_review (
rnumber SERIAL NOT NULL PRIMARY KEY,
building_id INTEGER NOT NULL REFERENCES building(building_id) ON DELETE CASCADE,
user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
body TEXT,
rating INTEGER NOT NULL,
review_date DATE DEFAULT CURRENT_DATE,
CHECK (rating >= 0),
CHECK (rating <= 5));