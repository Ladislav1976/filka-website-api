from xml.dom.minidom import Document
from django.db import router
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from FilkaRecepty.views import FoodViewSet, FoodTagsViewSet, StepsViewSet,IngredientsViewSet, IngredientViewSet,UnitViewSet,ImageFoodViewSet, SearchFoodViewSet  ,FilterFoodViewSet


from . import views

# from .views import home_view
router = routers.DefaultRouter()
# monsters will be accesible on
router.register("foods", FoodViewSet),
router.register("foods/search", SearchFoodViewSet,basename='MyFoodsModel'),
router.register("foods/filter", FilterFoodViewSet,basename='MyFilterModel'),
# router.register('foodsearch' , SearcgFoodViewSet),
# router.register(r'^foods/(?P<id>[0-9]+)$', FoodViewSet),
# router.register("foods/<int:page>", FoodViewPagSet),
# router.register('foods', FoodViewSet,foodViewSet.list_foods),r"^articles/(?P<year>[0-9]{4})/$"
router.register('foodTags',FoodTagsViewSet) 
router.register('steps',StepsViewSet) 
router.register('ingredients',IngredientsViewSet) 
router.register('ingredient',IngredientViewSet) 
router.register('unit',UnitViewSet) 
router.register('imagefood',ImageFoodViewSet) 
# router.register('volume',VolumeViewSet) 
 


# router.register('image',ImageViewSet) 
# router.register('album',ImageAlbumViewSet) 
# router.register('images',home_view)

urlpatterns = [
    path('', include(router.urls)),
    # path('foods', include("FilkaRecepty.urls")),
    # path(
    #     "foods",
    #     views.foodslist, 
    #     name="foods"
    # ),
    # path(
    # "foods/<int:page>",
    #     views.foodslist, 
    #     name="foods-by-page"
    # )
    # # path(
    #     "foods/<int:page>",
    #     views.list_foods_api,
    #     name="foods-api"
    # ),
] 

urlpatterns += static (settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)