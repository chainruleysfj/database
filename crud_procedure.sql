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
    DELETE FROM movie_app_productioncompany WHERE id = p_company_id;
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
CREATE PROCEDURE get_movie_detail(IN movie_id INT)
BEGIN
    SELECT
        movie_id,
        moviename,
        length,
        releaseyear,
        plot_summary,
        resource_link,
        production_company_id
    FROM
        movie_app_movie
    WHERE
        movie_id = movie_id;
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

