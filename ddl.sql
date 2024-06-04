create database if not exists movie_industry;

Use movie_industry;

create table if not exists Production_Company #表的存储没有区分大小写，使用_隔开
	(CompanyID smallint unsigned primary key auto_increment , # 编号使用自增，不设定显示格式
	Name varchar(50) not null unique,
	City varchar(50),
	CompanyDescription text 
	);

create table if not exists Movie
	(MovieID int unsigned primary key auto_increment,
    Moviename varchar(100) not null,
    Length int unsigned not null check (Length < 9999) comment'Duration in minutes', # 时长用分钟存储
    Releaseyear YEAR, # 感觉年份的限制可以不要
    PlotSummary text, # 情节感觉用text比varchar好一些
    ResourceLink VARCHAR(100) not null unique,
    ProductionCompanyID smallint unsigned,
    foreign key (ProductionCompanyID) references Production_Company(CompanyID)
    );

create table if not exists person # 将演员表与导演表整合为一张person表
	(personID int unsigned primary key auto_increment,
    Name varchar(50) not null,
    BirthDate date,
    Gender enum('M','F','U') comment'M for Male,F for Famale,U for Unkown',
    MaritalStatus enum('S','M','W','U') comment"Marital status: S=Single, M=Married, W=Widowed, U=Unknown"
    );

create table if not exists Roles # Role为关键字，改为Roles
	(RoleID int unsigned primary key auto_increment,
	RoleName VARCHAR(50) NOT NULL,
	RoleDescription TEXT
	);
    
CREATE TABLE IF NOT EXISTS Narrations 
	(NarrationID INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    Content TEXT NOT NULL, #content
    ActorID INT UNSIGNED,
    MovieID INT UNSIGNED NOT NULL UNIQUE,
    FOREIGN KEY (ActorID) REFERENCES person(personID),
    FOREIGN KEY (MovieID) REFERENCES Movie(MovieID)
	);

CREATE TABLE IF NOT EXISTS MovieGenre
	(GenreID smallint UNSIGNED PRIMARY KEY AUTO_INCREMENT, #ID的check好像可以不用
    GenreName varchar(10) not null unique
    );
    
CREATE TABLE IF NOT EXISTS Users # User为关键字，改为Users.管理员相关好像可以靠role实现，不开新表，就先不定义了.
	(UserID INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    Username varchar(50) not null unique,
    UserPassword varchar(50) not null # Password为关键字，改为UserPassword
    );

CREATE TABLE IF NOT EXISTS Rating_User_Movie
	(UserID INT UNSIGNED not null,
    MovieID int unsigned not null,
    RatingValue enum('1','2','3','4','5') not null , #评分用给定值可能比float简单一点？
    Primary key (UserID,MovieID),
    Foreign key (UserID) references Users(UserID),
    Foreign key (MovieID) references Movie(MovieID)
    );
    
CREATE TABLE IF NOT EXISTS Comment_User_Movie    
	(CommentID bigint PRIMARY KEY AUTO_INCREMENT,
    UserID INT UNSIGNED not null,
    MovieID int unsigned not null,
	Content text not null,
    CommentTime DATETIME ,
    Foreign key (UserID) references Users(UserID),
    Foreign key (MovieID) references Movie(MovieID)
    );

CREATE TABLE IF NOT EXISTS MovieGenre_Association
	(MovieID int unsigned not null,
    GenreID smallint UNSIGNED not null,
    Primary key (MovieID,GenreID),
    Foreign key (MovieID) references Movie(MovieID),
    Foreign key (GenreID) references moviegenre(GenreID)
    );
    
CREATE TABLE IF NOT EXISTS Director_Movie
	(MovieID int unsigned not null,
    personID int unsigned not null,
    Primary key (MovieID,personID),
    Foreign key (MovieID) references Movie(MovieID),
    Foreign key (personID) references person(personID)
    );

CREATE TABLE IF NOT EXISTS Role_Actor_Movie
	(MovieID int unsigned not null,
    personID int unsigned not null,
    RoleID int unsigned not null,
    Primary key (MovieID,personID,RoleID),
    Foreign key (MovieID) references Movie(MovieID),
    Foreign key (personID) references person(personID),
	Foreign key (RoleID) references roles(RoleID)
    );

