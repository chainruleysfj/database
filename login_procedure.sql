-- 创建存储过程来插入用户
DROP PROCEDURE IF EXISTS create_user_procedure;
DELIMITER //
CREATE PROCEDURE create_user_procedure(
    IN p_username VARCHAR(150),
    IN p_password VARCHAR(128)
)
BEGIN
    INSERT INTO auth_user (username, password,is_superuser,first_name,last_name,email, is_staff, is_active, date_joined)
    VALUES (p_username, p_password, FALSE, '', '','', FALSE, TRUE, NOW());
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS get_users_procedure;
DELIMITER //
CREATE PROCEDURE get_users_procedure(
    IN p_username VARCHAR(150)
)
BEGIN
    IF p_username IS NULL THEN
        SELECT id, username, is_staff, is_active, is_superuser
        FROM auth_user;
    ELSE
        SELECT id, username, is_staff, is_active, is_superuser
        FROM auth_user
        WHERE username LIKE CONCAT('%', p_username, '%');
    END IF;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS set_staff_status;
DELIMITER //
CREATE PROCEDURE set_staff_status(
    IN p_user_id INT,
    IN p_is_staff BOOLEAN
)
BEGIN
    UPDATE auth_user
    SET is_staff = p_is_staff
    WHERE id = p_user_id;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS change_staff_status;
DELIMITER //
CREATE PROCEDURE change_staff_status(
    IN p_user_id INT
)
BEGIN
    UPDATE auth_user
    SET is_staff = not is_staff
    WHERE id = p_user_id;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS delete_user;
DELIMITER //
CREATE PROCEDURE delete_user(
    IN p_user_id INT
)
BEGIN
    DELETE FROM auth_user WHERE id = p_user_id;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS search_users;
DELIMITER //
CREATE PROCEDURE search_users(
    IN p_query VARCHAR(255)
)
BEGIN
    IF p_query IS NULL OR p_query = '' THEN
        SELECT * FROM auth_user;
    ELSE
        SELECT * FROM auth_user WHERE username LIKE CONCAT('%', p_query, '%');
    END IF;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS update_password_procedure;
DELIMITER //
CREATE PROCEDURE update_password_procedure(IN user_id INT, IN new_password VARCHAR(255))
BEGIN
    UPDATE auth_user SET password = new_password WHERE id = user_id;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS set_security_question_proc;
DELIMITER $$
CREATE PROCEDURE set_security_question_proc(
    IN p_user_id INT,
    IN p_security_question VARCHAR(255),
    IN p_security_answer VARCHAR(255)
)
BEGIN
    DECLARE user_exists INT;
    -- Check if the user exists
    SELECT COUNT(*) INTO user_exists FROM auth_user WHERE id = p_user_id;
    
    IF user_exists = 1 THEN
        -- Update or insert into SecurityQA table
        INSERT INTO movie_app_securityqa (user_id, security_question, security_answer)
        VALUES (p_user_id, p_security_question, p_security_answer)
        ON DUPLICATE KEY UPDATE
        security_question = VALUES(security_question),
        security_answer = VALUES(security_answer);
    ELSE
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'User does not exist';
    END IF;
END$$
DELIMITER ;

