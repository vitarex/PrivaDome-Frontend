""" Model Serializers. """
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied, ValidationError


class UserListSerializer(serializers.ModelSerializer):
    """ Serialize User objects. """
    admin = serializers.BooleanField(source='is_superuser', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'admin')


class UserCreateSerializer(serializers.ModelSerializer):
    """ Serialize incoming User create requests. """

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        """ Create a User with an email, username and password. """

        if 'email' in validated_data\
                and 'username' in validated_data\
                and 'password' in validated_data:
            user = User(
                email=validated_data['email'],
                username=validated_data['username']
            )
            user.set_password(validated_data['password'])
            user.save()
            return user
        else:
            raise ValidationError("Bad request")


class UserUpdateSerializer(serializers.ModelSerializer):
    """ Serialize incoming User update requests. """
    oldPassword = serializers.CharField()
    newPassword = serializers.CharField()

    class Meta:
        model = User
        fields = ('username', 'email', 'oldPassword',
                  'newPassword')
        extra_kwargs = {
            'newPassword': {'required': False},
            'email': {'required': False},
            'username': {'required': False}
            }

    def update(self, instance, validated_data):
        """ Update a User object. """

        if 'oldPassword' in validated_data:
            if instance.check_password(validated_data['oldPassword']):
                if 'email' in validated_data:
                    instance.email = validated_data['email']
                if 'username' in validated_data:
                    instance.username = validated_data['username']
                if 'newPassword' in validated_data:
                    instance.set_password(validated_data['newPassword'])
                instance.save()
                return instance
            else:
                raise PermissionDenied("Incorrect password")
        else:
            raise PermissionDenied("Password not provided")
