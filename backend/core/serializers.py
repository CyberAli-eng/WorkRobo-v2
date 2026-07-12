from rest_framework import serializers
from .models import Credential


class CredentialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Credential
        fields = ("id", "name", "provider", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")
class CredentialCreateSerializer(serializers.ModelSerializer):
    value = serializers.CharField(write_only=True, required=True, allow_blank=False)

    class Meta:
        model = Credential
        fields = ("id", "name", "provider", "value", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")

    def create(self, validated_data):
        # 1. Pop out the raw unencrypted value string
        plaintext = validated_data.pop("value")
        
        # 2. Extract user safely whether it comes from validated_data or extra kwargs
        user = validated_data.pop("user", None) or self.context["request"].user
        
        # 3. Build the instance explicitly
        cred = Credential(user=user, **validated_data)
        
        # 4. Encrypt into the target model storage text field safely
        cred.set_value(plaintext)
        cred.save()
        return cred

    def update(self, instance, validated_data):
        if "value" in validated_data:
            plaintext = validated_data.pop("value")
            instance.set_value(plaintext)
        return super().update(instance, validated_data)