from rest_framework import serializers
from .models import Category, Skill, Service, Proposal
from django.db import transaction
from users.models import Freelancer
class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name']

class CategorySerializer(serializers.ModelSerializer):
    skills = SkillSerializer(read_only = True, many=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'skills']

class ServiceSerializer(serializers.ModelSerializer):
    categories = serializers.SerializerMethodField(read_only=True)
    freelancer = serializers.SerializerMethodField()
    skills = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = [
            'id', 'freelancer', 'title',
            'description', 'price', 'is_active',
            'skills', 'categories'
        ]

    def create(self, validated_data):
        freelancer = self.context['request'].user.freelancer

        freelancer_skills = freelancer.skills.all()
        related_categories = Category.objects.filter(skills__in=freelancer_skills).distinct()

        with transaction.atomic():
            service = Service.objects.create(freelancer=freelancer, **validated_data)
            service.categories.set(related_categories)
            service.save()

        return service

    def get_freelancer(self, obj):
        return obj.freelancer.user.username

    def get_skills(self, obj):
        category_skills = []
        for category in obj.categories.all():
            category_skills += list(category.skills.all())

        category_skill_ids = {skill.id for skill in category_skills}

        freelancer_skills = obj.freelancer.skills.all()
        return [skill.name for skill in freelancer_skills if skill.id in category_skill_ids]

    def get_categories(self, obj):
        return [category.name for category in obj.categories.all()]



class FreelancerServiceDetailSerializer(serializers.ModelSerializer):
    freelancer = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()
    skills = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = [
            'id', 'freelancer', 'title', 
            'description', 'price', 'is_active',
            'skills', 'categories' 
            ]
        read_only = ['categories', "skills"]
        
    def get_freelancer(self, obj):
        return obj.freelancer.user.username
    
    def get_categories(self, obj):
        return [category.name for category in obj.categories.all()]
    
    def get_skills(self, obj):
        return [skills.name for skills in obj.freelancer.skills.all()]


class ServiceSearchSerializer(serializers.Serializer):
    categories = serializers.ListField(
        child = serializers.CharField(),
        required = False
    )
    skills = serializers.ListField(
        child = serializers.CharField(),
        required = False
    )
     
class ProposalCreateSerializer(serializers.ModelSerializer):
    freelancer = serializers.CharField(write_only=True)

    class Meta:
        model = Proposal
        fields = ['freelancer', 'proposed_price', 'status']  

    def validate_freelancer(self, value):
        try:
            return Freelancer.objects.get(user__username=value)
        except Freelancer.DoesNotExist:
            raise serializers.ValidationError(f"Freelancer '{value}' not found.")

    def create(self, validated_data):
        freelancer = validated_data.pop('freelancer')
        return Proposal.objects.create(freelancer=freelancer, **validated_data)


class FreelancerProposalSerializer(serializers.ModelSerializer):
    client = serializers.SerializerMethodField()
    service = serializers.SerializerMethodField()

    class Meta:
        model = Proposal
        fields = [
            "id", 'client', 'service',
            'proposal_date', 'proposed_price',"status" 
        ]
    
    def get_client(self, obj):
        return obj.client.user.username
    
    def get_service(self, obj):
        return{
            "title": obj.service.title,
            "description": obj.service.description,
            "price": str(obj.service.price),
        }
