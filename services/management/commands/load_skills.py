from django.core.management.base import BaseCommand
from services.models import Skill, Category
from services.utlis import SKILL_CATEGORY_MAP

class Command(BaseCommand):
    help = "Load Skills and Category into the database"

    def handle(self, *args, **kwargs):
        for skill_name, category_name in SKILL_CATEGORY_MAP.items():
            category, created = Category.objects.get_or_create(
                name=category_name,
                defaults={'description': f'Description for {category_name}'}
            )
            skill, created = Skill.objects.get_or_create(
                name = skill_name,
                defaults={'category': category}
            )