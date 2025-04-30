from services.models import Service

class ServiceSearcher:
    def __init__(self, categories= None, skills = None):
        self.categories = categories
        self.skills = skills
        self.queryset_all = Service.objects.all()

    def search(self):
        if not self.categories and not self.skills:
            return self.queryset_all, None, None
        
        queryset_category = Service.objects.none()
        queryset_skills = Service.objects.none()

        if self.categories:
            queryset_category = self.queryset_all.filter(
                categories__name__in = self.categories
            ).distinct()

        if self.skills:
            queryset_skills = self.queryset_all.filter(
                freelancer__skills__name__in=self.skills
            ).distinct()

        return None, queryset_category, queryset_skills 
         