from email.policy import default
from enum import unique
from logging import error
from optparse import Values
from pickle import FALSE
from rest_framework import serializers
from FilkaRecepty.models import Foods, FoodTags, Steps, Ingredients,Ingredient, Unit,ImageFood#Volume

# class FoodTagSerializer (serializers.Serializer):
#     # foodTag = serializers.CharField(max_length=60)
#     class Meta:
#         model = FoodTags
#         fields = '__all__'

# class OrderSerializer (serializers.Serializer):
#     id_foodTag = FoodTagSerializer(many=True, read_only=True)
#     class Meta:
#         model = Order
#         fields = ('id_foodTag',)



# class FoodSerializer(serializers.ModelSerializer):
#     id_food = serializers.IntegerField()
#     id_foodTag = OrderSerializer(many=True, read_only=True)
#     name = serializers.CharField()
#     class Meta:
#         model = Foods
#         fields = ('id_food','name','id_foodTag')



class FoodTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodTags
        fields = '__all__'  # in your case since you are using all fields.

class StepSerializer(serializers.ModelSerializer):
    class Meta:
        model = Steps
        fields = '__all__'  # in your case since you are using all fields.

class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = '__all__' # in your case since you are using all fields.     

class ImageFoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageFood
        fields = '__all__'  # in your case since you are using all fields.     

    
class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'  # in your case since you are using all fields.          

# class IngredientsSerializer (serializers.Serializer):
    # id = serializers.IntegerField(read_only = True)
    # headline= serializers.CharField(max_length=60)
    # units = serializers.PrimaryKeyRelatedField(many=True, read_only=False, queryset=Unit.objects.all())
    # volumes = serializers.PrimaryKeyRelatedField(many=True, read_only=False, queryset=Volume.objects.all())
    # ingredientName = serializers.PrimaryKeyRelatedField(many=True, read_only=False, queryset=Ingredient.objects.all())
class IngredientsSerializer(serializers.ModelSerializer):
    # units = UnitSerializer(many=True)
    # volumes = VolumeSerializer(many=True)
    # ingredientName = IngredientSerializer(many=True)
    class Meta:
        model = Ingredients
        fields = ('id','units','volume','ingredientName' )# in your case since you are using all fields.    
        # depth = 1 
        # if not Ingredients.objects.filter(fields).exists():
        #     # Insert new data here
        #     Ingredients.objects.create(fields)   
        # def entry(self, v1,v2,v3):
        #     if not Ingredients.objects.filter(units=v1).exists():
        #         Ingredients.objects.create(units=v1, volumes=v2,ingredientName=v3)
        # for instance in Ingredients.objects.all():
        #             if instance.units == units:
                        



from rest_framework import serializers    

class Base64ImageField(serializers.ImageField):
    """
    A Django REST framework field for handling image-uploads through raw post data.
    It uses base64 for encoding and decoding the contents of the file.

    Heavily based on
    https://github.com/tomchristie/django-rest-framework/pull/1268

    Updated for Django REST framework 3.
    """

    def to_internal_value(self, data):
        from django.core.files.base import ContentFile
        import base64
        import six
        import uuid

        # Check if this is a base64 string
        if isinstance(data, six.string_types):
            # Check if the base64 string is in the "data:" format
            if 'data:' in data and ';base64,' in data:
                # Break out the header from the base64 content
                header, data = data.split(';base64,')

            # Try to decode the file. Return validation error if it fails.
            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')

            # Generate file name:
            file_name = str(uuid.uuid4())[:12] # 12 characters are more than enough.
            # Get the file name extension:
            file_extension = self.get_file_extension(file_name, decoded_file)

            complete_file_name = "%s.%s" % (file_name, file_extension, )

            data = ContentFile(decoded_file, name=complete_file_name)

        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        import imghdr

        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension

        return extension

from drf_extra_fields.fields import Base64ImageField
class FoodSerializer(serializers.ModelSerializer):
    # id = serializers.IntegerField(read_only = True)
    # name = serializers.CharField()
    # ingredients = IngredientsSerializer(many=True)
    # foodTags = FoodTagSerializer(many=True)
    # steps = StepSerializer(many=False)
    # date = serializers.DateField() 
    # image = Base64ImageField(
    #     max_length=None, use_url=True,
    # )
    class Meta:
        model = Foods
        # fields = ("id", "name","image","ingredients","steps","date","foodTags",)
        fields = '__all__'  # in your case since you are using all fields.    
        # depth = 1              








# class FoodTagSerializer (serializers.Serializer):
#     id = serializers.IntegerField(read_only = True)
#     foodTag = serializers.CharField(max_length=60)
   

#     def create(self, validated_data):
#         newfoodTag = FoodTags.objects.create(
#             foodTag = validated_data["foodTag"],
#         )
#         return newfoodTag

#     def update(self, instance, validated_data):
#         instance.foodTag = validated_data.get('foodTag', instance.foodTag)
#         instance.save()
#         return instance        


# class StepSerializer (serializers.Serializer):
#     id = serializers.IntegerField(read_only = True)
#     step = serializers.CharField(max_length=500)
#     # album = serializers.PrimaryKeyRelatedField(many=True, read_only=False, queryset=ImageAlbum.objects.all())
   

#     def create(self, validated_data):
#         newStep = Steps.objects.create(
#             step = validated_data["step"],
#             # album = validated_data["album"],
#         )
#         return newStep

#     def update(self, instance, validated_data):
#         instance.step = validated_data.get('step', instance.step)
#         # instance.album = validated_data.get('album', instance.album)
#         instance.save()
#         return instance    


# class UnitSerializer (serializers.Serializer):
#     id = serializers.IntegerField(read_only = True)
#     unit = serializers.CharField(max_length=60)
   

#     def create(self, validated_data):
#         newUnit = Unit.objects.create(
#             unit = validated_data["unit"],
#         )
#         return newUnit

#     def update(self, instance, validated_data):
#         instance.unit = validated_data.get('unit', instance.unit)
#         instance.save()
#         return instance       

# class VolumeSerializer (serializers.Serializer):
#     id = serializers.IntegerField(read_only = True)
#     volume = serializers.CharField(max_length=60)
   

#     def create(self, validated_data):
#         newVolume = Volume.objects.create(
#             volume = validated_data["volume"],
#         )
#         return newVolume

#     def update(self, instance, validated_data):
#         instance.volume = validated_data.get('volume', instance.volume)
#         instance.save()
#         return instance     

# class IngredientSerializer (serializers.Serializer):
#     id = serializers.IntegerField(read_only = True)
#     ingredient = serializers.CharField(max_length=60)
   

#     def create(self, validated_data):
#         newIngredient = Ingredient.objects.create(
#             ingredient = validated_data["ingredient"],
#         )
#         return newIngredient

#     def update(self, instance, validated_data):
#         instance.ingredient = validated_data.get('ingredient', instance.ingredient)
#         instance.save()
#         return instance                       

# class IngredientsSerializer (serializers.Serializer):
#     id = serializers.IntegerField(read_only = True)
#     # ids= serializers.CharField(max_length=60, default="")
#     units = serializers.PrimaryKeyRelatedField(many=True, read_only=False, queryset=Unit.objects.all())
#     volumes = serializers.PrimaryKeyRelatedField(many=True, read_only=False, queryset=Volume.objects.all())
#     ingredientName = serializers.PrimaryKeyRelatedField(many=True, read_only=False, queryset=Ingredient.objects.all())
   

#     def create(self, validated_data):
#         newIngredient = Ingredients.objects.create(
#             # ids = validated_data["ids"],
#         )
#         newIngredient.units.set(validated_data["units"])
#         newIngredient.volumes.set(validated_data["volumes"])
#         newIngredient.ingredientName.set(validated_data["ingredientName"])
#         return newIngredient

#     def update(self, instance, validated_data):
#         # instance.ids = validated_data.get('ids', instance.ids)
#         instance.units.set(validated_data["units"])
#         instance.volumes.set(validated_data["volumes"])
#         instance.ingredientName.set(validated_data["ingredientName"])
#         instance.save()
#         return instance             


# class FoodSerializer (serializers.Serializer):
#     id = serializers.IntegerField(read_only = True)
#     name = serializers.CharField(max_length=60)
#     image = serializers.ImageField()
#     ingredients = serializers.PrimaryKeyRelatedField(many=True, read_only=False, queryset=Ingredients.objects.all())
#     foodTags = serializers.PrimaryKeyRelatedField(many=True, read_only=False, queryset=FoodTags.objects.all())
#     steps = serializers.PrimaryKeyRelatedField(many=False, read_only=False, queryset=Steps.objects.all())
#     date = serializers.DateField()


#     def create(self, validated_data):
#         newfood = Foods.objects.create(
#             name = validated_data["name"],
#             image = validated_data["image"],
#             date = validated_data["date"],

#         )
#         newfood.foodTags.set(validated_data["foodTags"])
#         newfood.steps.set(validated_data["steps"])
#         newfood.ingredients.set(validated_data["ingredients"])

#         return newfood

#     def update(self, instance, validated_data):
#         instance.name = validated_data.get('name', instance.name)
#         instance.image = validated_data.get('image', instance.image)
#         instance.date = validated_data.get('date', instance.date)
#         instance.foodTags.set(validated_data["foodTags"])
#         instance.steps.set(validated_data["steps"])
#         instance.ingredients.set(validated_data["ingredients"])
#         instance.save()
#         return instance            

