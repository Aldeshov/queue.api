import random

from rest_framework import serializers
from django.contrib.auth.models import User
from app.models import Queue, Member


class UserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name')


class QueueSerializer(serializers.Serializer):
    title = serializers.CharField()
    owner = UserSerializer(read_only=True)
    code = serializers.IntegerField(read_only=True)
    quantity = serializers.IntegerField(read_only=True)

    def update(self, instance, validated_data):
        return instance

    def create(self, validated_data):
        code = random.randint(11111111, 99999999)
        while Queue.objects.filter(code=code):
            code = random.randint(11111111, 99999999)

        validated_data.setdefault('code', code)
        validated_data.setdefault('owner', self.context.get('owner'))
        queue = Queue.objects.create(**validated_data)
        return queue


class MemberSerializer(serializers.Serializer):
    place = serializers.IntegerField(read_only=True)
    user = UserSerializer(read_only=True)
    active = serializers.BooleanField(read_only=True)
    comment = serializers.CharField(allow_blank=True)

    def update(self, instance, validated_data):
        instance.comment = validated_data.get('comment')
        instance.save()
        return instance

    def create(self, validated_data, **kwargs):
        validated_data.setdefault('queue', self.context.get('queue'))
        validated_data.setdefault('user', self.context.get('user'))
        validated_data.setdefault('place', validated_data.get('queue').quantity + 1)

        member = Member.objects.create(**validated_data)
        return member
