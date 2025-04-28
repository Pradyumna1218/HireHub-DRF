from django.contrib import admin
from users.models import Freelancer, Client, User

class FreelancerAdmin(admin.ModelAdmin):
    list_display = ('user', 'display_skills_with_categories')

    def display_skills_with_categories(self, obj):
        return ", ".join(
            f"{skill.name} ({skill.category.name})"
            for skill in obj.skills.all()
        )

    display_skills_with_categories.short_description = 'Skills (Category)'

admin.site.register(Freelancer, FreelancerAdmin)

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('user', 'display_preferred_categories')

    def display_preferred_categories(self, obj):
        return ", ".join([category.name for category in obj.preferred_categories.all()])

    display_preferred_categories.short_description = 'Preferred Categories'

admin.site.register(User)
