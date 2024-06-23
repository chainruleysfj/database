CREATE INDEX idx_name_city ON movie_app_productioncompany (name, city);

CREATE INDEX idx_moviename ON movie_app_movie (moviename);

CREATE INDEX idx_production_company_id ON movie_app_movie (production_company_id);

CREATE INDEX idx_movie_length ON movie_app_movie(length);

CREATE INDEX idx_movie_releaseyear ON movie_app_movie(releaseyear);

CREATE fulltext index idx_movie_plot_summary ON movie_app_movie(plot_summary);

CREATE INDEX idx_person_name ON movie_app_person (name);

CREATE UNIQUE INDEX  idx_genre_name ON movie_app_MovieGenre (genre_name);

CREATE INDEX  idx_movie_id_genre_association ON movie_app_MovieGenreAssociation (Movie_ID);

CREATE INDEX  idx_genre_id_genre_association ON movie_app_MovieGenreAssociation (Genre_ID);