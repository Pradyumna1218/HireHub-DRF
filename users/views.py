from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    ClientRegistrationSerializer,
    FreelancerRegistrationSerializers,
    FreelancerProfileSerializer,
    ClientProfileSerializer,
    PasswordResetRequestSerializer, 
    PasswordResetSerializer
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import User, Freelancer, Client, PasswordResetToken
from django.core.signing import TimestampSigner
from .tasks import send_password_reset_email
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta

signer = TimestampSigner()

class FreelancerRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = FreelancerRegistrationSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Freelancer registered successfully"}, status= status.HTTP_201_CREATED)


class ClientRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ClientRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Client registered successfully"}, status= status.HTTP_201_CREATED)


class FreelancerProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        freelancer = get_object_or_404(Freelancer, user = request.user)
        serializer = FreelancerProfileSerializer(freelancer)
        return Response(serializer.data)
        
    
    def patch(self, request):
        freelancer = get_object_or_404(Freelancer, user = request.user)
        serializer = FreelancerProfileSerializer(freelancer, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

class ClientProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        client = get_object_or_404(Client, user = request.user)
        serializer = ClientProfileSerializer(client)
        return Response(serializer.data)
    

    def patch(self, request):
        client = get_object_or_404(Client, user = request.user)
        serializer = ClientProfileSerializer(client, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)  
        
class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        user = get_object_or_404(User, email=email)

        token = signer.sign(user.pk)
        reset_link = f"http://localhost:8000/reset/?token={token}"

        reset_token = PasswordResetToken.objects.create(
            user=user,
            token=token,
            used=False  
        )

        send_password_reset_email.delay(email, reset_link)

        print(f"Reset link for {email}: {reset_link}")

        return Response(
            {"message": "Password reset link sent. Check your email."}, 
            status=status.HTTP_200_OK
        )


class PasswordResetView(APIView):
    def post(self, request):
        token = request.query_params.get('token')
        if not token:
            return Response(
                {"error": "Missing token in URL."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        token_obj = get_object_or_404(
            PasswordResetToken,
            token=token,
            used=False  
        )

        if token_obj.created_at < timezone.now() - timedelta(hours=1):
            return Response(
                {"error": "Token has expired."},
                status=status.HTTP_400_BAD_REQUEST
            )
        data = request.data.copy()
        data['token'] = token
        serializer = PasswordResetSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        token_obj.used = True
        token_obj.save()


        return Response(
            {"message": "Password reset successful."},
            status=status.HTTP_200_OK
        )

        
