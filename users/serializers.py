from rest_framework import serializers
from .models import User, Freelancer, Client
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from services.models import Skill, Category
from django.db import transaction, IntegrityError


signer = TimestampSigner()

class UserRegistrationSerializers(serializers.ModelSerializer):
    class Meta: 
        model = User
        fields = ["username", "email", "phone", "password"]
    
    def validate_skills(self, value):
        invalid_skills = []
        for skill_name in value:
            if not Skill.objects.filter(name=skill_name).exists():
                invalid_skills.append(skill_name)

        if invalid_skills:
            raise serializers.ValidationError(f"The following skills do not exist: {', '.join(invalid_skills)}")

        return value
    
    def validate_password(self, password):
        # if len(password) < 8:
        #     raise serializers.ValidationError("Password must be at least 8 characters long.")

        # has_lower = any(c.islower() for c in password)
        # has_upper = any(c.isupper() for c in password)
        # has_digit = any(c.isdigit() for c in password)
        # has_special = any(c in "!@#$%^&*()-+" for c in password)
        # no_adjacent_duplicates = all(password[i] != password[i + 1] for i in range(len(password) - 1))

        # if not all([has_lower, has_upper, has_digit, has_special, no_adjacent_duplicates]):
        #     raise serializers.ValidationError(
        #         "Password must contain at least one lowercase, one uppercase, one digit, "
        #         "one special character (!@#$%^&*()-+), and no adjacent repeated characters."
        #     )

        return password
    
    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user 

class FreelancerRegistrationSerializers(UserRegistrationSerializers):
    profile = serializers.CharField(required=False, allow_blank=True)
    skills = serializers.ListField(child=serializers.CharField(), write_only=True)
    rating = serializers.CharField(required=False, allow_blank=True, default = '0')
   

    class Meta(UserRegistrationSerializers.Meta):
        fields = UserRegistrationSerializers.Meta.fields + [ 
                  'profile', 'skills', 'rating'
                  ]
        read_only = ["rating"]

    def validate_skills(self, skill_list):
        validated_skills = []

        for skill_name in skill_list:
            try:
                skill = Skill.objects.get(name = skill_name)
                validated_skills.append(skill)
            except Skill.DoesNotExist:
                raise serializers.ValidationError(f"{skill} does not exists")
            
        return validated_skills


    def create(self, validated_data):
        profile = validated_data.pop('profile', '')
        skills = validated_data.pop('skills', [])
        rating = validated_data.pop('rating', '')

        try:
            with transaction.atomic():
                user = super().create(validated_data)

                freelancer = Freelancer.objects.create(
                    user=user,
                    profile=profile,
                    rating=rating
                )
                freelancer.skills.set(skills)
                return user  

        except (IntegrityError, serializers.ValidationError) as e:
            raise serializers.ValidationError({"detail": f"Freelancer registration failed: {str(e)}"})


class ClientRegistrationSerializer(UserRegistrationSerializers):
    preferred_categories = serializers.ListField(required=False, child = serializers.CharField())
    class Meta(UserRegistrationSerializers.Meta):
        fields = UserRegistrationSerializers.Meta.fields + ['preferred_categories']

    def validate_preferred_categories(self, value):
        invalid_categories = []
        for category_name in value:
            if not Category.objects.filter(name=category_name).exists():
                invalid_categories.append(category_name)

        if invalid_categories:
            raise serializers.ValidationError(f"The following categories do not exist: {', '.join(invalid_categories)}")

        return value

    def create(self, validated_data):
        preferred_categories_name = validated_data.pop('preferred_categories', [])
        
        try:
            with transaction.atomic():
                user = super().create(validated_data)
                client = Client.objects.create(user=user)

                for category_name in preferred_categories_name:
                    category, _ = Category.objects.get_or_create(name=category_name)
                    client.preferred_categories.add(category)

                return user

        except(IntegrityError, serializers.ValidationError) as e:
            raise serializers.ValidationError({"detail": f"Client registration failed: {str(e)}"})

    
class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['name']

class CategorySerializer(serializers.ModelSerializer):
    skills = SkillSerializer(source='skill_set', many=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'skills']
        
class FreelancerProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    email = serializers.EmailField(source='user.email')
    phone = serializers.CharField(source='user.phone')
    skills = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()

    class Meta:
        model = Freelancer
        fields = ['username', 'email', 'phone', 'profile', 
                  'categories','skills', 'rating'
                  ]

    def validate_skills(self, value):
        """Validate that all skills exist in database."""

        validated_skills = []
        for skill_name in value:
            try:
                skill_instance = Skill.objects.get(name=skill_name)
                validated_skills.append(skill_instance)
            except Skill.DoesNotExist:
                raise serializers.ValidationError(f"Skill '{skill_name}' does not exist.")
        
        return validated_skills
    
    def validate_categories(self, value):
        """Validate that all categories exist in the database."""

        validated_categories = []
        for category_name in value:
            try:
                category_instance = Category.objects.get(name=category_name)
                validated_categories.append(category_instance)
            except Category.DoesNotExist:
                raise serializers.ValidationError(f"Category '{category_name}' does not exist.")
        
        return validated_categories
    
    def get_categories(self, obj):
        category_names = set()
        for skill in obj.skills.all():
            if skill.category:
                category_names.add(skill.category.name)
        return sorted(list(category_names))
    
    def get_skills(self, obj):
        skill_names = set(skill.name for skill in obj.skills.all())
        return sorted(list(skill_names))
    

class ClientProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    email = serializers.EmailField(source='user.email')
    phone = serializers.CharField(source='user.phone')
    preferred_categories = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = ['username', 'email', 
                  'phone', 'preferred_categories'
                  ]
    
    def validate_preferred_categories(self, value):
        if not all(Category.objects.filter(id=category.id).exists() for category in value):
            raise serializers.ValidationError("One or more categories are invalid.")
        return value
    
    def get_preferred_categories(self, obj):
        return [category.name for category in obj.preferred_categories.all()]

        
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, email):
        if not User.objects.filter(email = email).exists():
            raise serializers.ValidationError("User with this email doesn't exists")
        return email
    
class PasswordResetSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        token = data.get('token')
        try:
            user_id = signer.unsign(token, max_age=3600)  # 1 hour expiry
            user = User.objects.get(pk=user_id)
        except (BadSignature, SignatureExpired, User.DoesNotExist):
            raise serializers.ValidationError({"token": "Invalid or expired token."})

        self.user = user
        return data

    def save(self):
        password = self.validated_data['new_password']
        self.user.set_password(password)
        self.user.save()