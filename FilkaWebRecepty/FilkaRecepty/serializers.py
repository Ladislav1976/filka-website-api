from email.policy import default
from enum import unique
from logging import error
from optparse import Values
from pickle import FALSE
from rest_framework import serializers
from FilkaRecepty.models import Foods, FoodTags, Steps, Ingredients,Ingredient, Unit,ImageFood, Url,CustomUser 


class FoodTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodTags
        fields = '__all__' 

class StepSerializer(serializers.ModelSerializer):
    class Meta:
        model = Steps
        fields = '__all__'  

class UrlSerializer(serializers.ModelSerializer):
    class Meta:
        model = Url
        fields = '__all__'  

class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = '__all__'     

class ImageFoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageFood
        fields = '__all__'       

    
class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'          


class IngredientsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredients
        fields = ('id','units','quantity','ingredientName','position' ) 



class FoodSerializer(serializers.ModelSerializer):

    class Meta:
        model = Foods
        fields = '__all__' 
             
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        # model = get_user_model()
        model = CustomUser
        fields = ('id','email', 'first_name', 'last_name' ,'role', 'is_superuser')#,'password')

class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields= ('id','email','first_name', 'last_name','role')

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        style={"input_type": "password"}, write_only=True)


# class RecipeEmailSubmitSerializer(serializers.Serializer):
#     class Meta:
#         model = CustomUser
#         fields = ('id','email','recipe') 



        