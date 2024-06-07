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

DROP PROCEDURE IF EXISTS get_all_movies_with_directors_and_companies;
DELIMITER //
CREATE PROCEDURE get_all_movies_with_directors_and_companies()
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

DROP PROCEDURE IF EXISTS search_movies_with_directors_and_companies;
DELIMITER //
CREATE PROCEDURE search_movies_with_directors_and_companies(
    IN p_keyword VARCHAR(100),
    IN p_min_length INT,
    IN p_max_length INT,
    IN p_min_releaseyear INT,
    IN p_max_releaseyear INT,
    IN p_production_company_id INT
)
BEGIN
    SELECT m.Movie_ID, m.moviename, m.length, m.releaseyear, m.plot_summary, m.resource_link, pc.name AS production_company_name,
           GROUP_CONCAT(p.name) AS directors
    FROM movie_app_movie m
    LEFT JOIN movie_app_directormovie dm ON m.Movie_ID = dm.Movie_ID
    LEFT JOIN movie_app_person p ON dm.person_ID = p.personID
    LEFT JOIN movie_app_productioncompany pc ON m.production_company_id = pc.company_id
    WHERE (p_keyword IS NULL OR m.moviename LIKE CONCAT('%', p_keyword, '%'))
    AND m.length BETWEEN p_min_length AND p_max_length
    AND m.releaseyear BETWEEN p_min_releaseyear AND p_max_releaseyear
    AND (p_production_company_id IS NULL OR m.production_company_id = p_production_company_id)
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

