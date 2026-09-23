from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from order.models import Order
from order.serializers import OrderSerializer


class OrderViewSet(ModelViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.all().order_by("-id")
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]