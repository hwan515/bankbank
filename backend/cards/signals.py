from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """회원가입 시 UserProfile 자동 생성"""
    if created:
        from .models import UserProfile
        UserProfile.objects.get_or_create(user=instance)
