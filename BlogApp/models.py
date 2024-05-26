from django.db import models
from UserApp.models import User
from django.urls import reverse

class Tag(models.Model):
    caption = models.CharField(max_length=12)

    def __str__(self):
        return self.caption

class Post(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=100, blank=True, null=True)
    content = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    tags = models.ManyToManyField(Tag)
    image = models.ImageField(upload_to="PostPic/", default="")
    slug = models.SlugField(default="", blank=True, null=False, db_index=True)

    def get_absolute_url(self):
        return reverse("post-detail", args=[self.slug])


