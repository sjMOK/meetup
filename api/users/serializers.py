from rest_framework import serializers
from rest_framework.exceptions import APIException

from .models import User


class UserTypeSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    possible_duration = serializers.IntegerField(read_only=True)


class UserDepartmentSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'user_no', 'password', 'name', 'email', 'user_type', 'department']
        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 8,
            },
            'department': {
                'required': True
            }
        }

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['user_type'] = UserTypeSerializer(instance.user_type).data
        ret['department'] = UserDepartmentSerializer(instance.department).data

        return ret

    def validate_password(self, value):
        if self.instance is not None:
            raise APIException('Cannot update password with UserSerializer instance.')

        return value
    

class UserNoshowSerializer(serializers.ModelSerializer):
    noshow = serializers.IntegerField()

    class Meta:
        model = User
        fields = ['id', 'user_no', 'name', 'user_type', 'noshow']

    # def to_representation(self, instance):
    #     ret = super().to_representation(instance)
    #     ret['user_type'] = UserTypeSerializer(instance.user_type).data

    #     return ret
    


class LoginSerializer(serializers.Serializer):
    user_no = serializers.CharField(write_only=True, trim_whitespace=False)
    password = serializers.CharField(write_only=True, trim_whitespace=False)


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(min_length=8, max_length=128)
    new_password = serializers.CharField(min_length=8, max_length=128)

    def validate_current_password(self, value):
        if not self.instance.check_password(value):
            raise serializers.ValidationError('The current password not matched.')

        return value

    def validate(self, attrs):
        current_password, new_password = attrs['current_password'], attrs['new_password']
        if current_password == new_password:
            raise serializers.ValidationError('The new password is same as the current password.')

        return attrs
