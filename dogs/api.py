from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins, viewsets, permissions, serializers
from django.db.models import Avg, Count, Max, Min
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import authenticate, login, logout
from django.core.cache import cache  
from rest_framework.permissions import BasePermission
import pyotp
from openpyxl import Workbook
from openpyxl.writer.excel import save_workbook
from django.http import FileResponse, HttpResponse
import io

from dogs.models import Breed, Dog, Owner, Country, Hobby
from dogs.serializers import DogCreateSerializer, DogListSerializer, BreedSerializer, OwnerSerializer, CountrySerializer, HobbySerializer, DogUpdateSerializer






class UserProfileViewSet(
    GenericViewSet
):
    permission_classes = [AllowAny]

    class OTPSerializer(serializers.Serializer):
        key = serializers.CharField()

    class OTPRequired(BasePermission):
        def has_permission(self, request, view):
            return bool(request.user and cache.get('otp_good', False))
        
    @action(detail=False, url_path="check-login", methods=['GET'], permission_classes=[])
    def get_check_login(self, request, *args, **kwargs):
        return Response({
            'is_authenticated': self.request.user.is_authenticated
        })
    
    # @action(detail=False, url_path="login", methods=['GET'], permission_classes=[])
    # def use_login(self, request, *args, **kwargs):
    #     user= authenticate(username='username', password='pass')
    #     if user:
    #         login(request, user)
    #     return Response({
    #         'is_authenticated': bool(user)
    #     })

    @action(detail=False, url_path='otp-login', methods=['POST'], serializer_class=OTPSerializer)
    def otp_login(self, *args, **kwargs):
        totp = pyotp.TOTP(self.request.user.userprofile.opt_key)
        
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        success = False
        if totp.now() == serializer.validated_data['key']:
            cache.set('otp_good:{self.request.user.id}', True, 60*2)
            success = True

        return Response({
            'success': success
        })

    
    @action(detail=False, url_path='otp-status')
    def get_otp_status(self, *args, **kwargs):
        otp_good = cache.get('otp_good:{self.request.user.id}', False)
        return Response({
            'otp_good': otp_good
        })
    
    @action(detail=False, url_path='otp-required', permission_classes=[OTPRequired])
    def page_with_otp_required(self, *args, **kwargs):
        return Response({
            'success': True
        })







class UserViewset(GenericViewSet):
        @action(detail=False, methods=['GET'], url_path='info')
        def get_info(self, request, *args, **kwargs):
            data = {
                "is_authenticated": request.user.is_authenticated
            }
            if request.user.is_authenticated:
                data.update({
                    "username": request.user.username,
                    "user_id":request.user.id
                })
            return Response(data)
        
        @action(detail=False, methods=['POST'], url_path='login')
        def login(self, request, *args, **kwargs):
            username = request.data.get("user") 
            password = request.data.get("pass") 
            user = authenticate(request, username = username, password = password)
            if user:
                login(request, user)
                return Response({"status": "success"})  # Возвращаем успешный ответ
            else:
                return Response({"status": "error", "message": "Неверные учетные данные"}, status=401) 
        
        @action(detail=False, methods=['POST'], url_path='logout')
        def logout(self, request, *args, **kwargs):
            logout(request)
            return Response({})



class IsOwnerOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_superuser or obj.user == request.user and cache.get(f'otp_good:{request.user.id}', False)
    

class DogsViewset(
    mixins.CreateModelMixin, 
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet):
    queryset = Dog.objects.all().order_by("id")
    serializer_class = DogListSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name', 'breed__name', 'owner__first_name', 'owner__last_name', 'country__country', 'hobby__name_hobby']

    def get_serializer_class(self):
        if self.action == 'create':
            return DogCreateSerializer
        if self.action == 'update':
            return DogUpdateSerializer
        return super(DogsViewset, self).get_serializer_class()        

    def get_queryset(self):
        qs = super().get_queryset()  # Используем super() для получения queryset
        # print(self.request.user)
        # # Если пользователь не суперпользователь, фильтруем по текущему пользователю
        # if not self.request.user.is_superuser:
        #     qs = qs.filter(user=self.request.user)
        # else:
        #     # Если суперпользователь, добавляем возможность фильтрации по пользователю
        #     user_id = self.request.query_params.get('user_id', None)  # Получаем user_id из параметров запроса
        #     if user_id:
        #         qs = qs.filter(owner__user_id=user_id)

        return qs
        
    class StatsSerializer(serializers.Serializer):
        count = serializers.IntegerField()
        avg = serializers.FloatField()
        max = serializers.IntegerField()
        min = serializers.IntegerField()

    @action(detail=False, methods=['GET'], url_path='stats')
    def get_stats(self, request, *args, **kwargs):
        try:
            qs = Dog.objects.all()

            user_id = request.query_params.get('user_id')
            if user_id:
                qs = qs.filter(user_id=user_id)
                print("user_id")
                print(user_id)

            stats = qs.aggregate(
                count=Count('*'),
                avg=Avg('id'),
                max=Max('id'),
                min=Min('id'),
            )

            serializer = self.StatsSerializer(instance=stats)
            return Response(serializer.data)
    
        except Exception as e:
            print(f"Ошибка при экспорте: {e}")
            return Response({"error": str(e)}, status=500)
    


    @action(detail=False, methods=['GET'], url_path='export')
    def export_data(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())

        wb = Workbook()
        ws = wb.active
        ws.append(['ID', 'Имя', 'Порода', 'Владелец', 'Страна', 'Хобби'])  

        for dog in qs:
            owner_name = f"{dog.owner.first_name} {dog.owner.last_name}" if dog.owner else ""
            ws.append([dog.id, dog.name, dog.breed.name if dog.breed else "", owner_name, dog.country.country if dog.country else "", dog.hobby.name_hobby if dog.hobby else ""])

        virtual_workbook = io.BytesIO()
        wb.save(virtual_workbook)
        virtual_workbook.seek(0)

        response = HttpResponse(content=virtual_workbook, content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename=dogs.xlsx'
        return response

 

class BreedsViewset(
    mixins.CreateModelMixin, 
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet):
    queryset = Breed.objects.all()
    serializer_class = BreedSerializer
    permission_classes = [AllowAny]

    class StatsSerializer(serializers.Serializer):
        count = serializers.IntegerField()
        avg = serializers.FloatField()
        max = serializers.IntegerField()
        min = serializers.IntegerField()

    @action(detail=False, methods=['GET'], url_path='stats')
    def get_stats(self, request, *args, **kwargs):
        qs = Breed.objects.all()

        user_id = request.query_params.get('user_id')
        if user_id:
            qs = qs.filter(user_id=user_id)
            print("user_id")
            print(user_id)

        stats = qs.aggregate(
            count=Count('*'),
            avg=Avg('id'),
            max=Max('id'),
            min=Min('id'),
        )

        serializer = self.StatsSerializer(instance=stats)
        return Response(serializer.data)




class OwnersViewset(
    mixins.CreateModelMixin, 
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet):
    queryset = Owner.objects.all()
    serializer_class = OwnerSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'first_name', 'last_name', 'phone_number']

    def get_queryset(self):
        qs = super().get_queryset()  # Используем super() для получения queryset

        # # Если пользователь не суперпользователь, фильтруем по текущему пользователю
        # if not self.request.user.is_superuser:
        #     qs = qs.filter(user=self.request.user)
        # else:
        #     # Если суперпользователь, добавляем возможность фильтрации по пользователю
        #     user_id = self.request.query_params.get('user_id', None)  # Получаем user_id из параметров запроса
        #     if user_id is not None:
        #         qs = qs.filter(user_id=user_id)

        return qs
        
    class StatsSerializer(serializers.Serializer):
        count = serializers.IntegerField()
        avg = serializers.FloatField()
        max = serializers.IntegerField()
        min = serializers.IntegerField()

    @action(detail=False, methods=['GET'], url_path='stats')
    def get_stats(self, request, *args, **kwargs):
        stats = Owner.objects.aggregate(
            count=Count('*'),
            avg=Avg('id'),
            max=Max('id'),
            min=Min('id'),
        )

        serializer = self.StatsSerializer(instance=stats)

        return Response(serializer.data) 

class CountryViewset(
    mixins.CreateModelMixin, 
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [AllowAny]

    class StatsSerializer(serializers.Serializer):
        count = serializers.IntegerField()
        avg = serializers.FloatField()
        max = serializers.IntegerField()
        min = serializers.IntegerField()

    @action(detail=False, methods=['GET'], url_path='stats')
    def get_stats(self, request, *args, **kwargs):
        qs = Country.objects.all()

        user_id = request.query_params.get('user_id')
        if user_id:
            qs = qs.filter(user_id=user_id)
            print("user_id")
            print(user_id)

        stats = qs.aggregate(
            count=Count('*'),
            avg=Avg('id'),
            max=Max('id'),
            min=Min('id'),
        )

        serializer = self.StatsSerializer(instance=stats)
        return Response(serializer.data)

class HobbyViewset(
    mixins.CreateModelMixin, 
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet):
    queryset = Hobby.objects.all()
    serializer_class = HobbySerializer
    permission_classes = [AllowAny]

    class StatsSerializer(serializers.Serializer):
        count = serializers.IntegerField()
        avg = serializers.FloatField()
        max = serializers.IntegerField()
        min = serializers.IntegerField()

    @action(detail=False, methods=['GET'], url_path='stats')
    def get_stats(self, request, *args, **kwargs):
        qs = Hobby.objects.all()

        user_id = request.query_params.get('user_id')
        if user_id:
            qs = qs.filter(user_id=user_id)
            print("user_id")
            print(user_id)

        stats = qs.aggregate(
            count=Count('*'),
            avg=Avg('id'),
            max=Max('id'),
            min=Min('id'),
        )

        serializer = self.StatsSerializer(instance=stats)
        return Response(serializer.data)