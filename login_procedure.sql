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
