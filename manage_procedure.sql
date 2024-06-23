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
    AND ((m.releaseyear BETWEEN p_min_releaseyear AND p_max_releaseyear) OR m.releaseyear is null)
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

DROP PROCEDURE IF EXISTS delete_movie_and_directormovie;
DELIMITER //
CREATE PROCEDURE delete_movie_and_directormovie(IN p_movie_id INT)
BEGIN
	DELETE FROM movie_app_directormovie dm WHERE dm.movie_id = p_movie_id;
    DELETE FROM movie_app_movie m WHERE m.movie_id = p_movie_id;
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

DROP PROCEDURE IF EXISTS delete_person_and_directormovie;
DELIMITER //
CREATE PROCEDURE delete_person_and_directormovie(
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

DROP PROCEDURE IF EXISTS delete_movie_and_directormovie_and_genre;
DELIMITER //
CREATE PROCEDURE delete_movie_and_directormovie_and_genre(IN p_movie_id INT)
BEGIN
	DELETE FROM movie_app_MovieGenreAssociation mga WHERE mga.movie_id = p_movie_id;
	DELETE FROM movie_app_directormovie dm WHERE dm.movie_id = p_movie_id;
    DELETE FROM movie_app_comment mc WHERE mc.movie_id = p_movie_id;
    DELETE FROM movie_app_rating mr WHERE mr.movie_id = p_movie_id;
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

DROP PROCEDURE IF EXISTS search_movies_with_directors_and_companies_and_genres;
DELIMITER //
CREATE PROCEDURE search_movies_with_directors_and_companies_and_genres(
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

DROP PROCEDURE IF EXISTS delete_production_company;
DELIMITER $$
CREATE PROCEDURE delete_production_company(IN p_company_id INT)
BEGIN
    DELETE FROM movie_app_productioncompany WHERE company_id = p_company_id;
END$$
DELIMITER ;

