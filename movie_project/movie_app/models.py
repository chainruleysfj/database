from django.db import models
from django.core.validators import MaxValueValidator

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
