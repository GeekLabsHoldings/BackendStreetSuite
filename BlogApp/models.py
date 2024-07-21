from django.db import models
from UserApp.models import User
from django.urls import reverse
from datetime import timedelta
from django.utils.text import slugify

class Category(models.Model):
    text = models.CharField(max_length=16)

    def __str__(self):
        return self.text

class Post(models.Model):
    categories = models.ManyToManyField(Category)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=100, blank=True, null=True)
    content = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)
    time_reading = models.DurationField(blank=True, null=True)
    videolink = models.URLField(null=True, blank=True)
    contentimage = models.ImageField(upload_to="PostPic/", default="PostPic/default.png", null=True, blank=True)
    image = models.ImageField(upload_to="CoverPic/", default="CoverPic/default.png", null=True, blank=True)
    slug = models.SlugField(unique=True, blank=True, null=False, db_index=True)

    def get_absolute_url(self):
        return reverse("post-detail", args=[self.slug])  
    
 
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        WordCount = len(self.content.split())/86400 
        self.time_reading = timedelta(WordCount)
        super().save(*args, **kwargs)