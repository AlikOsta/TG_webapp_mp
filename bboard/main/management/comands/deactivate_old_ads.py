from django.db.models.signals import post_save
from django.dispatch import receiver
from main.models import Bb

@receiver(post_save, sender=Bb)
def deactivate_old_ads(sender, instance, **kwargs):
    instance.check_expiration()
