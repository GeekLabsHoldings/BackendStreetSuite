from typing import Iterable
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User

class Vacancy(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=1000)
    responsibilities = models.TextField()
    benefits = models.TextField()
    requirement = models.TextField()
    slug = models.SlugField(blank=True , null= True)

    def __str__(self):
        return self.title
    
    def save(self, *args , **kwargs):
        self.slug = slugify(self.title)
        return super().save(*args , **kwargs)
    
## function to save cv of candidtates in media dir ##

def save_cv(instance, filename):
    document , extention = filename.split(".")
    ### return the path of saved uplauded image 
    return f"apply/{instance.first_name}_{instance.last_name}.{extention}"


## class for appliction ##
class Application(models.Model):
    vacancy = models.ForeignKey(Vacancy,on_delete=models.CASCADE , related_name="vacancy")
    first_name = models.CharField(max_length=70)
    last_name = models.CharField(max_length=70)
    email = models.EmailField()
    portofolio_link = models.URLField()
    git_hub_link = models.URLField()
    cv = models.FileField(upload_to=save_cv)

    def __str__(self):
        return self.first_name