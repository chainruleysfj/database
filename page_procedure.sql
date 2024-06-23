DROP PROCEDURE IF EXISTS get_movie_production_company;
DELIMITER //
CREATE PROCEDURE get_movie_production_company(IN p_movie_id INT)
BEGIN
    SELECT production_company_id
    FROM movie_app_movie
    WHERE movie_id = p_movie_id;
END //
DELIMITER ;
