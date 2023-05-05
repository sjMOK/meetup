from django.db import models
from users.models import User
from django.utils.translation import gettext_lazy as _
class RoomImages(models.Model):
    id = models.BigAutoField(primary_key=True)
    image=models.ImageField(upload_to="images/", db_column="image")


class Room(models.Model):
    id = models.BigAutoField(primary_key=True)
    name=models.CharField(blank=False, max_length=100, null=False)
    discription=models.TextField()
    images = models.ForeignKey(RoomImages, on_delete=models.CASCADE, null=True)

class Reservation(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, related_name="reservation", on_delete=models.CASCADE, db_column="user_id")
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    
    class ReservationStatus(models.TextChoices):
        NRESERVED = 'NRES', _('NotReserved')
        RESERVED = 'RES', _('Reserved')
        BLOCKED = 'BLK', _('Blocked')

    reservation_status = models.CharField(
        max_length=16,
        choices=ReservationStatus.choices,
        default=ReservationStatus.NRESERVED,
    )



class DailyReservationCard(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateField(auto_now_add=True)
    room = models.ForeignKey(Room, related_name="reservation", on_delete=models.CASCADE, db_column="room_id")
    



