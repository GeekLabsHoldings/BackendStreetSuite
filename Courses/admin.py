from django.contrib import admin

from .models import Course, Module, Article, Assessment , Category , Subscribed_course , Answer , Question 

class Subscribed_courses_Admin(admin.ModelAdmin):
    list_display = ("user", 'course', 'completed_modules', 'start_date')


class ModuleCompletedAdmin(admin.ModelAdmin):
    list_display = ("title","course")

class AnswerCompletedAdmin(admin.ModelAdmin):
    list_display = ("question", "text","is_correct")

class ArticlesAdmin(admin.ModelAdmin):
    list_display = ("title", "module")

# Register your models here.
admin.site.register(Course)
admin.site.register(Category)
admin.site.register(Module,ModuleCompletedAdmin)
admin.site.register(Article, ArticlesAdmin)
admin.site.register(Assessment)
admin.site.register(Question)
admin.site.register(Answer,AnswerCompletedAdmin)
admin.site.register(Subscribed_course , Subscribed_courses_Admin)