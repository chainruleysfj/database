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

