from django.urls import path
from .views import (
    MyReservationView,
    ReservationView,
    RoomView,
    authenticate_location,
)

urlpatterns = [
    path("", RoomView.as_view({"get": "list", "post": "create"})),
    path(
        "/<int:id>",
        RoomView.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "delete": "destroy",
            }
        ),
    ),
    path(
        "/reservations",
        ReservationView.as_view({"get": "list", "post": "create"}),
    ),
    # path(
    #     "/reservations/<int:pk>",
    #     ReservationView.as_view(
    #         {
    #             "get": "retrieve",
    #             "put": "update",
    #             "patch": "partial_update",
    #             "delete": "destroy",
    #         }
    #     ),
    # ),
    path(
        "/my-reservations",
        MyReservationView.as_view({"get": "list"}),
    ),
    path(
        "/my-reservations/<int:pk>",
        MyReservationView.as_view(
            {
                "get": "retrieve",
                "delete": "destroy",
            }
        ),
    ),
    path("/reservations/<int:id>/location", authenticate_location),
]
