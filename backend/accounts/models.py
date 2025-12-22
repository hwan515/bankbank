from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    age = models.PositiveIntegerField(null=True, blank=True)
    sex = models.CharField(max_length=1, choices=[('M','Male'),('F','Female')], null=True, blank=True)

    greeting = models.TextField(null=True, blank=True)

    # F03-3: 가입한 금융상품 목록
    deposit_products = models.ManyToManyField(
        'products.DepositProducts',
        related_name='subscribed_users',
        blank=True
    )
    saving_products = models.ManyToManyField(
        'products.SavingProducts',
        related_name='subscribed_users',
        blank=True
    )

class Information(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='infos') 
    title = models.TextField(max_length=100, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
