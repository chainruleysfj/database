DROP PROCEDURE IF EXISTS get_movie_production_company;
DELIMITER //
CREATE PROCEDURE get_movie_production_company(IN p_movie_id INT)
BEGIN
    SELECT production_company_id
    FROM movie_app_movie
    WHERE movie_id = p_movie_id;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS delete_production_company;
DELIMITER //
CREATE PROCEDURE delete_production_company(IN p_company_id INT)
BEGIN
    DECLARE done INT DEFAULT 0;
    DECLARE v_movie_id INT;

    -- Declare a cursor to select all movie_ids associated with the production company
    DECLARE movie_cursor CURSOR FOR
        SELECT m.movie_id FROM movie_app_movie m WHERE m.production_company_id = p_company_id;

    -- Declare continue handler to handle cursor end
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

    -- Open the cursor
    OPEN movie_cursor;

    -- Loop through all movie_ids and delete them
    read_loop: LOOP
        FETCH movie_cursor INTO v_movie_id;
        IF done THEN
            LEAVE read_loop;
        END IF;
        CALL delete_movie_and_directormovie_and_genre(v_movie_id);
    END LOOP;

    -- Close the cursor
    CLOSE movie_cursor;

    -- Delete the production company
    DELETE FROM movie_app_productioncompany pc WHERE pc.company_id = p_company_id;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS get_movies_by_company;
DELIMITER //
CREATE PROCEDURE get_movies_by_company(IN p_company_id INT)
BEGIN
    SELECT movie_id FROM movie_app_movie WHERE production_company_id = p_company_id;
END //
DELIMITER ;
