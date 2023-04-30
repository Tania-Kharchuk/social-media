from django.contrib.auth import get_user_model
from rest_framework import serializers

from user.models import Follow


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "password",
            "is_staff",
        )
        read_only_fields = ("is_staff",)
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update a user, set the password correctly and return it"""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
        user.save()

        return user


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "is_staff",
            "nickname",
            "image",
            "bio",
        )
        read_only_fields = ("is_staff", "email")


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = "__all__"

    def validate(self, attrs):
        if self.instance in Follow.objects.all():
            raise serializers.ValidationError("You already follow this user")
        return attrs


class FollowingDetailSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="followed.email", read_only=True)

    class Meta:
        model = Follow
        fields = ("created_at", "user")


class FollowersDetailSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="follower.email", read_only=True)

    class Meta:
        model = Follow
        fields = ("created_at", "user")
