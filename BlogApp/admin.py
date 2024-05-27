from django.contrib import admin
from .models import Post, Tag


class PostAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("title", "date_posted", "author",)
# Register your models here.
admin.site.register(Post, PostAdmin)
admin.site.register(Tag)

