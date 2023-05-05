
from rest_framework import serializers
from .models import Room, RoomImages
from django.contrib.auth.models import User


class RoomImageSerializer(serializers.ModelSerializer):
    id=serializers.IntegerField(read_only=True)
    image = serializers.ImageField(use_url=True, required=False)
    class Meta:
        model=RoomImages
        fields=("__all__")
        
class RoomSerializer(serializers.ModelSerializer):
    id=serializers.IntegerField(read_only=True)
    name=serializers.CharField()
    discription=serializers.CharField()
    images=RoomImageSerializer(required=False)

    def create(self, validated_data):
        # print(validated_data)
        images = validated_data.pop('images')
        room = Room.objects.create(**validated_data)
        # for image in images:
        #     RoomImages.objects.create(image=image)
        return room
    class Meta:
        model=Room
        fields=("__all__")




    
# class CommentSerializer(serializers.ModelSerializer):
#     auth=AuthSerializer(read_only=True)
#     class Meta:
#         model = Comment
#         fields = ("id", "post_id", "auth", "contents", "created", "updated")