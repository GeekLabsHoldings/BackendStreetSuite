from django.contrib import admin

from .models import Course, Module, Articles, Assessment , Category , Subscribed_courses , Answers , Questions  

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
admin.site.register(Category )
# admin.site.register(Likes_history)
admin.site.register(Module,ModuleCompletedAdmin)
admin.site.register(Articles, ArticlesAdmin)
admin.site.register(Assessment)
######################
admin.site.register(Questions)
admin.site.register(Answers,AnswerCompletedAdmin)
# admin.site.register(AssessmentCompleted,AssessmentCompletedAdmin)
# admin.site.register(CompletedModules , ModuleCompletedAdmin)
admin.site.register(Subscribed_courses , Subscribed_courses_Admin)