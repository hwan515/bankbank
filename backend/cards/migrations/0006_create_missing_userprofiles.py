from django.db import migrations


def create_missing_profiles(apps, schema_editor):
    """기존 사용자 중 UserProfile이 없는 경우 생성"""
    User = apps.get_model('accounts', 'User')
    UserProfile = apps.get_model('cards', 'UserProfile')

    for user in User.objects.all():
        UserProfile.objects.get_or_create(user=user)


def reverse_func(apps, schema_editor):
    """Reverse: 아무 작업도 하지 않음 (데이터 삭제 방지)"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('cards', '0005_remove_primary_category'),
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_missing_profiles, reverse_func),
    ]
