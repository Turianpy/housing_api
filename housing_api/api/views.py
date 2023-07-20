from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from users.models import User

from .permissions import IsAdmin, IsModerator
from .serializers import UserCreateSerializer, UserSerializer


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

    @action(detail=False, methods=['get', 'patch'])
    def me(self, request):
        if request.method == 'PATCH':
            if 'role' in request.data:
                return Response(
                    {'error': 'You cannot change your role here'},
                    status=status.HTTP_400_BAD_REQUEST
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
