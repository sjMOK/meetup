from django.db import models
from users.models import User
from django.utils.translation import gettext_lazy as _


class RoomImages(models.Model):
    id = models.BigAutoField(primary_key=True, auto_created=True)
    image = models.ImageField(upload_to="images/", db_column="image")


class Room(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(blank=False, max_length=100, null=False)
    discription = models.TextField()
    images = models.ForeignKey(RoomImages, on_delete=models.CASCADE, null=True)


class Reservation(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey("users.User", models.DO_NOTHING)
    room = models.ForeignKey("Room", models.DO_NOTHING)
    start = models.DateTimeField()
    end = models.DateTimeField()

    class Meta:
        db_table = "reservation"


class DailyReservationCard(models.Model):
    id = models.AutoField(primary_key=True)
    reservation = models.ForeignKey("Reservation", models.DO_NOTHING)
    user = models.ForeignKey("users.User", models.DO_NOTHING)

    class Meta:
        db_table = "reservation_attendees"
