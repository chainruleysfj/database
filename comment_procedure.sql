DROP PROCEDURE IF EXISTS get_user_activity;
DELIMITER //
CREATE PROCEDURE get_user_activity(IN user_id INT)
BEGIN
    -- Get Ratings
    SELECT 
        r.id,
        r.user_id,
        r.movie_id,
        m.moviename AS movie_name,
        r.rating
    FROM 
        movie_app_rating r
    JOIN 
        movie_app_movie m ON r.movie_id = m.movie_id
    WHERE 
        r.user_id = user_id;

    -- Get Comments
    SELECT 
        c.comment_id,
        c.user_id,
        c.movie_id,
        m.moviename AS movie_name,
        c.content,
        c.comment_time
    FROM 
        movie_app_comment c
    JOIN 
        movie_app_movie m ON c.movie_id = m.movie_id
    WHERE 
        c.user_id = user_id
    AND 
        c.is_approved = TRUE;
END //

DELIMITER ;