from rest_framework import serializers
from .models import User, Information
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'greeting', 'age', 'sex']
    
class InformationSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = Information
        fields = ['id', 'title', 'content', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']