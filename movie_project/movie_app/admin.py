from django.contrib import admin
from .models import ProductionCompany, Movie, Person, DirectorMovie, MovieGenre, MovieGenreAssociation

admin.site.register(ProductionCompany)
admin.site.register(Movie)
admin.site.register(Person)
admin.site.register(DirectorMovie)
admin.site.register(MovieGenre)
admin.site.register(MovieGenreAssociation)

