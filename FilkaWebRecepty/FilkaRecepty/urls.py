from xml.dom.minidom import Document
from django.db import router
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from FilkaRecepty.views import FoodViewSet, FoodTagsViewSet, StepsViewSet,IngredientsViewSet, IngredientViewSet,UnitViewSet,ImageFoodViewSet # VolumeViewSet 


# from .views import home_view
from . import views

# from .views import home_view
router = routers.DefaultRouter()
# monsters will be accesible on
router.register('foods', FoodViewSet),
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
    path('', include(router.urls))
] 

urlpatterns += static (settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)