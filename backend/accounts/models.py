from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    age = models.PositiveIntegerField(null=True, blank=True)

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