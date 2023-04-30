from rest_framework import  viewsets
from rest_framework.response import Response
from .models import  Room, RoomImages
from .serializers import RoomSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
 
class RoomView(viewsets.ModelViewSet):
    # permission_classes = [IsAuthenticated]
    queryset=Room.objects.all()
    serializer_class = RoomSerializer

    def list(self, request):
        queryset=Room.objects.all()
        serializer=RoomSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer=RoomSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save(user=request.user.id)
                return Response({"message":"complete"})
            except:
                return Response({"message":"fail"})
        return Response({"message":"invalid form"})
 

class RoomRetrieveView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset=Room.objects.all()
    serializer_class = RoomSerializer
