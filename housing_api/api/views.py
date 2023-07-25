import jwt
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from properties.models import Property, RentDetails, Image, Location
from rest_framework import permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.parsers import MultiPartParser, JSONParser
from users.models import User

from .permissions import IsAdmin, IsModerator
from .serializers import (ChangePasswordSerializer, GetTokenSerializer,
                          PropertyCreateSerializer, PropertySerializer,
                          ResetPasswordSerializer, SignUpSerializer,
                          UserCreateSerializer, UserSerializer)
from .tasks import send_activation_email_task, send_reset_password_email_task
from .utils import generate_user_token, get_tokens
from .validators import validate_email_and_username_exist


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def singup(request):
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email, username, password = serializer.validated_data.values()
    validate_email_and_username_exist(
        email=email,
        username=username
    )
    user = User.objects.create_user(
        username=username,
        email=email,
        is_active=False
    )
    user.set_password(password)
    user.save()
    send_activation_email_task(
        username, email, generate_user_token(user)
    )
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def activate(request):
    token = request.query_params.get('token')
    if not token:
        return Response(
            {'error': 'Token not provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user = User.objects.get(email=payload['email'])
        if user.is_active:
            return Response(
                {"message": "User already activated"},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.is_active = True
        user.save()
        return Response(
            {"message": "Account successfully activated"},
            status=status.HTTP_200_OK
        )
    except jwt.ExpiredSignatureError:
        return Response(
            {'error': 'Activation link has expired'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except jwt.DecodeError:
        return Response(
            {'error': 'Invalid token'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except User.DoesNotExist:
        return Response(
            {'error': 'User with given email not found'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def get_token(request):
    serializer = GetTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(User, email=serializer.validated_data['email'])
    return Response(get_tokens(user), status=status.HTTP_200_OK)


class UserViewSet(ModelViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    action_to_serializer = {
        'create': UserCreateSerializer,
        'update': UserCreateSerializer,
    }
    permission_classes = [IsModerator | IsAdmin]

    def get_serializer_class(self):
        return self.action_to_serializer.get(
            self.action,
            self.serializer_class
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid()
        try:
            validate_password(request.data['password'])
        except ValidationError as e:
            return Response(
                {'error': e.messages},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=False,
        methods=['get', 'patch'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def me(self, request):
        if request.method == 'PATCH':
            if 'role' in request.data:
                return Response(
                    {'error': 'You cannot change your role here'},
                    status=status.HTTP_403_FORBIDDEN
                )
            serializer = self.get_serializer_class()(
                request.user,
                data=request.data,
                partial=True
            )
            serializer.is_valid()
            serializer.save()
            return Response(serializer.data)
        return Response(self.get_serializer_class()(request.user).data)

    @action(
        detail=False,
        methods=['patch', 'post'],
        permission_classes=[permissions.AllowAny]
    )
    def reset_password(self, request):
        if request.method == 'POST':
            email = request.data['email']
            if not email:
                return Response(
                    {'error': 'Email not provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user = get_object_or_404(User, email=email)
            send_reset_password_email_task(
                user.username,
                user.email,
                generate_user_token(user)
            )
            return Response(
                {'message': 'Reset password link sent'},
                status=status.HTTP_200_OK
            )
        if request.method == 'PATCH':
            token = request.query_params.get('token')
            if not token:
                return Response(
                    {'error': 'Token not provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            data = request.data
            try:
                payload = jwt.decode(
                    token,
                    settings.SECRET_KEY,
                    algorithms=['HS256']
                )
            except jwt.InvalidSignatureError:
                return Response(
                    {'error': 'Invalid token'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            data["email"] = payload['email']
            serializer = ResetPasswordSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            user = get_object_or_404(User, email=data['email'])
            user.set_password(serializer.validated_data['new'])
            user.save()
            return Response(
                {'message': 'Password reset successfully'},
                status=status.HTTP_200_OK
            )
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        methods=['PATCH'],
        detail=False,
        permission_classes=[permissions.IsAuthenticated]
    )
    def change_password(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.validated_data['new'])
        user.save()
        return Response(
            {'message': 'Password changed successfully'},
            status=status.HTTP_200_OK
        )

    @action(
        methods=['get'],
        detail=True,
        permission_classes=[permissions.IsAuthenticated]
    )
    def properties(self, request):
        user = self.get_object()
        properties = Property.objects.filter(owner=user)
        serializer = PropertySerializer(properties, many=True)
        return Response(serializer.data)


class PropertyViewSet(ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = Property.objects.all()
    parser_classes = [MultiPartParser, JSONParser]

    def get_serializer_class(self):
        if self.action == 'create':
            return PropertyCreateSerializer
        return PropertySerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)

        image_data = []
        for k, v in request.data.items():
            if k.startswith('image'):
                image_data.append({'image': v})
        validated_data = serializer.validated_data
        rent_details_data = validated_data.pop('rent_details', None)
        location_data = validated_data.pop('location', None)
        validated_data.pop('images', None)

        prop = Property.objects.create(**validated_data, owner=request.user)
        if rent_details_data is not None:
            print('rent_details true')
            RentDetails.objects.create(property=prop, **rent_details_data)
        if location_data is not None:
            print('location true')
            Location.objects.create(property=prop, **location_data)
        for image in image_data:
            Image.objects.create(property=prop, **image)
        prop.refresh_from_db()
        return Response(PropertySerializer(prop).data, status=status.HTTP_201_CREATED)

    @action(
        methods=['get'], detail=False,
        permission_classes=[permissions.IsAuthenticated]
    )
    def favorites(self, request):
        favorites = request.user.favorites.all()
        if not favorites:
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = PropertySerializer(favorites, many=True)
        return Response(serializer.data)

    @action(
        methods=['post', 'delete'], detail=True,
        permission_classes=[permissions.IsAuthenticated]
    )
    def favorite(self, request, pk):
        property = self.get_object()
        if request.method == 'DELETE':
            request.user.favorites.remove(property)
            return Response(status=status.HTTP_200_OK)
        request.user.favorites.add(property)
        return Response(status=status.HTTP_200_OK)

    @action(
        methods=['post'], detail=True,
        permission_classes=[permissions.IsAuthenticated]
    )
    def reserve(self, request, pk):
        pass
