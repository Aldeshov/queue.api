from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Queue(models.Model):
    title = models.CharField(max_length=128)
    code = models.PositiveIntegerField(validators=[MinValueValidator(8), MaxValueValidator(8)], unique=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="queues")
    quantity = models.IntegerField(default=0)


class Member(models.Model):
    place = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    queue = models.ForeignKey(Queue, on_delete=models.CASCADE, related_name="members")
    active = models.BooleanField(default=True)
    comment = models.CharField(max_length=128, blank=True, default=None)
