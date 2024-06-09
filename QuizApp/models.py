from django.db import models
from django.utils.translation import gettext_lazy as _

class Category(models.Model):
    name = models.CharField(max_length=200)
    def __str__(self):
        return self.name
    
class Quizzes(models.Model):
   
    class Meta:
        ordering = ['id']

    title = models.CharField(max_length=200, default=_("New Quiz"), verbose_name=_("Quiz title"))
    categories = models.ManyToManyField(Category)
    date_created = models.DateTimeField(auto_now_add=True)
    label = models.CharField(max_length=10, default=None, null=True, blank=True)
    
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

    quiz = models.ForeignKey(Quizzes, related_name="question", on_delete=models.DO_NOTHING)
    technique = models.IntegerField(choices=TYPE, default=0)
    title = models.CharField(max_length=200)
    difficulty = models.IntegerField(choices=SCALE, default=0)
    date_created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False, verbose_name=_('Active Status'))

    def __str__(self):
        return self.title

class Answer(Updated):
    class Meta:
        ordering = ['id']

    question = models.ForeignKey(Question, related_name="answer", on_delete=models.DO_NOTHING)
    answer_text = models.CharField(max_length=200, verbose_name=_("Answer Text"))
    is_right = models.BooleanField(default=False, verbose_name=_("is_right"))
    
    def __str__(self):
        return self.answer_text
    

