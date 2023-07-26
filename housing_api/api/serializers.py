import base64

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.files.base import ContentFile
from djmoney.contrib.django_rest_framework import MoneyField
from properties.models import Image, Location, Property, RentDetails
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .validators import validate_username

User = get_user_model()


class Base64ImageField(serializers.ImageField):

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254, required=True)
    new = serializers.CharField(required=True, validators=[validate_password])
    new_retype = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new'] != attrs['new_retype']:
            raise serializers.ValidationError(
                {'new': 'Passwords do not match'}
            )
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    old = serializers.CharField(required=True)
    new = serializers.CharField(required=True, validators=[validate_password])
    new_retype = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['old'] == attrs['new']:
            raise serializers.ValidationError(
                {'new': 'New password must be different from old password'}
            )
        if not self.context['request'].user.check_password(attrs['old']):
            raise serializers.ValidationError(
                {'old': 'Incorrect password'}
            )
        if attrs['new'] != attrs['new_retype']:
            raise serializers.ValidationError(
                {'new': 'Passwords do not match'}
            )
        return attrs


class SignUpSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=254, required=True)
    username = serializers.CharField(
        max_length=30,
        required=True,
        validators=[validate_username]
    )
    password = serializers.CharField(
        required=True,
        validators=[validate_password]
    )

    class Meta:
        model = User
        fields = ('email', 'username', 'password')


class GetTokenSerializer(serializers.Serializer):

    email = serializers.EmailField(max_length=254, required=True)
    password = serializers.CharField(required=True)

    def validate(self, attrs):
        try:
            user = User.objects.get(email=attrs['email'])
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'Invalid credentials'
            )
        if not user.check_password(attrs['password']):
            raise serializers.ValidationError(
                'Invalid credentials'
            )
        if not user.is_active:
            raise serializers.ValidationError(
                'Account is not active'
            )
        return attrs


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
        fields = ('__all__')
        model = User


class ImageSerializer(serializers.ModelSerializer):

    image = Base64ImageField()

    class Meta:
        fields = ('id', 'image', 'property')
        model = Image


class LocationSerializer(serializers.ModelSerializer):

    class Meta:
        exclude = ('property',)
        model = Location


class RentDetailsSerializer(serializers.ModelSerializer):
    rent_price = MoneyField(
        max_digits=14, decimal_places=2,
        default_currency='USD'
    )
    deposit_amount = MoneyField(
        max_digits=14, decimal_places=2,
        default_currency='USD'
    )

    class Meta:
        exclude = ('property',)
        model = RentDetails


class PropertyCreateSerializer(serializers.ModelSerializer):
    price = MoneyField(max_digits=14, decimal_places=2, default_currency='USD')
    rent_details = RentDetailsSerializer(required=False)
    location = LocationSerializer(required=False)

    class Meta:
        model = Property
        exclude = ('owner', 'id')

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        new_ret = ret.copy()
        for key in ret:
            if ret[key] is None:
                new_ret.pop(key)
        return new_ret


class PropertySerializer(serializers.ModelSerializer):
    price = MoneyField(max_digits=14, decimal_places=2, default_currency='USD')
    images = ImageSerializer(many=True, read_only=True)
    rent_details = serializers.SerializerMethodField()
    location = LocationSerializer(read_only=True)
    for_rent = serializers.SerializerMethodField()
    owner = serializers.SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = Property
        fields = ('__all__')

    def get_rent_details(self, obj):
        try:
            return RentDetailsSerializer(obj.rent_details).data
        except RentDetails.DoesNotExist:
            return None

    def get_for_rent(self, obj):
        return self.get_rent_details(obj) is not None
