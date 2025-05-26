from rest_framework import serializers
from .models import User, Freelancer, Client
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from services.models import Skill, Category
from django.db import transaction, IntegrityError


signer = TimestampSigner()

class UserRegistrationSerializers(serializers.ModelSerializer):
    """
    Serializer for registering a new user.

    Fields:
        id, username, email, phone, password

    Validates:
        - Minimum 8-character password
        - One lowercase, one uppercase, one digit, one special char
        - No adjacent repeated characters
    """
    class Meta: 
        model = User
        fields = ["id", "username", "email", "phone", "password"]
    
    def validate_password(self, password):
        """Enforce password validation and pattern of password"""

        if len(password) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")

        has_lower = any(c.islower() for c in password)
        has_upper = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()-+" for c in password)
        no_adjacent_duplicates = all(password[i] != password[i + 1] for i in range(len(password) - 1))

        if not all([has_lower, has_upper, has_digit, has_special, no_adjacent_duplicates]):
            raise serializers.ValidationError(
                "Password must contain at least one lowercase, one uppercase, one digit, "
                "one special character (!@#$%^&*()-+), and no adjacent repeated characters."
            )   

        return password
    
    def create(self, validated_data):
        """Create user with hashed password"""

        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user 

class FreelancerRegistrationSerializers(UserRegistrationSerializers):
    """
    Serializer for freelancer registration.

    Adds:
        - profile (optional)
        - skills (validated against Skill model)
    """

    profile = serializers.CharField(required=False, allow_blank=True)
    skills = serializers.ListField(child=serializers.CharField(), write_only=True)

    class Meta(UserRegistrationSerializers.Meta):
        fields = UserRegistrationSerializers.Meta.fields + ['profile', 'skills']
        read_only_fields = ["rating"]

    def validate_skills(self, skill_list):
        """Ensure all submitted skills exist."""

        found_skills = Skill.objects.filter(name__in=skill_list)
        skill_set = set(skill_list)
        found_names = {skill.name for skill in found_skills}

        invalid_skills = skill_set - found_names

        if invalid_skills:
            raise serializers.ValidationError(f"Invalid skill(s): {', '.join(invalid_skills)}")
        return list(found_skills)

    def create(self, validated_data):
        """Create user + freelancer + assign validated skills."""

        profile = validated_data.pop('profile', '')
        skills = validated_data.pop('skills', [])
        
        with transaction.atomic():
            user = super().create(validated_data)
            freelancer = Freelancer.objects.create(
                user=user,
                profile=profile,
            )
            freelancer.skills.set(skills)

        return freelancer  
        

class ClientRegistrationSerializer(UserRegistrationSerializers):
    """
    Serializer for client registration.

    Adds:
        - preferred_categories (optional)
    """

    preferred_categories = serializers.ListField(required=False, child=serializers.CharField())

    class Meta(UserRegistrationSerializers.Meta):
        fields = UserRegistrationSerializers.Meta.fields + ['preferred_categories']

    def validate_preferred_categories(self, value):
        """Ensure all submitted categories exist."""

        categories = Category.objects.filter(name__in=value)
        category_set = set(value)
        category_names = {category.name for category in categories}

        invalid_category = category_set - category_names

        if invalid_category:
            raise serializers.ValidationError(f"Invalid categories: {', '.join(invalid_category)}")

        return list(categories)

    def create(self, validated_data):
        """Create user + client + assign validated preferred categories."""

        preferred_categories = validated_data.pop('preferred_categories', [])
        
        with transaction.atomic():
            user = super().create(validated_data)
            client = Client.objects.create(user=user)
            client.preferred_categories.set(preferred_categories)  

        return client

    
class SkillSerializer(serializers.ModelSerializer):
    """Serializer for Skill model."""
    class Meta:
        model = Skill
        fields = ['name']

class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for Category model.

    Includes nested SkillSerializer for associated skills.
    """

    skills = SkillSerializer(source='skills', many=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'skills']
        
class FreelancerProfileSerializer(serializers.ModelSerializer):
    """
    Serializer to expose freelancer profile with user info and related data.

    Fields:
        id, username, email, phone, profile, skills, categories, rating
    """

    id = serializers.CharField(source='user.id')
    username = serializers.CharField(source='user.username')
    email = serializers.EmailField(source='user.email')
    phone = serializers.CharField(source='user.phone')
    skills = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()

    class Meta:
        model = Freelancer
        fields = ['id', 'username', 'email', 'phone', 'profile', 
                  'categories','skills', 'rating'
                  ]
    
    def get_categories(self, obj):
        """Fetch unique categories for the freelancer's skills."""
        return sorted(
            {skill.category.name for skill in obj.skills.all() if skill.category}
        )

    def get_skills(self, obj):
        """Fetch unique skills names for the freelancer."""
        return sorted({skill.name for skill in obj.skills.all()})
    

class ClientProfileSerializer(serializers.ModelSerializer):
    """
    Serializer to expose client profile with user info and preferred categories.
    """

    id = serializers.CharField(source='user.id')
    username = serializers.CharField(source='user.username')
    email = serializers.EmailField(source='user.email')
    phone = serializers.CharField(source='user.phone')
    preferred_categories = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = ['id', 'username', 'email', 
                  'phone', 'preferred_categories'
                  ]
    
    def validate_preferred_categories(self, value):
        """Validate preferred categories (redundant here — safe to remove)."""

        found_categories = Category.objects.filter(name__in=value)
        category_set = set(value)
        found_names = {category.name for category in found_categories}

        invalid_categories = category_set - found_names

        if invalid_categories:
            raise serializers.ValidationError(f"Invalid categories")

        return list(found_categories)
    
    def get_preferred_categories(self, obj):
        """Return list of preferred category names."""

        return [category.name for category in obj.preferred_categories.all()]

        
class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer for requesting a password reset.

    Validates:
        - That a user with the given email exists
    """

    email = serializers.EmailField()

    def validate_email(self, email):
        """Ensure a user with the email exists."""

        if not User.objects.filter(email = email).exists():
            raise serializers.ValidationError("User with this email doesn't exists")
        return email
    
class PasswordResetSerializer(serializers.Serializer):
    """
    Serializer for resetting password using a signed token.

    Validates:
        - Token is valid and not expired
    """

    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        """Check token validity and extract the user."""

        token = data.get('token')
        try:
            user_id = signer.unsign(token, max_age=3600)  
            user = User.objects.get(pk=user_id)
        except (BadSignature, SignatureExpired, User.DoesNotExist):
            raise serializers.ValidationError({"token": "Invalid or expired token."})

        self.user = user
        return data

    def save(self):
        """Reset the user's password."""
        password = self.validated_data['new_password']
        self.user.set_password(password)
        self.user.save()