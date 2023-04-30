
from rest_framework import serializers
from .models import Room, Reservation, RoomImages, DailyReservationCard
from django.contrib.auth.models import User


class RoomImageSerializer(serializers.ModelSerializer):
    class Meta:
        model=RoomImages
        fields="__all__"
        
class RoomSerializer(serializers.ModelSerializer):
    id=serializers.IntegerField(read_only=True)
    image=RoomImageSerializer()
    class Meta:
        model=Room
        fields=("id","image","name","discription")

    
# class CommentSerializer(serializers.ModelSerializer):
#     auth=AuthSerializer(read_only=True)
#     class Meta:
#         model = Comment
#         fields = ("id", "post_id", "auth", "contents", "created", "updated")