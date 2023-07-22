from django.contrib.auth import get_user_model
from rest_framework import serializers

from .validators import validate_username

User = get_user_model()


class SignUpSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=254, required=True)
    username = serializers.CharField(
        max_length=30,
        required=True,
        validators=[validate_username]
    )

    class Meta:
        model = User
        fields = ('email', 'username', 'password')


class UserCreateSerializer(serializers.ModelSerializer):

    class Meta:
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'phone_number',
        )
        model = User

    def create(self, validated_data):
        pw = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(pw)
        user.save()
        return user

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret.pop('password')
        return ret


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'phone_number',
        )
        model = User
        read_only_fields = ('role',)
