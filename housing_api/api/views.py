from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from users.models import User

from .permissions import IsAdmin, IsModerator
from .serializers import SignUpSerializer, UserCreateSerializer, UserSerializer
from .tasks import send_confirmation_code_task
from .utils import generate_conf_code
from .validators import validate_email_and_username_exist


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def singup(request):
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid()
    email, username, password = serializer.validated_data.values()
    if not User.objects.filter(email=email, username=username).exists():
        validate_email_and_username_exist(
            email=email,
            username=username
        )
        user = User.objects.create_user(
            username=username,
            email=email,
        )
        user.set_password(password)
        user.save()
    user = User.objects.get(username=username)
    conf_code = generate_conf_code(user)
    send_confirmation_code_task(username=username, email=email, code=conf_code)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


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
