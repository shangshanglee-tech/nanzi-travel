from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Activity, ActivityImage, CabinDisplayGroup, CabinType, Destination, Product, ProductImage, Vessel, VesselDeckPlan, VesselPageBlock, VesselPageBlockImage, VesselPageBlockType
from .operations_serializers import (
    OperationsDestinationSerializer,
    OperationsProductImageSerializer,
    OperationsProductSerializer,
    OperationsVesselSerializer,
    OperationsVesselPageBlockImageSerializer,
    OperationsVesselPageBlockSerializer,
    OperationsCabinDisplayGroupSerializer,
    OperationsCabinSerializer,
    OperationsVesselDeckPlanSerializer,
    OperationsActivityImageSerializer,
    OperationsActivitySerializer,
)


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
        products = Product.objects.select_related("destination").prefetch_related("vessels", "departures", "itinerary_days", "images")
        return Response({"results": OperationsProductSerializer(products, many=True, context={"request": request}).data})

    def post(self, request):
        serializer = OperationsProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(OperationsProductSerializer(serializer.save(), context={"request": request}).data, status=status.HTTP_201_CREATED)


class ProductDetailView(OperationsAdminView):
    def get_object(self, pk):
        try:
            return Product.objects.select_related("destination").prefetch_related("vessels", "departures", "itinerary_days", "images").get(pk=pk)
        except Product.DoesNotExist:
            return None

    def get(self, request, pk):
        product = self.get_object(pk)
        if product is None:
            return Response({"detail": "旅行产品不存在"}, status=status.HTTP_404_NOT_FOUND)
        return Response(OperationsProductSerializer(product, context={"request": request}).data)

    def patch(self, request, pk):
        product = self.get_object(pk)
        if product is None:
            return Response({"detail": "旅行产品不存在"}, status=status.HTTP_404_NOT_FOUND)
        serializer = OperationsProductSerializer(product, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        return Response(OperationsProductSerializer(serializer.save(), context={"request": request}).data)

    def delete(self, request, pk):
        product = self.get_object(pk)
        if product is None:
            return Response({"detail": "旅行产品不存在"}, status=status.HTTP_404_NOT_FOUND)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductHeroImageView(OperationsAdminView):
    def post(self, request, pk):
        try:
            product = Product.objects.prefetch_related("images").get(pk=pk)
        except Product.DoesNotExist:
            return Response({"detail": "旅行产品不存在"}, status=status.HTTP_404_NOT_FOUND)
        image = request.FILES.get("image")
        if image is None:
            return Response({"detail": "请选择封面图片"}, status=status.HTTP_400_BAD_REQUEST)
        product.hero_image = image
        product.save(update_fields=["hero_image", "updated_at"])
        return Response(OperationsProductSerializer(product, context={"request": request}).data)


class ProductImageListCreateView(OperationsAdminView):
    def post(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({"detail": "旅行产品不存在"}, status=status.HTTP_404_NOT_FOUND)
        image = request.FILES.get("image")
        if image is None:
            return Response({"detail": "请选择图库图片"}, status=status.HTTP_400_BAD_REQUEST)
        last_image = product.images.order_by("-sort_order", "-id").first()
        product_image = ProductImage.objects.create(
            product=product,
            image=image,
            alt_text=request.data.get("alt_text", ""),
            sort_order=(last_image.sort_order + 1) if last_image else 0,
        )
        return Response(
            OperationsProductImageSerializer(product_image, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class ProductImageDetailView(OperationsAdminView):
    def delete(self, request, pk, image_id):
        try:
            image = ProductImage.objects.get(pk=image_id, product_id=pk)
        except ProductImage.DoesNotExist:
            return Response({"detail": "图库图片不存在"}, status=status.HTTP_404_NOT_FOUND)
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class VesselListView(OperationsAdminView):
    def get(self, request):
        vessels = Vessel.objects.all()
        return Response({"results": OperationsVesselSerializer(vessels, many=True, context={"request": request}).data})

    def post(self, request):
        serializer = OperationsVesselSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            OperationsVesselSerializer(serializer.save(), context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class VesselDetailView(OperationsAdminView):
    def get_object(self, pk):
        try:
            return Vessel.objects.get(pk=pk)
        except Vessel.DoesNotExist:
            return None

    def get(self, request, pk):
        vessel = self.get_object(pk)
        if vessel is None:
            return Response({"detail": "船只不存在"}, status=status.HTTP_404_NOT_FOUND)
        return Response(OperationsVesselSerializer(vessel, context={"request": request}).data)

    def patch(self, request, pk):
        vessel = self.get_object(pk)
        if vessel is None:
            return Response({"detail": "船只不存在"}, status=status.HTTP_404_NOT_FOUND)
        serializer = OperationsVesselSerializer(vessel, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        return Response(OperationsVesselSerializer(serializer.save(), context={"request": request}).data)


class VesselCardImageView(OperationsAdminView):
    def post(self, request, pk):
        try:
            vessel = Vessel.objects.get(pk=pk)
        except Vessel.DoesNotExist:
            return Response({"detail": "船只不存在"}, status=status.HTTP_404_NOT_FOUND)
        image = request.FILES.get("image")
        if image is None:
            return Response({"detail": "请选择卡片图"}, status=status.HTTP_400_BAD_REQUEST)
        vessel.card_image = image
        vessel.save(update_fields=["card_image", "updated_at"])
        return Response(OperationsVesselSerializer(vessel, context={"request": request}).data)


class VesselPageBlockListCreateView(OperationsAdminView):
    def get_vessel(self, pk):
        try:
            return Vessel.objects.get(pk=pk)
        except Vessel.DoesNotExist:
            return None

    def get(self, request, pk):
        vessel = self.get_vessel(pk)
        if vessel is None:
            return Response({"detail": "船只不存在"}, status=status.HTTP_404_NOT_FOUND)
        blocks = vessel.page_blocks.prefetch_related("additional_images")
        return Response({"results": OperationsVesselPageBlockSerializer(blocks, many=True, context={"request": request}).data})

    def post(self, request, pk):
        vessel = self.get_vessel(pk)
        if vessel is None:
            return Response({"detail": "船只不存在"}, status=status.HTTP_404_NOT_FOUND)
        serializer = OperationsVesselPageBlockSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data["block_type"] == VesselPageBlockType.CARD and request.FILES.get("image") is None:
            return Response({"detail": "内容卡片必须上传图片"}, status=status.HTTP_400_BAD_REQUEST)
        last_block = vessel.page_blocks.order_by("-sort_order", "-id").first()
        block = serializer.save(
            vessel=vessel,
            image=request.FILES.get("image"),
            sort_order=(last_block.sort_order + 1) if last_block else 0,
        )
        return Response(OperationsVesselPageBlockSerializer(block, context={"request": request}).data, status=status.HTTP_201_CREATED)


class VesselPageBlockDetailView(OperationsAdminView):
    def get_block(self, vessel_id, block_id):
        try:
            return VesselPageBlock.objects.prefetch_related("additional_images").get(pk=block_id, vessel_id=vessel_id)
        except VesselPageBlock.DoesNotExist:
            return None

    def patch(self, request, pk, block_id):
        block = self.get_block(pk, block_id)
        if block is None:
            return Response({"detail": "页面内容不存在"}, status=status.HTTP_404_NOT_FOUND)
        serializer = OperationsVesselPageBlockSerializer(block, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        return Response(OperationsVesselPageBlockSerializer(serializer.save(), context={"request": request}).data)

    def delete(self, request, pk, block_id):
        block = self.get_block(pk, block_id)
        if block is None:
            return Response({"detail": "页面内容不存在"}, status=status.HTTP_404_NOT_FOUND)
        block.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class VesselPageBlockOrderView(OperationsAdminView):
    def patch(self, request, pk):
        ids = request.data.get("ids", [])
        blocks = list(VesselPageBlock.objects.filter(vessel_id=pk).order_by("id"))
        if len(ids) != len(blocks) or set(ids) != {block.id for block in blocks}:
            return Response({"detail": "排序内容与当前页面内容不一致"}, status=status.HTTP_400_BAD_REQUEST)
        block_map = {block.id: block for block in blocks}
        for order, block_id in enumerate(ids):
            block_map[block_id].sort_order = order
        VesselPageBlock.objects.bulk_update(blocks, ["sort_order"])
        ordered = [block_map[block_id] for block_id in ids]
        return Response({"results": OperationsVesselPageBlockSerializer(ordered, many=True, context={"request": request}).data})


class VesselPageBlockImageListCreateView(OperationsAdminView):
    def post(self, request, pk, block_id):
        try:
            block = VesselPageBlock.objects.get(pk=block_id, vessel_id=pk)
        except VesselPageBlock.DoesNotExist:
            return Response({"detail": "页面内容不存在"}, status=status.HTTP_404_NOT_FOUND)
        if block.block_type != VesselPageBlockType.CARD:
            return Response({"detail": "只有内容卡片可以添加额外图片"}, status=status.HTTP_400_BAD_REQUEST)
        image = request.FILES.get("image")
        if image is None:
            return Response({"detail": "请选择图片"}, status=status.HTTP_400_BAD_REQUEST)
        last_image = block.additional_images.order_by("-sort_order", "-id").first()
        block_image = VesselPageBlockImage.objects.create(
            vessel=block.vessel,
            page_block=block,
            image=image,
            sort_order=(last_image.sort_order + 1) if last_image else 0,
        )
        return Response(OperationsVesselPageBlockImageSerializer(block_image, context={"request": request}).data, status=status.HTTP_201_CREATED)


class VesselPageBlockImageDetailView(OperationsAdminView):
    def delete(self, request, pk, block_id, image_id):
        try:
            image = VesselPageBlockImage.objects.get(pk=image_id, vessel_id=pk, page_block_id=block_id)
        except VesselPageBlockImage.DoesNotExist:
            return Response({"detail": "额外图片不存在"}, status=status.HTTP_404_NOT_FOUND)
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class VesselCabinListCreateView(OperationsAdminView):
    def get_vessel(self, pk):
        try:
            return Vessel.objects.get(pk=pk)
        except Vessel.DoesNotExist:
            return None

    def get(self, request, pk):
        vessel = self.get_vessel(pk)
        if vessel is None:
            return Response({"detail": "船只不存在"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"results": OperationsCabinSerializer(vessel.cabins.all(), many=True, context={"request": request}).data})

    def post(self, request, pk):
        vessel = self.get_vessel(pk)
        if vessel is None:
            return Response({"detail": "船只不存在"}, status=status.HTTP_404_NOT_FOUND)
        serializer = OperationsCabinSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        last_cabin = vessel.cabins.order_by("-sort_order", "-id").first()
        cabin = serializer.save(vessel=vessel, sort_order=(last_cabin.sort_order + 1) if last_cabin else 0)
        return Response(OperationsCabinSerializer(cabin, context={"request": request}).data, status=status.HTTP_201_CREATED)


class VesselCabinDetailView(OperationsAdminView):
    def get_cabin(self, vessel_id, cabin_id):
        try:
            return CabinType.objects.get(pk=cabin_id, vessel_id=vessel_id)
        except CabinType.DoesNotExist:
            return None

    def patch(self, request, pk, cabin_id):
        cabin = self.get_cabin(pk, cabin_id)
        if cabin is None:
            return Response({"detail": "舱位不存在"}, status=status.HTTP_404_NOT_FOUND)
        serializer = OperationsCabinSerializer(cabin, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        return Response(OperationsCabinSerializer(serializer.save(), context={"request": request}).data)

    def delete(self, request, pk, cabin_id):
        cabin = self.get_cabin(pk, cabin_id)
        if cabin is None:
            return Response({"detail": "舱位不存在"}, status=status.HTTP_404_NOT_FOUND)
        cabin.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class VesselCabinImageView(OperationsAdminView):
    def post(self, request, pk, cabin_id):
        try:
            cabin = CabinType.objects.get(pk=cabin_id, vessel_id=pk)
        except CabinType.DoesNotExist:
            return Response({"detail": "舱位不存在"}, status=status.HTTP_404_NOT_FOUND)
        image = request.FILES.get("image")
        if image is None:
            return Response({"detail": "请选择舱型图片"}, status=status.HTTP_400_BAD_REQUEST)
        cabin.image = image
        cabin.save(update_fields=["image"])
        return Response(OperationsCabinSerializer(cabin, context={"request": request}).data)


class VesselCabinGroupListCreateView(OperationsAdminView):
    def get_vessel(self, pk):
        try:
            return Vessel.objects.get(pk=pk)
        except Vessel.DoesNotExist:
            return None

    def get(self, request, pk):
        vessel = self.get_vessel(pk)
        if vessel is None:
            return Response({"detail": "船只不存在"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"results": OperationsCabinDisplayGroupSerializer(vessel.cabin_groups.all(), many=True).data})

    def post(self, request, pk):
        vessel = self.get_vessel(pk)
        if vessel is None:
            return Response({"detail": "船只不存在"}, status=status.HTTP_404_NOT_FOUND)
        serializer = OperationsCabinDisplayGroupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cabins = serializer.validated_data.get("cabins", [])
        if any(cabin.vessel_id != vessel.id for cabin in cabins):
            return Response({"detail": "只能选择当前船只的舱位"}, status=status.HTTP_400_BAD_REQUEST)
        last_group = vessel.cabin_groups.order_by("-sort_order", "-id").first()
        group = serializer.save(vessel=vessel, sort_order=(last_group.sort_order + 1) if last_group else 0)
        return Response(OperationsCabinDisplayGroupSerializer(group).data, status=status.HTTP_201_CREATED)


class VesselDeckPlanListCreateView(OperationsAdminView):
    def get_vessel(self, pk):
        try:
            return Vessel.objects.get(pk=pk)
        except Vessel.DoesNotExist:
            return None

    def get(self, request, pk):
        vessel = self.get_vessel(pk)
        if vessel is None:
            return Response({"detail": "船只不存在"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"results": OperationsVesselDeckPlanSerializer(vessel.deck_plans.all(), many=True, context={"request": request}).data})

    def post(self, request, pk):
        vessel = self.get_vessel(pk)
        if vessel is None:
            return Response({"detail": "船只不存在"}, status=status.HTTP_404_NOT_FOUND)
        image = request.FILES.get("image")
        if image is None:
            return Response({"detail": "请选择甲板示意图"}, status=status.HTTP_400_BAD_REQUEST)
        last_plan = vessel.deck_plans.order_by("-sort_order", "-id").first()
        deck_plan = VesselDeckPlan.objects.create(vessel=vessel, title=request.data.get("title", ""), image=image, sort_order=(last_plan.sort_order + 1) if last_plan else 0)
        return Response(OperationsVesselDeckPlanSerializer(deck_plan, context={"request": request}).data, status=status.HTTP_201_CREATED)


class VesselDeckPlanDetailView(OperationsAdminView):
    def delete(self, request, pk, deck_id):
        try:
            deck_plan = VesselDeckPlan.objects.get(pk=deck_id, vessel_id=pk)
        except VesselDeckPlan.DoesNotExist:
            return Response({"detail": "甲板示意图不存在"}, status=status.HTTP_404_NOT_FOUND)
        deck_plan.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ActivityListCreateView(OperationsAdminView):
    def get(self, request):
        activities = Activity.objects.select_related("destination").prefetch_related("products", "images")
        return Response({"results": OperationsActivitySerializer(activities, many=True, context={"request": request}).data})

    def post(self, request):
        serializer = OperationsActivitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(OperationsActivitySerializer(serializer.save(), context={"request": request}).data, status=status.HTTP_201_CREATED)


class ActivityDetailView(OperationsAdminView):
    def get_object(self, pk):
        try:
            return Activity.objects.select_related("destination").prefetch_related("products", "images").get(pk=pk)
        except Activity.DoesNotExist:
            return None

    def get(self, request, pk):
        item = self.get_object(pk)
        if item is None:
            return Response({"detail": "活动不存在"}, status=status.HTTP_404_NOT_FOUND)
        return Response(OperationsActivitySerializer(item, context={"request": request}).data)

    def patch(self, request, pk):
        item = self.get_object(pk)
        if item is None:
            return Response({"detail": "活动不存在"}, status=status.HTTP_404_NOT_FOUND)
        serializer = OperationsActivitySerializer(item, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        return Response(OperationsActivitySerializer(serializer.save(), context={"request": request}).data)

    def delete(self, request, pk):
        item = self.get_object(pk)
        if item is None:
            return Response({"detail": "活动不存在"}, status=status.HTTP_404_NOT_FOUND)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ActivityHeroImageView(OperationsAdminView):
    def post(self, request, pk):
        try:
            item = Activity.objects.get(pk=pk)
        except Activity.DoesNotExist:
            return Response({"detail": "活动不存在"}, status=status.HTTP_404_NOT_FOUND)
        image = request.FILES.get("image")
        if image is None:
            return Response({"detail": "请选择活动主图"}, status=status.HTTP_400_BAD_REQUEST)
        item.hero_image = image
        item.save(update_fields=["hero_image", "updated_at"])
        return Response(OperationsActivitySerializer(item, context={"request": request}).data)


class ActivityImageListCreateView(OperationsAdminView):
    def post(self, request, pk):
        try:
            item = Activity.objects.get(pk=pk)
        except Activity.DoesNotExist:
            return Response({"detail": "活动不存在"}, status=status.HTTP_404_NOT_FOUND)
        image = request.FILES.get("image")
        if image is None:
            return Response({"detail": "请选择活动图片"}, status=status.HTTP_400_BAD_REQUEST)
        last_image = item.images.order_by("-sort_order", "-id").first()
        activity_image = ActivityImage.objects.create(activity=item, image=image, alt_text=request.data.get("alt_text", ""), sort_order=(last_image.sort_order + 1) if last_image else 0)
        return Response(OperationsActivityImageSerializer(activity_image, context={"request": request}).data, status=status.HTTP_201_CREATED)


class ActivityImageDetailView(OperationsAdminView):
    def delete(self, request, pk, image_id):
        try:
            image = ActivityImage.objects.get(pk=image_id, activity_id=pk)
        except ActivityImage.DoesNotExist:
            return Response({"detail": "活动图片不存在"}, status=status.HTTP_404_NOT_FOUND)
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class VesselOptionsView(OperationsAdminView):
    def get(self, request):
        return Response({"results": [{"id": vessel.id, "name": vessel.name} for vessel in Vessel.objects.all()]})
