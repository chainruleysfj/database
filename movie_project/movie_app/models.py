from django.db import models
from django.core.validators import MaxValueValidator
from django.contrib.auth.models import AbstractUser,User


# Create your models here.
class ProductionCompany(models.Model):
    company_id = models.AutoField(primary_key=True)  # 对应 CompanyID
    name = models.CharField(max_length=50, unique=True)  # 对应 Name
    city = models.CharField(max_length=50, blank=True, null=True)  # 对应 City
    company_description = models.TextField(blank=True, null=True)  # 对应 CompanyDescription

    def __str__(self):
        return self.name
    

class Movie(models.Model):
    movie_id = models.AutoField(primary_key=True)  # 对应 MovieID
    moviename = models.CharField(max_length=100)  # 对应 Moviename
    length = models.PositiveSmallIntegerField(validators=[MaxValueValidator(9999)])  # 对应 Length，使用 PositiveSmallIntegerField 并添加验证器以确保长度小于9999
    releaseyear = models.IntegerField(null=True, blank=True)  # 对应 Releaseyear，可以为空
    plot_summary = models.TextField(blank=True)
    resource_link = models.CharField(max_length=100, unique=True)  # 对应 ResourceLink
    production_company = models.ForeignKey(ProductionCompany, on_delete=models.CASCADE)  # 对应 ProductionCompanyID，设置外键约束

    def __str__(self):
        return self.moviename

class Person(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('U', 'Unknown'),
    ]

    MARITAL_STATUS_CHOICES = [
        ('S', 'Single'),
        ('M', 'Married'),
        ('W', 'Widowed'),
        ('U', 'Unknown'),
    ]

    personID = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='U')
    marital_status = models.CharField(max_length=1, choices=MARITAL_STATUS_CHOICES, default='U')

    def __str__(self):
        return self.name
    
class DirectorMovie(models.Model):
    id = models.AutoField(primary_key=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='directors')
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='movies_directed')

    class Meta:
        unique_together = ('movie_id', 'person_id')  # 确保电影和导演的组合是唯一的

class MovieGenre(models.Model):
    genre_id = models.AutoField(primary_key=True)  # 对应 GenreID
    genre_name = models.CharField(max_length=10, unique=True)  # 对应 GenreName

    def __str__(self):
        return self.genre_name
    
class MovieGenreAssociation(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    genre = models.ForeignKey(MovieGenre, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('movie', 'genre')



class SecurityQA(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    security_question = models.CharField(max_length=255)
    security_answer = models.CharField(max_length=255)


class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    content = models.TextField()
    comment_time = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    is_denied = models.BooleanField(default=False)  # New field to track denied comments
    
class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()  # Should be between 1 and 5

    class Meta:
        unique_together = ('user', 'movie')
    def __str__(self):
        return f"{self.user.username}'s Security Question"
    
class LoginRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=100)
    login_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Login Record"
        verbose_name_plural = "Login Records"

    def __str__(self):
        return f"{self.user.username} - {self.login_time}"
