from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Destination, Product, Vessel
from .operations_serializers import OperationsDestinationSerializer, OperationsProductSerializer


class CsrfTokenView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"csrfToken": get_token(request)})


@method_decorator(csrf_protect, name="dispatch")
class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username", "")
        password = request.data.get("password", "")
        user = authenticate(request, username=username, password=password)
        if not user or not user.is_superuser:
            return Response({"detail": "账号或密码错误"}, status=status.HTTP_400_BAD_REQUEST)

        login(request, user)
        return Response({"username": user.get_username()})


@method_decorator(csrf_protect, name="dispatch")
class LogoutView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAdminUser]

    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CurrentUserView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAdminUser]

    def get(self, request):
        return Response({"username": request.user.get_username()})


class OperationsAdminView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAdminUser]


class DestinationListCreateView(OperationsAdminView):
    def get(self, request):
        destinations = Destination.objects.all()
        return Response({"results": OperationsDestinationSerializer(destinations, many=True).data})

    def post(self, request):
        serializer = OperationsDestinationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        destination = serializer.save()
        return Response(
            OperationsDestinationSerializer(destination).data,
            status=status.HTTP_201_CREATED,
        )


class DestinationDetailView(OperationsAdminView):
    def get_object(self, pk):
        try:
            return Destination.objects.get(pk=pk)
        except Destination.DoesNotExist:
            return None

    def patch(self, request, pk):
        destination = self.get_object(pk)
        if destination is None:
            return Response({"detail": "目的地不存在"}, status=status.HTTP_404_NOT_FOUND)
        serializer = OperationsDestinationSerializer(destination, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        return Response(OperationsDestinationSerializer(serializer.save()).data)

    def delete(self, request, pk):
        destination = self.get_object(pk)
        if destination is None:
            return Response({"detail": "目的地不存在"}, status=status.HTTP_404_NOT_FOUND)
        destination.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductListCreateView(OperationsAdminView):
    def get(self, request):
        products = Product.objects.select_related("destination").prefetch_related("vessels", "departures", "itinerary_days")
        return Response({"results": OperationsProductSerializer(products, many=True).data})

    def post(self, request):
        serializer = OperationsProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(OperationsProductSerializer(serializer.save()).data, status=status.HTTP_201_CREATED)


class ProductDetailView(OperationsAdminView):
    def get_object(self, pk):
        try:
            return Product.objects.select_related("destination").prefetch_related("vessels", "departures", "itinerary_days").get(pk=pk)
        except Product.DoesNotExist:
            return None

    def get(self, request, pk):
        product = self.get_object(pk)
        if product is None:
            return Response({"detail": "旅行产品不存在"}, status=status.HTTP_404_NOT_FOUND)
        return Response(OperationsProductSerializer(product).data)

    def patch(self, request, pk):
        product = self.get_object(pk)
        if product is None:
            return Response({"detail": "旅行产品不存在"}, status=status.HTTP_404_NOT_FOUND)
        serializer = OperationsProductSerializer(product, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        return Response(OperationsProductSerializer(serializer.save()).data)

    def delete(self, request, pk):
        product = self.get_object(pk)
        if product is None:
            return Response({"detail": "旅行产品不存在"}, status=status.HTTP_404_NOT_FOUND)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class VesselOptionsView(OperationsAdminView):
    def get(self, request):
        return Response({"results": [{"id": vessel.id, "name": vessel.name} for vessel in Vessel.objects.all()]})
