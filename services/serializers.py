from rest_framework import serializers
from .models import Category, Skill, Service, Proposal
from django.db import transaction
from users.models import Freelancer
from django.db.models import Prefetch


class SkillSerializer(serializers.ModelSerializer):
    """
    Serializer for Skill model.
    Serializes 'id' and 'name' of a skill.
    """

    class Meta:
        model = Skill
        fields = ['id', 'name']

class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for Category model.
    Includes nested SkillSerializer for all skills related to the category.
    Fields: id, name, and skills (read-only).
    """

    skills = SkillSerializer(read_only = True, many=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'skills']

class ServiceSerializer(serializers.ModelSerializer):
    """
    Serializer for Service model with custom create logic.

    - Serializes fields including freelancer username, title, description, 
      price, active status,freelancer's skills, and service categories.
    - On creation, automatically associates categories based on the freelancer's skills.
    """

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
        """
        Create a Service instance associated with the authenticated freelancer.
        Automatically links categories related to freelancer's skills.
        Uses atomic transaction to ensure integrity.
        """

        freelancer = self.context['request'].user.freelancer

        freelancer_skills = freelancer.skills.all()
        related_categories = Category.objects.filter(skills__in=freelancer_skills)

        with transaction.atomic():
            service = Service.objects.create(
                freelancer=freelancer, 
                **validated_data
            )
            service.categories.set(related_categories)

        return service

    def get_freelancer(self, obj):
        """
        Returns the username of the freelancer who owns the service.
        """
        return obj.freelancer.user.username

    def get_skills(self, obj):
        """
        Returns list of skills  of the freelancer linked to service
        """
        skills = obj.freelancer.skills.all()
        return [skill.name for skill in skills]

    def get_categories(self, obj):
        """
        Returns list of category  of the freelancer linked to service
        """
        return [category.name for category in obj.categories.all()]


class FreelancerServiceDetailSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for detailed view of a Service.

    Includes freelancer username, title, description, price, active status,
    freelancer's skills, and categories.
    """

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
        """
        Returns the username of the freelancer who owns the service.
        """
        return obj.freelancer.user.username
    
    def get_categories(self, obj):
        """
        Returns list of category  of the freelancer linked to service
        """
        return [category.name for category in obj.categories.all()]
    
    def get_skills(self, obj):
        """
        Returns list of skills  of the freelancer linked to service
        """
        return [skills.name for skills in obj.freelancer.skills.all()]


class ServiceSearchSerializer(serializers.Serializer):
    """
    Serializer for search filters on services.

    Accepts optional lists of categories and skills (as strings) for filtering.
    """
    categories = serializers.ListField(
        child = serializers.CharField(),
        required = False
    )
    skills = serializers.ListField(
        child = serializers.CharField(),
        required = False
    )
     
class ProposalCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating Proposal instances.

    Accepts freelancer username as input, validates existence,
    and creates proposal linked to that freelancer.
    """

    freelancer = serializers.CharField(write_only=True)

    class Meta:
        model = Proposal
        fields = ['freelancer', 'proposed_price', 'status']  

    def validate_freelancer(self, value):
        """
        Validates that the freelancer with the given username exists.
        Raises ValidationError if not found.
        """

        freelancer = Freelancer.objects.filter(
            user__username=value
        ).first()
        if not freelancer:
            raise serializers.ValidationError(f"Freelancer '{value}' not found.")

        return freelancer

    def create(self, validated_data):
        """
        Creates a Proposal instance, linking to the Freelancer instance.
        """

        freelancer = validated_data.pop('freelancer')
        return Proposal.objects.create(freelancer=freelancer, **validated_data)


class FreelancerProposalSerializer(serializers.ModelSerializer):
    """
    Serializer for Proposal model for freelancer's view.

    Serializes proposal id, client username, service details (title, description, price),
    proposal date, proposed price, and status.
    """

    client = serializers.SerializerMethodField()
    service = serializers.SerializerMethodField()

    class Meta:
        model = Proposal
        fields = [
            "id", 'client', 'service',
            'proposal_date', 'proposed_price',"status" 
        ]
    
    def get_client(self, obj):
        """
        Returns the username of the client who made the proposal.
        """
        return obj.client.user.username
    
    def get_service(self, obj):
        """
        Returns a dict of service details:
        title, description, and price (stringified).
        """

        return{
            "title": obj.service.title,
            "description": obj.service.description,
            "price": str(obj.service.price),
        }
