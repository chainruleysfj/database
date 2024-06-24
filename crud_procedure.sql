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

DROP PROCEDURE IF EXISTS get_all_movies;
DELIMITER $$
CREATE PROCEDURE get_all_movies()
BEGIN
    SELECT * FROM movie_app_movie;
END$$
DELIMITER ;

DROP PROCEDURE IF EXISTS search_movies;
DELIMITER $$
CREATE PROCEDURE search_movies(
    IN movie_name VARCHAR(255),
    IN city VARCHAR(255)
)
BEGIN
    SELECT * FROM movie_app_movie
    WHERE moviename LIKE CONCAT('%', movie_name, '%')
    AND production_company_id IN (
        SELECT company_id FROM movie_app_productioncompany WHERE city LIKE CONCAT('%', city, '%')
    );
END$$
DELIMITER ;

DROP PROCEDURE IF EXISTS get_movie_detail;

DELIMITER //

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
    SELECT GROUP_CONCAT(CONCAT(p.name, ' (', r.role_name, ')') SEPARATOR '; ')
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

DROP PROCEDURE IF EXISTS delete_movie;
DELIMITER //
CREATE PROCEDURE delete_movie(IN p_movie_id INT)
BEGIN
    DELETE FROM movie_app_movie WHERE movie_id = p_movie_id;
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
    IN p_production_company_id INT
)
BEGIN
    SELECT * FROM movie_app_movie
    WHERE (moviename LIKE CONCAT('%', p_keyword, '%') OR plot_summary LIKE CONCAT('%', p_keyword, '%'))
    AND (length BETWEEN p_min_length AND p_max_length)
    AND (releaseyear BETWEEN p_min_releaseyear AND p_max_releaseyear)
    AND (production_company_id = p_production_company_id OR p_production_company_id IS NULL);
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

DROP PROCEDURE IF EXISTS delete_person;
DELIMITER //
CREATE PROCEDURE delete_person(
    IN p_person_id INT
)
BEGIN
    DELETE FROM movie_app_person WHERE personID = p_person_id;
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


DROP PROCEDURE IF EXISTS get_person_by_id;
DELIMITER //
CREATE PROCEDURE get_person_by_id(
    IN p_person_id INT
)
BEGIN
    SELECT * FROM movie_app_person WHERE personID = p_person_id;
END //
DELIMITER ;

