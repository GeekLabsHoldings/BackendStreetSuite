from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User


percentage_validators = [MinValueValidator(0), MaxValueValidator(100)]


class Course(models.Model):
    CATEGORY_CHOICES = [
        ('options', 'Options'),
        ('stock', 'Stock'),
        ('day_trading', 'Day Trading'),
    ]

    user = models.ForeignKey(User, related_name='courses_author', null=True, on_delete=models.CASCADE)
    subscribed = models.ManyToManyField(User, related_name="subscribed",)
    image = models.ImageField(upload_to="CoursePic/", default="CoursePic/default.png", null=True, blank=True)
    title = models.CharField(max_length=255)
    likes_number = models.PositiveIntegerField(default=0)
    likes = models.ManyToManyField(User, related_name="likes")
    description = models.TextField(null=True, blank=True)
    label = models.CharField(max_length=12, null=True, blank=True)
    subscribers = models.PositiveIntegerField(default=0)
    tag = models.CharField(max_length=20, null=True, blank=True)
    completed = models.PositiveIntegerField(default=0)
    duration = models.CharField(max_length=50)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='options')
    average_completed = models.IntegerField(validators=percentage_validators, default=0)
    users_completed = models.ManyToManyField(User, related_name="Course")


class Module(models.Model):
    course = models.ForeignKey(Course, related_name='modules', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField() 


class Section(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    article = models.TextField()
    image = models.ImageField(upload_to="CoursePic/SectionPic/", default="CoursePic/default.png", null=True, blank=True)
    completed = models.ManyToManyField(User, related_name="section_completed")

class Assessment(models.Model):
    module = models.ForeignKey(Module, related_name='assessments', on_delete=models.CASCADE,)
    description = models.TextField(blank=True, null=True)
    instructions = models.TextField(blank=True, null=True)

class Question(models.Model):
    assessment = models.ForeignKey(Assessment, related_name='questions', on_delete=models.CASCADE)
    text = models.TextField(blank=True, null=True)

class Answer(models.Model):
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    text = models.TextField(blank=True, null=True)
    is_correct = models.BooleanField(default=False)

class AssessmentCompleted(models.Model):
    user = models.ForeignKey(User, related_name="assment_completed", on_delete=models.CASCADE)
    assessment = models.ForeignKey(Assessment, related_name="assessment_completed", on_delete=models.CASCADE)
    score = models.IntegerField(validators=percentage_validators, default=0)
    module = models.ForeignKey(Module, related_name="completed", on_delete=models.CASCADE, null=True)
