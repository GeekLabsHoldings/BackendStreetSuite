from django.contrib import admin
from . import models
# Register your models here.
@admin.register(models.Category)
class CatAdmin(admin.ModelAdmin):
    list_display = ['text']

@admin.register(models.SubCategory)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['id','title',]

class AnswerInlineModel(admin.TabularInline):
    model = models.Answer
    fields = ['answer_text', 'is_right',]

@admin.register(models.Question)
class QuestionAdmin(admin.ModelAdmin):
    fields = ['title','subcategory',]
    list_display = ['title','subcategory',]
    inlines = [AnswerInlineModel]

@admin.register(models.Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['answer_text','is_right','question']

@admin.register(models.UserEmail)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'result']