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
CREATE PROCEDURE update_password_procedure(IN p_user_id INT, IN new_password VARCHAR(255))
BEGIN
    UPDATE auth_user SET password = new_password WHERE id = p_user_id;
    DELETE FROM movie_app_loginrecord WHERE user_id = p_user_id;
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

DROP PROCEDURE IF EXISTS reset_password_proc;
DELIMITER $$
CREATE PROCEDURE reset_password_proc(
    IN p_username VARCHAR(150),
    IN p_security_answer VARCHAR(255),
    IN p_new_password VARCHAR(255),
    OUT p_success TINYINT(1),
    OUT p_message VARCHAR(255)
)
BEGIN
    DECLARE p_user_id INT;
    DECLARE answer_correct TINYINT(1);
    
    -- Check if the user exists
    SELECT id INTO p_user_id FROM auth_user WHERE username = p_username;
    IF p_user_id IS NULL THEN
        SET p_success = 0;
        SET p_message = 'User does not exist.';
    ELSE
        -- Check if the provided security answer matches the stored answer
        SELECT CASE WHEN LOWER(security_answer) = LOWER(p_security_answer) THEN 1 ELSE 0 END INTO answer_correct
        FROM movie_app_securityqa
        WHERE user_id = p_user_id;

        IF answer_correct = 1 THEN
            -- Update the user's password
            UPDATE auth_user SET password = p_new_password WHERE id = p_user_id;
            SET p_success = 1;
            SET p_message = 'Password reset successfully.';
			DELETE FROM movie_app_loginrecord WHERE user_id = p_user_id;
        ELSE
            SET p_success = 0;
            SET p_message = 'Incorrect security answer.';
        END IF;
    END IF;
    SELECT p_success AS success, p_message AS message;
END$$
DELIMITER ;

DROP PROCEDURE IF EXISTS get_security_question_proc;
DELIMITER $$
CREATE PROCEDURE get_security_question_proc(
    IN p_username VARCHAR(150),
    OUT p_security_question VARCHAR(255),
    OUT p_message VARCHAR(255)
)
BEGIN
    DECLARE p_user_id INT;
    -- Check if the user exists and get the user ID
    SELECT id INTO p_user_id FROM auth_user WHERE username = p_username;
    IF p_user_id IS NULL THEN
        SET p_security_question = NULL;
        SET p_message = 'User does not exist.';
    ELSE
        -- Get the security question for the user
        SELECT security_question INTO p_security_question 
        FROM movie_app_securityqa 
        WHERE user_id = p_user_id;
        
        IF p_security_question IS NULL THEN
            SET p_message = 'Security question not set for this user.';
        ELSE
            SET p_message = 'Success';
        END IF;
    END IF;
    SELECT p_security_question AS security_question, p_message AS message;
END$$
DELIMITER ;

DROP PROCEDURE IF EXISTS manage_login_record;
DELIMITER $$
CREATE PROCEDURE manage_login_record(
    IN p_user_id INT,
    IN p_session_key VARCHAR(100),
    IN p_action VARCHAR(10)
)
BEGIN
    -- Check if the user already has an active login record
    IF p_action = 'create' THEN
        -- Create a new login record
        INSERT INTO movie_app_loginrecord (user_id, session_key, login_time)
        VALUES (p_user_id, p_session_key, now());

    ELSEIF p_action = 'delete' THEN
        -- Delete the specific login record
        DELETE FROM movie_app_loginrecord
        WHERE user_id = p_user_id AND session_key = p_session_key;
    END IF;
END$$
DELIMITER ;

DROP PROCEDURE IF EXISTS get_active_login_records;
DELIMITER $$
CREATE PROCEDURE get_active_login_records(
    IN p_user_id INT
)
BEGIN
    SELECT COUNT(*) 
    FROM movie_app_loginrecord
    WHERE user_id = p_user_id;
END$$
DELIMITER ;

