from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="skills")

    def __str__(self):
        return self.name


class Service(models.Model):
    freelancer = models.ForeignKey("users.Freelancer", on_delete=models.CASCADE, related_name="services")
    categories = models.ManyToManyField('Category', related_name= "services")
    
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} by {self.freelancer.user.username}"
