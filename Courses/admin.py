from django.contrib import admin

from .models import Course, Module, Articles, Assessment , Category , Subscribed_courses , Answers , Questions  

class Subscribed_courses_Admin(admin.ModelAdmin):
    list_display = ("user", 'course', 'completed_modules', 'start_date')

# class ModuleCompletedAdmin(admin.ModelAdmin):
#     list_display = ("user", "module")

class AnswerCompletedAdmin(admin.ModelAdmin):
    list_display = ("question", "text","is_correct")

# Register your models here.
admin.site.register(Course)
admin.site.register(Category)
# admin.site.register(Likes_history)
admin.site.register(Module)
admin.site.register(Articles)
admin.site.register(Assessment)
######################
admin.site.register(Questions)
admin.site.register(Answers,AnswerCompletedAdmin)
# admin.site.register(AssessmentCompleted,AssessmentCompletedAdmin)
# admin.site.register(CompletedModules , ModuleCompletedAdmin)
admin.site.register(Subscribed_courses , Subscribed_courses_Admin)