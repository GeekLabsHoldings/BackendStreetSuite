from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils.functional import cached_property
from django.dispatch import receiver
from django.db.models.signals import post_save

percentage_validators = [MinValueValidator(0), MaxValueValidator(100)]

## category of each course ## 
class Category(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()

    def __str__(self):
        return self.title

class Course(models.Model):
    auther = models.ForeignKey(User, related_name='courses_author', null=True, blank=True , on_delete=models.CASCADE)
    category = models.ForeignKey(Category,max_length=50, null=True, blank=True , on_delete=models.CASCADE)
    image = models.ImageField(upload_to='CoursePic/', null=True, blank=True)
    title = models.CharField(max_length=255)
    likes_number = models.PositiveIntegerField(default=0)
    description = models.TextField(null=True, blank=True)
    subscriber_number = models.PositiveIntegerField(default=0)
    duration = models.CharField(max_length=50)
    users_completed = models.PositiveIntegerField(default=0)
    liked_users = models.ManyToManyField(User , related_name='liked_users')
    slug = models.SlugField(blank=True , null= True)

    def __str__(self):
        return self.title

    ## create slug on each specific save ##
    def save(self, *args , **keargs):
        self.slug = slugify(self.title)
        return super().save(*args , **keargs)
    
    ## cach the number of modules in first time ##
    @cached_property
    def get_number_modules(self):
        number = Module.objects.filter(course = self).count()
        return number

    ## get number of modules of each course ##
    def number_of_modules(self):
        return f'{self.get_number_modules} Modules' 


## module for applied courses ##
class Subscribed_courses(models.Model):
    user = models.ForeignKey(User, related_name='subscriber_user',on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='subscribed_course',on_delete=models.CASCADE)
    completed_modules = models.PositiveIntegerField(default=0)
    start_date = models.DateField(auto_now_add=True)
    assessment_score = models.FloatField(default=0.0)

class Module(models.Model):
    course = models.ForeignKey(Course, related_name='modules', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField() 
    slug = models.SlugField(blank=True , null= True) 

    def __str__(self):
        return self.title
    
    ## create slug on each specific save ##
    def save(self, *args , **keargs):
        self.slug = slugify(self.title)
        return super().save(*args , **keargs)

class Articles(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE , related_name='article_modules')
    title = models.CharField(max_length=255)
    article = models.TextField()
    image = models.ImageField(upload_to="CoursePic/SectionPic/",  null=True, blank=True)

    def __str__(self):
        return self.title
   
class Assessment(models.Model):
    course = models.ForeignKey(Course, related_name='assessments', on_delete=models.CASCADE , null=True , blank=True)
    description = models.TextField(blank=True, null=True)
    instructions = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.course.title

# class Question(models.Model):
#     assessment = models.ForeignKey(Assessment, related_name='questions', on_delete=models.CASCADE)
#     text = models.TextField(blank=True, null=True)

#     def __str__(self):
#         return self.text

# class Answer(models.Model):
#     question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
#     text = models.TextField(blank=True, null=True)
#     is_correct = models.BooleanField(default=False)

#     def __str__(self):
#         return self.question.text

class Questions(models.Model):
    course = models.ForeignKey(Course, related_name='course_question', on_delete=models.CASCADE)
    text = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.text

class Answers(models.Model):
    question = models.ForeignKey(Questions, related_name='course_answers', on_delete=models.CASCADE)
    text = models.TextField(blank=True, null=True)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.question.text

### segnal to increament subscriber_number once an subscribed course created ###
@receiver(post_save, sender = Subscribed_courses )
def increament_subscriber_number(sender, instance, created, **kwargs):
    ## get the course of instance (subscribed course) ##
    course = instance.course
    ## increment the subscriber_number attribute ##
    course.subscriber_number += 1
    course.save()
