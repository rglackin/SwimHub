from django.db.models.signals import pre_delete
from django.dispatch import receiver
from .models import SwimTime,PersonalBest

@receiver(pre_delete, sender=SwimTime)
def update_personal_best_on_delete(sender, instance, **kwargs):
    
    try:
        # Retrieve the personal best time for the given swim time
        personal_best = PersonalBest.objects.get(swim_time=instance)
    except PersonalBest.DoesNotExist:
        # If no personal best time exists for the given swim time, do nothing
        pass
    else:
        # Check if there are any other swim times with the same stroke type and distance as the current personal best
        other_times = SwimTime.objects.filter(
            swimmer=instance.swimmer,
            strokeType=instance.strokeType,
            distance=instance.distance
        ).exclude(id=instance.id)
        if other_times.exists():
            # If such swim times exist, update the personal best with the fastest swim time
            fastest_time = other_times.order_by('time').first()
            #print(fastest_time.id)
            personal_best.swim_time = fastest_time
            #print(personal_best)
            personal_best.save()
        else:
            # If no such swim times exist, delete the personal best
            personal_best.delete()