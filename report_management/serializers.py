from rest_framework import serializers
from .models import ReportsNotes, Brief


class NotesSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReportsNotes
        fields = '__all__'


class BriefSerializer(serializers.ModelSerializer):

    class Meta:
        model = Brief
        fields = '__all__'
