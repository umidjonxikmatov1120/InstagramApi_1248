from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password

from accounts.models import VIA_EMAIL, VIA_PHONE, NEW
from accounts.utils import check_email_or_phone


class SignUpSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    def __init__(self, *args, **kwargs):
        super(SignUpSerializer, self).__init__(*args, **kwargs)
        self.fields['email_phone_number'] = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = (
            'id',
            'auth_type',
            'auth_status',
        )
        extra_kwargs = {
            'auth_type': {'read_only': True, 'required': False},
            'auth_status': {'read_only': True, 'required': False},
        }

    def create(self, validated_data):
        user = super(SignUpSerializer, self).create(validated_data)
        if user.auth_type == VIA_EMAIL:
            code = user.create_verify_code(VIA_EMAIL)
        elif user.auth_type == VIA_PHONE:
            code = user.create_verify_code(VIA_PHONE)
        user.save()
        return user

    def validate(self, data):
        super(SignUpSerializer, self).validate(data)
        data = self.auth_validate(data)
        return data

    @staticmethod
    def auth_validate(data):
        user_input = str(data.get('email_phone_number')).lower()
        input_type = check_email_or_phone(user_input)
        if input_type == 'email':
            data = {
                'auth_type': VIA_EMAIL,
                'email': user_input,
            }
        elif input_type == 'phone':
            data = {
                'auth_type': VIA_PHONE,
                'phone_number': user_input,
            }
        else:
            data = {
                "success": False,
                "message": "Email yoki telefon raqamni to'g'ri kiriting."
            }
            raise ValidationError(data)

        return data

    def to_representation(self, instance):
        data = super(SignUpSerializer, self).to_representation(instance)
        data.update(instance.token())
        return data

    def validate_email_phone_number(self, value):
        value = value.lower()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                {
                    "success": False,
                    "message": "Bunday email allaqachon mavjud!"
                }
            )
        elif User.objects.filter(phone=value).exists():
            raise serializers.ValidationError(
                {
                    "success": False,
                    "message": "Bunday telefon raqam allaqachon mavjud!"
                }
            )
        return value

