from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver



    
class Category(models.Model):
    text = models.CharField(max_length=200)
    def __str__(self):
        return self.text

class Quizzes(models.Model):
   
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quizzes')
    categories = models.ManyToManyField(Category)
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to="QuizPic/", default="QuizPic/default.png", null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    label = models.CharField(max_length=10, default=None, null=True, blank=True)
    duration = models.PositiveIntegerField()
    score = models.PositiveIntegerField()
    achievement = models.PositiveIntegerField(null=True, blank=True)
    likes = models.PositiveIntegerField(null=True, blank=True)
    enrollers = models.PositiveIntegerField(null=True, blank=True)
    questions_counter = models.SmallIntegerField(default=0)
    
    def __str__(self):
        return self.title
class Updated(models.Model):
    date_time = models.DateTimeField(verbose_name=_("Last Updated"), auto_now=True)
    
    class Meta:
        abstract = True

class Question(Updated):

    class Meta:
        verbose_name = _("Question")
        verbose_name_plural = _("Questions")
        ordering = ['id']

    SCALE = (
        (0, _('Fundamental')),
        (1, _('Beginner')),
        (2, _('Intermediate')),
        (3, _('Advanced')),
        (4, _('Expert'))
    )
    TYPE = (
        (0,_('Multiple Choice')),
    )

    quiz = models.ForeignKey(Quizzes, related_name="questions", on_delete=models.CASCADE)
    technique = models.IntegerField(choices=TYPE, default=0)
    title = models.CharField(max_length=200)
    difficulty = models.IntegerField(choices=SCALE, default=0)
    date_created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False, verbose_name=_('Active Status'))
    

    def __str__(self):
        return self.title

class Answer(Updated):
    
    question = models.ForeignKey(Question, related_name="answer", on_delete=models.CASCADE)
    answer_text = models.CharField(max_length=200, verbose_name=_("Answer Text"))
    is_right = models.BooleanField(default=False, verbose_name=_("is_right"))
    
    def __str__(self):
        return self.answer_text
    


@receiver(post_save, sender= Question)
def update_quiz_question_count(sender, instance, created, **kwargs):
    if created:
        quiz = instance.quiz
        quiz.questions_counter = quiz.questions.count()
        quiz.save()

@receiver(post_delete, sender=Question)
def decrement_quiz_question_count(sender, instance, **kwargs):
    quiz = instance.quiz
    quiz.questions_counter = quiz.questions.count()
    quiz.save()