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
CREATE PROCEDURE get_movie_detail(IN p_movie_id INT)
BEGIN
    SELECT
        movie_id,
        moviename,
        length,
        releaseyear,
        plot_summary,
        resource_link,
        name
    FROM
        movie_app_movie JOIN movie_app_productioncompany ON production_company_id = company_id
    WHERE
        p_movie_id = movie_id;
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

