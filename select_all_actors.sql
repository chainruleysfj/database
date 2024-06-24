DELIMITER //

CREATE PROCEDURE get_all_actors()
BEGIN
    SELECT DISTINCT p.personID, p.name, p.birth_date, p.gender, p.marital_status
    FROM Person p
    LEFT JOIN ActorMovie am ON p.personID = am.person_id
    LEFT JOIN Movie m ON p.personID = m.narrator_id
    WHERE am.person_id IS NOT NULL OR m.narrator_id IS NOT NULL;
END //

DELIMITER ;
