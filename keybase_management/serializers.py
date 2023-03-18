from rest_framework import serializers
from .models import Keybase


class KeybaseSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Keybase
        fields = '__all__'
