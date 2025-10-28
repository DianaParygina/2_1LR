from rest_framework import serializers

from dogs.models import Breed, Dog, Owner, Hobby, Country

class BreedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Breed
        fields = "__all__"

class BreedCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Breed
        fields = ['id', 'name'] 

class OwnerSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        if 'request' in self.context:
            validated_data['user'] = self.context['request'].user
            
            return super().create(validated_data)
    
    # def create(self, validated_data):
    #     # Получаем текущего пользователя из контекста запроса
    #     user = self.context['request'].user 
    #     # Создаем объект Owner с привязкой к пользователю
    #     owner = Owner.objects.create(user=user, **validated_data)
    #     return owner
    
    class Meta:
        model = Owner
        fields = ['id', 'first_name', 'last_name', 'phone_number', 'pictureOwner', 'user']
        read_only_fields = ['user'] 

class HobbySerializer(serializers.ModelSerializer):
    class Meta:
        model = Hobby
        fields = ['id', 'name_hobby']      

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'country'] 

class DogListSerializer(serializers.ModelSerializer):
    breed = BreedSerializer(read_only=True)
    owner = OwnerSerializer(read_only=True)
    hobby = HobbySerializer(read_only=True)
    country = CountrySerializer(read_only=True)

    class Meta:
        model = Dog
        fields = ['id', 'name', 'breed','owner', 'hobby', 'country', 'picture', 'user']  
        read_only_fields = ['user']


class DogCreateSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        user = self.context['request'].user
        dog = Dog.objects.create(user=user, **validated_data)
        return dog

    class Meta:
        model = Dog
        fields = ['id', 'name', 'breed','owner', 'hobby', 'country', 'picture', 'user']
        read_only_fields = ['user']

class DogUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dog
        fields = ['id', 'name', 'breed','owner', 'hobby', 'country', 'picture', 'user']        
        read_only_fields = ['user']   


class LoginSerializer(serializers.Serializer):
        username = serializers.CharField(required=True)
        password = serializers.CharField(required=True, style={'input_type': 'password'}) 