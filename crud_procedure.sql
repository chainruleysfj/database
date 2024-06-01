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
