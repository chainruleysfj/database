CREATE INDEX idx_name_city ON movie_app_productioncompany (name, city);

CREATE INDEX idx_moviename ON movie_app_movie (moviename);

CREATE INDEX idx_production_company_id ON movie_app_movie (production_company_id);

CREATE INDEX idx_movie_length ON movie_app_movie(length);

CREATE INDEX idx_movie_releaseyear ON movie_app_movie(releaseyear);

CREATE fulltext index idx_movie_plot_summary ON movie_app_movie(plot_summary);

CREATE INDEX idx_person_name ON movie_app_person (name);

CREATE UNIQUE INDEX  idx_genre_name ON movie_app_MovieGenre (genre_name);

CREATE INDEX  idx_movie_id_genre_association ON movie_app_MovieGenreAssociation (Movie_ID);

CREATE INDEX  idx_genre_id_genre_association ON movie_app_MovieGenreAssociation (Genre_ID);

DROP PROCEDURE IF EXISTS add_productioncompany;
DELIMITER $$
CREATE PROCEDURE add_productioncompany(IN p_name VARCHAR(50), IN p_city VARCHAR(50), IN p_description TEXT)
BEGIN
    INSERT INTO movie_app_productioncompany (name, city, company_description)
    VALUES (p_name, p_city, p_description);
END$$
DELIMITER ;

DROP PROCEDURE IF EXISTS get_all_production_companies;
DELIMITER $$
CREATE PROCEDURE get_all_production_companies()
BEGIN
    SELECT company_id, name, city, company_description FROM movie_app_productioncompany ORDER BY name, city;
END$$
DELIMITER ;

DROP PROCEDURE IF EXISTS get_company_by_id;
DELIMITER //
CREATE PROCEDURE get_company_by_id(
    IN p_company_id INT
)
BEGIN
    SELECT * FROM movie_app_productioncompany WHERE company_id = p_company_id;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS update_production_company;
DELIMITER $$
CREATE PROCEDURE update_production_company(
    IN p_id INT,
    IN p_name VARCHAR(50),
    IN p_city VARCHAR(50),
    IN p_description TEXT
)
BEGIN
    UPDATE movie_app_productioncompany
    SET name = p_name, city = p_city, company_description = p_description
    WHERE company_id = p_id;
END$$
DELIMITER ;

DROP PROCEDURE IF EXISTS delete_production_company;
DELIMITER $$
CREATE PROCEDURE delete_production_company(IN p_company_id INT)
BEGIN
    DELETE FROM movie_app_productioncompany WHERE company_id = p_company_id;
END$$
DELIMITER ;

DROP PROCEDURE IF EXISTS search_production_companies;
DELIMITER //
CREATE PROCEDURE search_production_companies(
    IN search_name VARCHAR(255),
    IN search_city VARCHAR(255)
)
BEGIN
    SELECT company_id, name, city, company_description
    FROM movie_app_productioncompany
    WHERE (name LIKE CONCAT('%', search_name, '%') OR search_name = '')
      AND (city LIKE CONCAT('%', search_city, '%') OR search_city = '')
	ORDER BY name, city;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS add_movie;
DELIMITER //
CREATE PROCEDURE add_movie(
    IN p_moviename VARCHAR(100),
    IN p_length SMALLINT,
    IN p_releaseyear INT,
    IN p_plot_summary TEXT,
    IN p_resource_link VARCHAR(100),
    IN p_production_company_id INT
)
BEGIN
    INSERT INTO movie_app_movie (moviename, length, releaseyear, plot_summary, resource_link, production_company_id)
    VALUES (p_moviename, p_length, p_releaseyear, p_plot_summary, p_resource_link, p_production_company_id);
END //
DELIMITER ;




DROP PROCEDURE IF EXISTS get_movie_detail;
DELIMITER //

CREATE PROCEDURE get_movie_detail(IN p_movie_id INT)
BEGIN
    -- Declare variables to store concatenated results
    DECLARE actors_list TEXT DEFAULT '';
    DECLARE directors_list TEXT DEFAULT '';
    DECLARE genres_list TEXT DEFAULT '';
    DECLARE narration_list TEXT DEFAULT '';
    
    -- Retrieve movie details
    SELECT
        m.movie_id,
        m.moviename,
        m.length,
        m.releaseyear,
        m.plot_summary,
        m.resource_link,
        pc.name AS production_company_name
    INTO
        @movie_id,
        @moviename,
        @length,
        @releaseyear,
        @plot_summary,
        @resource_link,
        @production_company_name
    FROM
        movie_app_movie m
    JOIN
        movie_app_productioncompany pc ON m.production_company_id = pc.company_id
    WHERE
        m.movie_id = p_movie_id;

    -- Get actors list with their roles (including those who narrated)
    SELECT GROUP_CONCAT(CONCAT(p.name, ':', r.role_name) SEPARATOR '; ')
    INTO actors_list
    FROM movie_app_person p
    JOIN movie_app_roleactormovie pm ON p.personID = pm.person_id
    JOIN movie_app_role r ON pm.role_id = r.role_id
    WHERE pm.movie_id = p_movie_id;
    
    -- Include narration actors in the actors list
    SELECT GROUP_CONCAT(CONCAT(p.name, ' (Narrator)') SEPARATOR '; ')
    INTO narration_list
    FROM movie_app_person p
    JOIN movie_app_narration nr ON p.personID = nr.actor_id
    WHERE nr.movie_id = p_movie_id;

    IF narration_list IS NOT NULL THEN
        SET actors_list = CONCAT(actors_list, '; ', narration_list);
    END IF;

    -- Retrieve directors
    SELECT GROUP_CONCAT(p.name SEPARATOR '; ')
    INTO directors_list
    FROM movie_app_person p
    JOIN movie_app_directormovie dm ON p.personID = dm.person_id
    WHERE dm.movie_id = p_movie_id;

    -- Retrieve genres
    SELECT GROUP_CONCAT(g.genre_name SEPARATOR '; ')
    INTO genres_list
    FROM movie_app_moviegenre g
    JOIN movie_app_moviegenreassociation ga ON g.genre_id = ga.genre_id
    WHERE ga.movie_id = p_movie_id;

    -- Retrieve narration content (if any)
    SELECT GROUP_CONCAT(CONCAT(p.name, ' - ', nr.content) SEPARATOR '; ')
    INTO narration_list
    FROM movie_app_person p
    JOIN movie_app_narration nr ON p.personID = nr.actor_id
    WHERE nr.movie_id = p_movie_id;

    -- Return the movie details along with actors, directors, genres, and narration
    SELECT
        @movie_id AS movie_id,
        @moviename AS moviename,
        @length AS length,
        @releaseyear AS releaseyear,
        @plot_summary AS plot_summary,
        @resource_link AS resource_link,
        @production_company_name AS production_company_name,
        actors_list AS actors,
        directors_list AS directors,
        genres_list AS genres,
        narration_list AS narration;
END //

DELIMITER ;


DROP PROCEDURE IF EXISTS update_movie;
DELIMITER //
CREATE PROCEDURE update_movie(
    IN p_movie_id INT,
    IN p_moviename VARCHAR(100),
    IN p_length SMALLINT,
    IN p_releaseyear INT,
    IN p_plot_summary TEXT,
    IN p_resource_link VARCHAR(255),
    IN p_production_company_id INT
)
BEGIN
    -- 更新电影信息
    UPDATE movie_app_movie
    SET
        moviename = p_moviename,
        length = p_length,
        releaseyear = p_releaseyear,
        plot_summary = p_plot_summary,
        resource_link = p_resource_link,
        production_company_id = p_production_company_id
    WHERE
        movie_id = p_movie_id;
        
END //
DELIMITER ;




DROP PROCEDURE IF EXISTS add_person;
DELIMITER //
CREATE PROCEDURE add_person(
    IN p_name VARCHAR(50),
    IN p_birth_date DATE,
    IN p_gender ENUM('M', 'F', 'U'),
    IN p_marital_status ENUM('S', 'M', 'W', 'U')
)
BEGIN
    INSERT INTO movie_app_person (Name, birth_date, Gender, marital_status)
    VALUES (p_name, p_birth_date, p_gender, p_marital_status);
END //
DELIMITER ;

DELIMITER //

DROP PROCEDURE IF EXISTS get_all_persons;
CREATE PROCEDURE get_all_persons()
BEGIN
    SELECT personID, Name, birth_date, Gender,  marital_status
    FROM movie_app_person;
END //
DELIMITER ;


DROP PROCEDURE IF EXISTS update_person;
DELIMITER //
CREATE PROCEDURE update_person(
    IN p_person_id INT,
    IN p_name VARCHAR(100),
    IN p_birth_date DATE,
    IN p_gender ENUM('M','F','U'),
    IN p_marital_status ENUM('S','M','W','U')
)
BEGIN
    UPDATE movie_app_person
    SET Name = p_name,
        birth_date = p_birth_date,
        Gender = p_gender,
        marital_status = p_marital_status
    WHERE personID = p_person_id;
END //
DELIMITER ;


DROP PROCEDURE IF EXISTS search_persons;
DELIMITER //
CREATE PROCEDURE search_persons(
    IN p_name VARCHAR(100),
    IN p_start_birth_date DATE,
    IN p_end_birth_date DATE,
    IN p_gender ENUM('M','F','U'),
    IN p_marital_status ENUM('S','M','W','U')
)
BEGIN
    SELECT personID, Name, birth_date, Gender, marital_status
    FROM movie_app_person
    WHERE (p_name IS NULL OR p_name = '' OR Name LIKE CONCAT('%', p_name, '%'))
    AND (p_start_birth_date IS NULL OR birth_date >= p_start_birth_date)
    AND (p_end_birth_date IS NULL OR birth_date <= p_end_birth_date)
    AND (p_gender IS NULL OR p_gender = '' OR Gender = p_gender)
    AND (p_marital_status IS NULL OR p_marital_status = '' OR marital_status = p_marital_status);
END //
DELIMITER ;



DROP PROCEDURE IF EXISTS add_director_movie;
DELIMITER //
CREATE PROCEDURE add_director_movie(
    IN p_movie_id INT,
    IN p_person_id INT
)
BEGIN
    INSERT INTO movie_app_directormovie (movie_ID, person_ID)
    VALUES (p_movie_id, p_person_id);
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS get_all_movies;
DELIMITER //
CREATE PROCEDURE get_all_movies()
BEGIN
    SELECT m.Movie_ID, m.moviename, m.length, m.releaseyear, m.plot_summary, m.resource_link, pc.name AS production_company_name,
           GROUP_CONCAT(p.name) AS directors
    FROM movie_app_movie m
    LEFT JOIN movie_app_directormovie dm ON m.Movie_ID = dm.Movie_ID
    LEFT JOIN movie_app_person p ON dm.person_ID = p.personID
    LEFT JOIN movie_app_productioncompany pc ON m.production_company_id = pc.company_id
    GROUP BY m.Movie_ID;
END //
DELIMITER ;


DROP PROCEDURE IF EXISTS get_last_insert_movie_id;
DELIMITER //
CREATE PROCEDURE get_last_insert_movie_id()
BEGIN
    SELECT LAST_INSERT_ID() AS movie_id;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS search_person_by_name;
DELIMITER //
CREATE PROCEDURE search_person_by_name(
    IN p_name VARCHAR(100)
)
BEGIN
    SELECT personID, name 
    FROM movie_app_person 
    WHERE name LIKE CONCAT('%', p_name, '%');
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS delete_directors_for_movie;
DELIMITER //
CREATE PROCEDURE delete_directors_for_movie(
    IN p_movie_id INT
)
BEGIN
    DELETE FROM movie_app_directormovie WHERE movie_ID = p_movie_id;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS get_directors_for_movie;
DELIMITER //  
CREATE PROCEDURE get_directors_for_movie(IN p_movie_id INT)  
BEGIN  
    SELECT p.personID, p.name   
    FROM movie_app_directormovie dm  
    JOIN movie_app_person p ON dm.person_id = p.personID  
    WHERE dm.movie_id = p_movie_id;  
END //  
DELIMITER ;



DROP PROCEDURE IF EXISTS get_all_directors_and_directmovie;
DELIMITER //
CREATE PROCEDURE get_all_directors_and_directmovie()
BEGIN
    SELECT p.personID, p.name AS director, 
           GROUP_CONCAT(CONCAT(m.Movie_ID, ':', m.moviename) SEPARATOR ', ') AS movies
    FROM movie_app_directormovie dm
    LEFT JOIN movie_app_movie m ON m.Movie_ID = dm.Movie_ID
    LEFT JOIN movie_app_person p ON dm.person_ID = p.personID
    GROUP BY p.personID;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS delete_person;
DELIMITER //
CREATE PROCEDURE delete_person(
    IN p_person_id INT
)
BEGIN
	DELETE FROM movie_app_directormovie dm WHERE dm.person_ID = p_person_id;
    DELETE FROM movie_app_person WHERE personID = p_person_id;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS select_all_genre;
DELIMITER //
CREATE PROCEDURE select_all_genre()
BEGIN
    SELECT * FROM movie_app_MovieGenre;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS add_movie_genre;
DELIMITER //
CREATE PROCEDURE add_movie_genre(IN p_genre_name VARCHAR(10))
BEGIN
    INSERT INTO movie_app_MovieGenre (genre_name) VALUES (p_genre_name);
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS delete_movie_genre;
DELIMITER //
CREATE PROCEDURE delete_movie_genre(IN p_genre_id SMALLINT UNSIGNED)
BEGIN
	DELETE FROM movie_app_MovieGenreAssociation WHERE Genre_ID = p_genre_id;
    DELETE FROM movie_app_MovieGenre WHERE genre_id = p_genre_id;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS add_movie_genre_association;
DELIMITER //
CREATE PROCEDURE add_movie_genre_association(IN p_movie_id INT, IN p_genre_id SMALLINT UNSIGNED)
BEGIN
    INSERT INTO movie_app_MovieGenreAssociation (Movie_ID, Genre_ID) VALUES (p_movie_id, p_genre_id);
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS delete_movie_genre_association;
DELIMITER //
CREATE PROCEDURE delete_movie_genre_association(IN p_movie_id INT, IN p_genre_id SMALLINT UNSIGNED)
BEGIN
    DELETE FROM movie_app_MovieGenreAssociation WHERE Movie_ID = p_movie_id AND Genre_ID = p_genre_id;
END //
DELIMITER ;




DROP PROCEDURE IF EXISTS get_movie_genre_association;
DELIMITER //
CREATE PROCEDURE get_movie_genre_association(IN p_movie_id INT)
BEGIN
    SELECT genre_id FROM movie_app_MovieGenreAssociation WHERE Movie_ID = p_movie_id ;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS delete_movie;
DELIMITER //
CREATE PROCEDURE delete_movie(IN p_movie_id INT)
BEGIN
	DELETE FROM movie_app_MovieGenreAssociation mga WHERE mga.movie_id = p_movie_id;
	DELETE FROM movie_app_directormovie dm WHERE dm.movie_id = p_movie_id;
    DELETE FROM movie_app_comment mc WHERE mc.movie_id = p_movie_id;
    DELETE FROM movie_app_rating mr WHERE mr.movie_id = p_movie_id;
    DELETE FROM movie_app_roleactormovie ram WHERE ram.movie_id = p_movie_id;
    DELETE FROM movie_app_movie m WHERE m.movie_id = p_movie_id;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS get_movie_genre_association_with_name;
DELIMITER //
CREATE PROCEDURE get_movie_genre_association_with_name(IN p_movie_id INT)
BEGIN
    SELECT mg.genre_id , mg.genre_name 
    FROM movie_app_MovieGenreAssociation mga
    JOIN movie_app_moviegenre mg
    ON mga.genre_id = mg.genre_id
    WHERE mga.movie_ID = p_movie_id ;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS search_movies;
DELIMITER //
CREATE PROCEDURE search_movies(
    IN p_keyword VARCHAR(255),
    IN p_min_length INT,
    IN p_max_length INT,
    IN p_min_releaseyear INT,
    IN p_max_releaseyear INT,
    IN p_production_company_id INT,
    IN p_genre_id SMALLINT UNSIGNED
)
BEGIN
    SELECT m.Movie_ID, m.moviename, m.length, m.releaseyear, m.plot_summary, m.resource_link, pc.name AS production_company_name, 
           GROUP_CONCAT(DISTINCT p.name ORDER BY p.name SEPARATOR ', ') AS directors
    FROM movie_app_movie m
    LEFT JOIN movie_app_directormovie dm ON m.Movie_ID = dm.Movie_ID
    LEFT JOIN movie_app_person p ON dm.person_ID = p.personID
    LEFT JOIN movie_app_productioncompany pc ON m.production_company_id = pc.company_id
    LEFT JOIN movie_app_MovieGenreAssociation mga ON m.Movie_ID = mga.Movie_ID
    LEFT JOIN movie_app_MovieGenre mg ON mga.genre_id = mg.genre_id
    WHERE (p_keyword IS NULL OR m.moviename LIKE CONCAT('%', p_keyword, '%'))
      AND m.length BETWEEN p_min_length AND p_max_length
      AND (m.releaseyear BETWEEN p_min_releaseyear AND p_max_releaseyear or m.releaseyear is null)
      AND (p_production_company_id IS NULL OR m.production_company_id = p_production_company_id)
      AND (p_genre_id IS NULL OR mg.genre_id = p_genre_id)
    GROUP BY m.Movie_ID, m.moviename, m.length, m.releaseyear, m.plot_summary, m.resource_link, pc.name;
END //
DELIMITER ;


DROP PROCEDURE IF EXISTS get_movie_production_company;
DELIMITER //
CREATE PROCEDURE get_movie_production_company(IN p_movie_id INT)
BEGIN
    SELECT production_company_id
    FROM movie_app_movie
    WHERE movie_id = p_movie_id;
END //
DELIMITER ;


DROP PROCEDURE IF EXISTS get_movies_by_company;
DELIMITER //
CREATE PROCEDURE get_movies_by_company(IN p_company_id INT)
BEGIN
    SELECT movie_id FROM movie_app_movie WHERE production_company_id = p_company_id;
END //
DELIMITER ;

-- 创建存储过程来插入用户
DROP PROCEDURE IF EXISTS create_user_procedure;
DELIMITER //
CREATE PROCEDURE create_user_procedure(
    IN p_username VARCHAR(150),
    IN p_password VARCHAR(128)
)
BEGIN
    INSERT INTO auth_user (username, password,is_superuser,first_name,last_name,email, is_staff, is_active, date_joined)
    VALUES (p_username, p_password, FALSE, '', '','', FALSE, TRUE, NOW());
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS get_users_procedure;
DELIMITER //
CREATE PROCEDURE get_users_procedure(
    IN p_username VARCHAR(150)
)
BEGIN
    IF p_username IS NULL THEN
        SELECT id, username, is_staff, is_active, is_superuser
        FROM auth_user;
    ELSE
        SELECT id, username, is_staff, is_active, is_superuser
        FROM auth_user
        WHERE username LIKE CONCAT('%', p_username, '%');
    END IF;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS set_staff_status;
DELIMITER //
CREATE PROCEDURE set_staff_status(
    IN p_user_id INT,
    IN p_is_staff BOOLEAN
)
BEGIN
    UPDATE auth_user
    SET is_staff = p_is_staff
    WHERE id = p_user_id;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS change_staff_status;
DELIMITER //
CREATE PROCEDURE change_staff_status(
    IN p_user_id INT
)
BEGIN
    UPDATE auth_user
    SET is_staff = not is_staff
    WHERE id = p_user_id;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS delete_user;
DELIMITER //
CREATE PROCEDURE delete_user(
    IN p_user_id INT
)
BEGIN
	DELETE FROM movie_app_securityqa WHERE user_id = p_user_id;
    DELETE FROM movie_app_comment WHERE user_id = p_user_id;
    DELETE FROM movie_app_rating WHERE user_id = p_user_id;
    DELETE FROM movie_app_loginrecord WHERE user_id = p_user_id;
    DELETE FROM auth_user WHERE id = p_user_id;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS search_users;
DELIMITER //
CREATE PROCEDURE search_users(
    IN p_query VARCHAR(255)
)
BEGIN
    IF p_query IS NULL OR p_query = '' THEN
        SELECT * FROM auth_user;
    ELSE
        SELECT * FROM auth_user WHERE username LIKE CONCAT('%', p_query, '%');
    END IF;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS update_password_procedure;
DELIMITER //
CREATE PROCEDURE update_password_procedure(IN p_user_id INT, IN new_password VARCHAR(255))
BEGIN
    UPDATE auth_user SET password = new_password WHERE id = p_user_id;
    DELETE FROM movie_app_loginrecord WHERE user_id = p_user_id;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS set_security_question_proc;
DELIMITER $$
CREATE PROCEDURE set_security_question_proc(
    IN p_user_id INT,
    IN p_security_question VARCHAR(255),
    IN p_security_answer VARCHAR(255)
)
BEGIN
    DECLARE user_exists INT;
    -- Check if the user exists
    SELECT COUNT(*) INTO user_exists FROM auth_user WHERE id = p_user_id;
    
    IF user_exists = 1 THEN
        -- Update or insert into SecurityQA table
        INSERT INTO movie_app_securityqa (user_id, security_question, security_answer)
        VALUES (p_user_id, p_security_question, p_security_answer)
        ON DUPLICATE KEY UPDATE
        security_question = VALUES(security_question),
        security_answer = VALUES(security_answer);
    ELSE
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'User does not exist';
    END IF;
END$$
DELIMITER ;

DROP PROCEDURE IF EXISTS reset_password_proc;
DELIMITER $$
CREATE PROCEDURE reset_password_proc(
    IN p_username VARCHAR(150),
    IN p_security_answer VARCHAR(255),
    IN p_new_password VARCHAR(255),
    OUT p_success TINYINT(1),
    OUT p_message VARCHAR(255)
)
BEGIN
    DECLARE p_user_id INT;
    DECLARE answer_correct TINYINT(1);
    
    -- Check if the user exists
    SELECT id INTO p_user_id FROM auth_user WHERE username = p_username;
    IF p_user_id IS NULL THEN
        SET p_success = 0;
        SET p_message = 'User does not exist.';
    ELSE
        -- Check if the provided security answer matches the stored answer
        SELECT CASE WHEN LOWER(security_answer) = LOWER(p_security_answer) THEN 1 ELSE 0 END INTO answer_correct
        FROM movie_app_securityqa
        WHERE user_id = p_user_id;

        IF answer_correct = 1 THEN
            -- Update the user's password
            UPDATE auth_user SET password = p_new_password WHERE id = p_user_id;
            SET p_success = 1;
            SET p_message = 'Password reset successfully.';
			DELETE FROM movie_app_loginrecord WHERE user_id = p_user_id;
        ELSE
            SET p_success = 0;
            SET p_message = 'Incorrect security answer.';
        END IF;
    END IF;
    SELECT p_success AS success, p_message AS message;
END$$
DELIMITER ;

DROP PROCEDURE IF EXISTS get_security_question_proc;
DELIMITER $$
CREATE PROCEDURE get_security_question_proc(
    IN p_username VARCHAR(150),
    OUT p_security_question VARCHAR(255),
    OUT p_message VARCHAR(255)
)
BEGIN
    DECLARE p_user_id INT;
    -- Check if the user exists and get the user ID
    SELECT id INTO p_user_id FROM auth_user WHERE username = p_username;
    IF p_user_id IS NULL THEN
        SET p_security_question = NULL;
        SET p_message = 'User does not exist.';
    ELSE
        -- Get the security question for the user
        SELECT security_question INTO p_security_question 
        FROM movie_app_securityqa 
        WHERE user_id = p_user_id;
        
        IF p_security_question IS NULL THEN
            SET p_message = 'Security question not set for this user.';
        ELSE
            SET p_message = 'Success';
        END IF;
    END IF;
    SELECT p_security_question AS security_question, p_message AS message;
END$$
DELIMITER ;

DROP PROCEDURE IF EXISTS manage_login_record;
DELIMITER $$
CREATE PROCEDURE manage_login_record(
    IN p_user_id INT,
    IN p_session_key VARCHAR(100),
    IN p_action VARCHAR(10)
)
BEGIN
    -- Check if the user already has an active login record
    IF p_action = 'create' THEN
        -- Create a new login record
        INSERT INTO movie_app_loginrecord (user_id, session_key, login_time)
        VALUES (p_user_id, p_session_key, now());

    ELSEIF p_action = 'delete' THEN
        -- Delete the specific login record
        DELETE FROM movie_app_loginrecord
        WHERE user_id = p_user_id AND session_key = p_session_key;
    END IF;
END$$
DELIMITER ;

DROP PROCEDURE IF EXISTS get_active_login_records;
DELIMITER $$
CREATE PROCEDURE get_active_login_records(
    IN p_user_id INT
)
BEGIN
    SELECT COUNT(*) 
    FROM movie_app_loginrecord
    WHERE user_id = p_user_id;
END$$
DELIMITER ;

DROP PROCEDURE IF EXISTS get_user_activity;
DELIMITER //
CREATE PROCEDURE get_user_activity(IN user_id INT)
BEGIN
    -- Get Ratings
    SELECT 
        r.id,
        r.user_id,
        r.movie_id,
        m.moviename AS movie_name,
        r.rating
    FROM 
        movie_app_rating r
    JOIN 
        movie_app_movie m ON r.movie_id = m.movie_id
    WHERE 
        r.user_id = user_id;

    -- Get Comments
    SELECT 
        c.comment_id,
        c.user_id,
        c.movie_id,
        m.moviename AS movie_name,
        c.content,
        c.comment_time
    FROM 
        movie_app_comment c
    JOIN 
        movie_app_movie m ON c.movie_id = m.movie_id
    WHERE 
        c.user_id = user_id
    AND 
        c.is_approved = TRUE;
END //

DELIMITER ;

DROP PROCEDURE IF EXISTS get_movies_by_production_company;
DELIMITER $$

CREATE PROCEDURE get_movies_by_production_company(
    IN company_id INT
)
BEGIN
    SELECT 
        m.movie_id,
        m.moviename,
        m.length,
        m.releaseyear,
        COALESCE(AVG(r.rating), 0) AS average_rating
    FROM 
        movie_app_movie m
        LEFT JOIN movie_app_rating r ON m.movie_id = r.movie_id
    WHERE 
        m.production_company_id = company_id
    GROUP BY 
        m.movie_id, m.moviename, m.length, m.releaseyear;
END$$

DELIMITER ;

DROP PROCEDURE IF EXISTS get_all_actors;
DELIMITER //
CREATE PROCEDURE get_all_actors(IN actor_name VARCHAR(50))
BEGIN
    SELECT DISTINCT p.personID, p.name
    FROM movie_app_person p
    LEFT JOIN movie_app_roleactormovie am ON p.personID = am.person_id
    LEFT JOIN movie_app_narration nr ON p.personID = nr.actor_id
    WHERE (am.person_id IS NOT NULL OR nr.actor_id IS NOT NULL)
    AND (p.name LIKE CONCAT('%', actor_name, '%') OR actor_name IS NULL);
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS get_actor_movies;
DELIMITER //
CREATE PROCEDURE get_actor_movies(IN p_person_id INT)
BEGIN
    SELECT DISTINCT m.moviename
    FROM movie_app_movie m
    JOIN movie_app_roleactormovie ram ON m.movie_id = ram.movie_id
    WHERE ram.person_id = p_person_id
    UNION
    SELECT DISTINCT m.moviename
    FROM movie_app_movie m
    JOIN movie_app_narration nr ON m.movie_id = nr.movie_id
    WHERE nr.actor_id = p_person_id;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS get_actor_movies_with_id;
DELIMITER //
CREATE PROCEDURE get_actor_movies_with_id(IN p_person_id INT)
BEGIN
    SELECT DISTINCT 
        m.movie_id,
        m.moviename,
        IFNULL(AVG(r.rating), 0) AS average_rating
    FROM 
        movie_app_movie m
    LEFT JOIN 
        movie_app_roleactormovie ram ON m.movie_id = ram.movie_id
    LEFT JOIN 
        movie_app_rating r ON m.movie_id = r.movie_id
    WHERE 
        ram.person_id = p_person_id
    GROUP BY 
        m.movie_id
    UNION
    SELECT DISTINCT 
        m.movie_id,
        m.moviename,
        IFNULL(AVG(r.rating), 0) AS average_rating
    FROM 
        movie_app_movie m
    LEFT JOIN 
        movie_app_narration nr ON m.movie_id = nr.movie_id
    LEFT JOIN 
        movie_app_rating r ON m.movie_id = r.movie_id
    WHERE 
        nr.actor_id = p_person_id
    GROUP BY 
        m.movie_id;
END //
DELIMITER ;


DROP PROCEDURE IF EXISTS get_role_detail;
DELIMITER //
DROP PROCEDURE IF EXISTS get_role_detail;

DELIMITER //

CREATE PROCEDURE get_role_detail(IN p_role_id INT)
BEGIN
    -- Declare variables for role details
    DECLARE v_role_name VARCHAR(50);
    DECLARE v_role_description TEXT;

    -- Retrieve role details
    SELECT
        role_name,
        role_description
    INTO
        v_role_name,
        v_role_description
    FROM
        movie_app_role
    WHERE
        role_id = p_role_id;

    -- Return role details
    SELECT
        v_role_name AS role_name,
        v_role_description AS role_description;

    -- Retrieve actor and movie details for the role
    SELECT
        ram.movie_id,
        m.moviename AS movie_title,
        ram.person_id,
        p.name AS person_name
    FROM
        movie_app_roleactormovie ram
    JOIN
        movie_app_movie m ON ram.movie_id = m.movie_id
    JOIN
        movie_app_person p ON ram.person_id = p.personID
    WHERE
        ram.role_id = p_role_id;
END //

DELIMITER ;

