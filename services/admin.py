from django.contrib import admin
from .models import Category, Skill

class SkillInline(admin.TabularInline):  
    model = Skill
    extra = 0  

class CategoryAdmin(admin.ModelAdmin):
    inlines = [SkillInline]

admin.site.register(Category, CategoryAdmin)
admin.site.register(Skill)  
