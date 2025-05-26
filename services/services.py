from services.models import Service

class ServiceSearcher:
    """
    Helper class to perform filtered searches on the Service model
    based on categories and/or freelancer skills.

    Args:
        categories (list[str] | None): List of category names to filter by.
        skills (list[str] | None): List of skill names to filter by.

    Attributes:
        queryset_all (QuerySet): Base queryset of all Service objects.

    Methods:
        search():
            Returns a tuple with three elements:
            - None if no filters applied,
            - QuerySet of Services filtered by categories (or empty),
            - QuerySet of Services filtered by skills (or empty).
    """

    def __init__(self, categories= None, skills = None):
        self.categories = categories
        self.skills = skills
        self.queryset_all = Service.objects.all()

    def search(self):
        """
        Executes the search based on provided categories and skills.

        Returns:
            tuple: (None or QuerySet, QuerySet, QuerySet)
                - First element is None if any filters provided, else full queryset.
                - Second element is queryset filtered by categories or empty.
                - Third element is queryset filtered by skills or empty.
        """
        
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
         