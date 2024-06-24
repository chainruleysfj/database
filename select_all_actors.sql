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
    SELECT DISTINCT m.movie_id,m.moviename
    FROM movie_app_movie m
    JOIN movie_app_roleactormovie ram ON m.movie_id = ram.movie_id
    WHERE ram.person_id = p_person_id
    UNION
    SELECT DISTINCT m.movie_id,m.moviename
    FROM movie_app_movie m
    JOIN movie_app_narration nr ON m.movie_id = nr.movie_id
    WHERE nr.actor_id = p_person_id;
END //
DELIMITER ;