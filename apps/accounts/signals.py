from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, AgentProfile, BuyerProfile


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == User.Role.AGENT:
            AgentProfile.objects.get_or_create(
                user=instance,
                defaults={'agency_name': f"{instance.full_name} Properties"}
            )
        elif instance.role == User.Role.BUYER:
            BuyerProfile.objects.get_or_create(user=instance)
