from rest_framework import serializers

from FilkaRecepty.models import (
    CustomUser,
    Foods,
    FoodTags,
    ImageFood,
    Ingredient,
    Ingredients,
    Steps,
    Unit,
    Url,
)


class FoodTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodTags
        fields = "__all__"


class StepSerializer(serializers.ModelSerializer):
    class Meta:
        model = Steps
        fields = "__all__"


class UrlSerializer(serializers.ModelSerializer):
    class Meta:
        model = Url
        fields = "__all__"


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = "__all__"


class ImageFoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageFood
        fields = "__all__"


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = "__all__"


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredients
        fields = "__all__"


class FoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Foods
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        # model = get_user_model()
        model = CustomUser
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "role",
            "upload_folder",
            "avatar",
            "is_superuser",
        )
        read_only_fields = ["id", "email", "is_staff", "is_superuser"]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.avatar:
            ret["avatar"] = f"http://127.0.0.1:8000{instance.avatar.url}"
            # ret["avatar"] = f"http://0.0.0.0:8000{instance.avatar.url}"
        else:
            ret["avatar"] = None
        return ret

    def get_avatar(self, obj):
        if obj.avatar and hasattr(obj.avatar, "url"):
            request = self.context.get("request")
            if request is not None:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None


class UsersSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = CustomUser
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "role",
            "upload_folder",
            "avatar",
            "is_superuser",
            "is_active",
        )
        read_only_fields = ["id", "email", "is_staff", "is_superuser"]


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)


# class RecipeEmailSubmitSerializer(serializers.Serializer):
#     class Meta:
#         model = CustomUser
#         fields = ('id','email','recipe')
