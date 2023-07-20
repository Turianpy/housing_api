from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


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
        read_only_fields = ('role',)
        extra_kwargs = {'password': {'write_only': True}}

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
