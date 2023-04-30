from django.db import models
from users.models import User
from django.utils.translation import gettext_lazy as _
class RoomImages(models.Model):
    id = models.AutoField(primary_key=True)
    image=models.ImageField(upload_to="images/")

    class Meta:
        db_table = 'room_images'

class Room(models.Model):
    id = models.AutoField(primary_key=True)
    name=models.CharField(help_text="product name",blank=False, max_length=100, null=False)
    discription=models.TextField()
    image=models.ForeignKey(RoomImages, related_name="room", on_delete=models.CASCADE, db_column="room_image_id")
    class Meta:
        db_table = 'room'

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

    class Meta:
        db_table = 'reservation'

class DailyReservationCard(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateField(auto_now_add=True)
    room = models.ForeignKey(Room, related_name="reservation", on_delete=models.CASCADE, db_column="room_id")
    



