from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

    
class Category(models.Model):
    text = models.CharField(max_length=200)
    
    def __str__(self):
        return self.text

class UserEmail(models.Model):
    email = models.EmailField()
    result = models.FloatField()

    def __str__(self):
        return self.email
   
class SubCategory(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authored_subcategories')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to="QuizPic/", default="QuizPic/default.png", null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    label = models.CharField(max_length=10, default=None, null=True, blank=True)
    duration = models.PositiveIntegerField()
    result = models.PositiveIntegerField(default=0)
    questions_counter = models.SmallIntegerField(default=0) ####
    total_passed = models.PositiveBigIntegerField(default=0) ###
    total_entries = models.PositiveBigIntegerField(default=0) ###
    avg_passed = models.FloatField(default=0.0)
    users = models.ManyToManyField(UserEmail,blank=True)

    def __str__(self):
        return self.title
    
class Question(models.Model):
    subcategory = models.ForeignKey(SubCategory, related_name="questions", on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    is_active = models.BooleanField(default=False, verbose_name=_('Active Status'))
    
    def __str__(self):
        return self.title

class Answer(models.Model):
    question = models.ForeignKey(Question, related_name="answer", on_delete=models.CASCADE)
    answer_text = models.CharField(max_length=200, verbose_name=_("Answer Text"))
    is_right = models.BooleanField(default=False, verbose_name=_("is_right"))
    
    def __str__(self):
        return self.answer_text
    
@receiver(post_save, sender= Question)
def update_subcategory_question_count(sender, instance, created, **kwargs):
    if created:
        subcategory = instance.subcategory
        subcategory.questions_counter += 1
        subcategory.save()

@receiver(post_delete, sender=Question)
def decrement_subcategory_question_count(sender, instance, **kwargs):
    subcategory = instance.subcategory
    subcategory.questions_counter -= 1
    subcategory.save()