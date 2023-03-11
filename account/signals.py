from .models import Account_HomeOwner
from .models import Account_Professional
from django.db.models.signals import post_delete
from django.dispatch import receiver

@receiver(post_delete, sender=Account_HomeOwner)
def delete_related_user(sender, instance, **kwargs):
    print("Page Post_Delete")
    instance.user.delete()
    
@receiver(post_delete, sender=Account_Professional)
def delete_related_user(sender, instance, **kwargs):
    print("Page Post_Delete")
    instance.user.delete()