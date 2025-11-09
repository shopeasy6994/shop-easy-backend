from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, OTPVerification
from customers.models import CustomerProfile, CustomerAddress

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'user_type']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                try:
                    user_obj = User.objects.get(email=username)
                    user = authenticate(username=user_obj.username, password=password)
                except User.DoesNotExist:
                    pass
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
            return attrs
        raise serializers.ValidationError('Must provide username and password')

class CustomerPasswordLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        password = attrs.get('password')
        if phone_number and password:
            try:
                user = User.objects.get(phone_number=phone_number, user_type='customer')
                auth_user = authenticate(username=user.username, password=password)
                if not auth_user:
                    raise serializers.ValidationError("Incorrect password.")
                if not auth_user.is_active:
                    raise serializers.ValidationError("User account is disabled.")
                attrs['user'] = auth_user
                return attrs
            except User.DoesNotExist:
                raise serializers.ValidationError("User with this phone number not found.")
        raise serializers.ValidationError("Must provide both phone number and password.")

class OTPRequestSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    
    def validate_phone_number(self, value):
        if not value.startswith('+'):
            raise serializers.ValidationError("Phone number must start with country code (+)")
        cleaned_number = ''.join(filter(str.isdigit, value[1:]))
        if len(cleaned_number) < 10:
            raise serializers.ValidationError("Invalid phone number")
        return value

class OTPVerificationSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    otp_code = serializers.CharField(max_length=6)
    name = serializers.CharField(max_length=150, required=False)
    
    def validate_otp_code(self, value):
        if not value.isdigit() or len(value) != 6:
            raise serializers.ValidationError("OTP must be 6 digits")
        return value

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                 'phone_number', 'user_type', 'is_phone_verified', 'created_at']
        read_only_fields = ['id', 'username', 'user_type', 'is_phone_verified', 'created_at']

class TokenSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
    user = UserProfileSerializer()
    token_type = serializers.CharField(default='Bearer')
    expires_in = serializers.IntegerField()
    
    def create(self, validated_data):
        user = validated_data['user']
        refresh = RefreshToken.for_user(user)
        return {
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'user': user,
            'token_type': 'Bearer',
            'expires_in': 1800,
        }

class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value

class ProfileSetupSerializer(serializers.Serializer):
    setup_token = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    gender = serializers.ChoiceField(choices=CustomerProfile.GENDER_CHOICES)
    age = serializers.IntegerField(min_value=14, max_value=100)
    occupation = serializers.ChoiceField(choices=CustomerProfile.OCCUPATION_CHOICES)
    address_line1 = serializers.CharField(max_length=255)
    address_line2 = serializers.CharField(max_length=255, required=False, allow_blank=True)
    landmark = serializers.CharField(max_length=255, required=False, allow_blank=True)
    city = serializers.CharField(max_length=100)
    state = serializers.CharField(max_length=100)
    pincode = serializers.CharField(max_length=6)

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        return attrs

    def validate_pincode(self, value):
        if not value.isdigit() or len(value) != 6:
            raise serializers.ValidationError("Pincode must be a 6-digit number.")
        return value

# --- NEW SERIALIZERS FOR FORGOT PASSWORD ---

class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer for requesting a password reset OTP.
    """
    phone_number = serializers.CharField(max_length=15)

    def validate_phone_number(self, value):
        if not User.objects.filter(phone_number=value, user_type='customer').exists():
            raise serializers.ValidationError("No active customer account found with this phone number.")
        return value

class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for confirming the password reset.
    """
    reset_token = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return attrs