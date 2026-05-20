from rest_framework import viewsets

from apps.users.permissions import IsAdmin
from apps.users.serializers import UserCreateSerializer, UserSerializer

from .models import User


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("-date_joined")
    permission_classes = [IsAdmin]

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        return UserSerializer
