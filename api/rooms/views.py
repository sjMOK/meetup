import json
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_202_ACCEPTED,
    HTTP_400_BAD_REQUEST,
)
from rest_framework.decorators import api_view
from django.core.exceptions import BadRequest
from .models import Reservation, Room, RoomImages
from .serializers import (
    MyReservationSerializer,
    ReservationSerializer,
    RoomSerializer,
)
from rest_framework.permissions import IsAuthenticated, AllowAny

from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
import logging
from haversine import haversine
from drf_yasg.utils import swagger_auto_schema

from users.permissions import (
    IsAdminOrReadOnly,
    IsOwnerOrAdmin,
    UserAccessPermission,
    IsNonAdminUser,
)


AI_CENTER_POINT = (37.551100, 127.075750)
ALLOWED_DISTANCE = 25


logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")


def check_schedule_conflict(start, end):
    conflicting_schedules = Reservation.objects.filter(
        start__lt=end,  # 등록하려는 일정의 종료일 이후에 시작하는 일정
        end__gt=start,  # 등록하려는 일정의 시작일 이전에 종료하는 일정
    )
    logger.warning(conflicting_schedules.id)
    if conflicting_schedules:
        raise BadRequest  # 겹치는 일정이 존재하는 경우

    return  # 겹치는 일정이 없는 경우


@api_view(["POST"])
def authenticate_location(request, id):
    latitude, logtitude = request.query_params.get(
        "latitude", None
    ), request.query_params.get("logtitude", None)
    if latitude is None or logtitude is None:
        return Response("pass latitude and logtitude", HTTP_400_BAD_REQUEST)

    try:
        latitude, logtitude = float(latitude), float(logtitude)
    except ValueError:
        return Response(
            "latitude and logtitude must be a float format.", HTTP_400_BAD_REQUEST
        )

    current_point = (latitude, logtitude)
    distance = haversine(AI_CENTER_POINT, current_point, unit="m")

    if distance < ALLOWED_DISTANCE:
        reservation = Reservation.objects.filter(id=id)
        reservation.update(is_attended=True)
        return Response({"message": "complete"}, status=HTTP_202_ACCEPTED)
    else:
        return Response({"message": "fail"}, status=HTTP_400_BAD_REQUEST)

    return Response(distance < ALLOWED_DISTANCE)


class RoomView(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    lookup_field = "id"

    def create(self, request):
        serializer = RoomSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            try:
                serializer.save()
                return Response({"message": "complete"})
            except Exception as e:
                return Response({"message": e})
        return Response({"message": "invalid form"})

    def update(self, request, id):
        room = Room.objects.filter(id=id)
        serializer = RoomSerializer(room, data=request.data)
        if serializer.is_valid(raise_exception=True):
            try:
                serializer.save()
                return Response({"message": "complete"})
            except Exception as e:
                return Response({"message": e})
        return Response({"message": "invalid form"})


class ReservationView(viewsets.ModelViewSet):
    # permission_classes = [IsAuthenticated]
    serializer_class = ReservationSerializer
    queryset = Reservation.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["date", "room"]

    def create(self, request):
        # if not check_schedule_conflict(
        #     request.data.get("start"), request.data.get("end")
        # ):
        #     raise BadRequest
        serializer = ReservationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            try:
                serializer.save()
                return Response({"message": "complete"})
            except Exception as e:
                return Response({"message": e})
        return Response({"message": "invalid form"})


class MyReservationView(viewsets.ModelViewSet):
    # permission_classes = [IsOwnerOrAdmin]
    serializer_class = MyReservationSerializer
    queryset = Reservation.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["date", "booker", "is_scheduled"]
    search_fields = ["day"]
