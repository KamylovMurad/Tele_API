from rest_framework import serializers
from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    entered_invite = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['phone_number', 'invite_code', 'entered_invite']

    def get_entered_invite(self, obj):
        if obj.entered_invite:
            return {
                'invite_code': obj.entered_invite.invite_code
            }
        else:
            return None


class SendCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['phone_number', ]


class VerifyCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'verification_code', ]