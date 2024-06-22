-- 创建存储过程来插入用户
DROP PROCEDURE IF EXISTS create_user;
DELIMITER //
CREATE PROCEDURE create_user(
    IN p_username VARCHAR(50),
    IN p_password VARCHAR(150)
)
BEGIN
    INSERT INTO movie_app_users (Username, UserPassword) VALUES (p_username, p_password);
END //
DELIMITER ;
