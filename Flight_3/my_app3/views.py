from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import authenticate
from .serializers import UserSerializer, LoginSerializer
from .models import CustomUser

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'Registration is done and your access token is valid for 5 mins only.',
                'access_token': str(refresh.access_token)
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RenewAccessTokenView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.access_token_used:
                return Response({'error': 'Access token has already been used. Cannot renew.'}, status=status.HTTP_400_BAD_REQUEST)
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'Your new access token is valid for 5 mins only.',
                'access_token': str(refresh.access_token)
            })
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            access_token = serializer.validated_data['access_token']

            try:
                user = CustomUser.objects.get(username=username)
            except CustomUser.DoesNotExist:
                return Response({'error': 'Invalid user. Register first'}, status=status.HTTP_400_BAD_REQUEST)

            if not user.check_password(password):
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

            if user.access_token_used:
                return Response({'error': 'Access token has already been used'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                token = AccessToken(access_token)
                if token['user_id'] != user.id:
                    return Response({'error': 'This access token is not active for this user'}, status=status.HTTP_400_BAD_REQUEST)
            except TokenError:
                return Response({'error': 'Invalid or expired access token'}, status=status.HTTP_400_BAD_REQUEST)

            user.access_token_used = True
            user.save()

            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'Login is successful. Your refresh token is valid for 1 day',
                'refresh_token': str(refresh)
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)