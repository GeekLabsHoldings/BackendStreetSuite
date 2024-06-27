from django.contrib import admin

from .models import Course, Module, Section, Assessment, Question, Answer, AssessmentCompleted

# Register your models here.
admin.site.register(Course)
admin.site.register(Module)
admin.site.register(Section)
admin.site.register(Assessment)
admin.site.register(Answer)
admin.site.register(Question)
admin.site.register(AssessmentCompleted)