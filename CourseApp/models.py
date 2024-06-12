from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User


percentage_validators = [MinValueValidator(0), MaxValueValidator(100)]
class Course(models.Model):
    user = models.ManyToManyField(User, related_name='courses')
    image = models.ImageField(upload_to="CoursePic/", default="CoursePic/default.png", null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    label = models.CharField(max_length=12, null=True, blank=True)
    subscribers = models.PositiveIntegerField()
    tag = models.CharField(max_length=20, null=True, blank=True)
    completed = models.PositiveIntegerField()
    duration = models.CharField(max_length=50)
    average_completed = models.IntegerField(validators=percentage_validators, default=0)

class Module(models.Model):
    course = models.ForeignKey(Course, related_name='modules', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()


class Section(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    article = models.TextField()
    image = models.ImageField(upload_to="CoursePic/SectionPic/", default="CoursePic/default.png", null=True, blank=True)
    is_completed = models.BooleanField(default=False)

class Assessment(models.Model):
    course = models.ForeignKey(Course, related_name='assessments', on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    instructions = models.TextField(blank=True, null=True)
    score = models.PositiveIntegerField(default=0)

class Question(models.Model):
    assessment = models.ForeignKey(Assessment, related_name='questions', on_delete=models.CASCADE)
    text = models.TextField(blank=True, null=True)

class Answer(models.Model):
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    text = models.TextField(blank=True, null=True)
    is_correct = models.BooleanField(default=False)





