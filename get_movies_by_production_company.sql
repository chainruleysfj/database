DROP PROCEDURE IF EXISTS get_movies_by_production_company()；
DELIMITER $$

CREATE PROCEDURE get_movies_by_production_company(
    IN company_id INT
)
BEGIN
    SELECT 
        m.movie_id,
        m.moviename,
        m.length,
        m.releaseyear,
        COALESCE(AVG(r.rating), 0) AS average_rating
    FROM 
        movie_app_movie m
        LEFT JOIN movie_app_rating r ON m.movie_id = r.movie_id
    WHERE 
        m.production_company_id = company_id
    GROUP BY 
        m.movie_id, m.moviename, m.length, m.releaseyear;
END$$

DELIMITER ;