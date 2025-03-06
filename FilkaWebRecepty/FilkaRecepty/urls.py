from xml.dom.minidom import Document
from django.db import router
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView
from FilkaRecepty.views import FoodViewSet, FoodTagsViewSet, StepsViewSet,IngredientsViewSet, IngredientViewSet,UnitViewSet,ImageFoodViewSet,UrlViewSet ,EmailTokenObtainPairView, RegisterView, MyTokenObtainPairView,UserView,UsersViewSet,logout_view,UserLogoutView, CookieTokenRefreshView, CookieTokenObtainPairView,ForgotPassword,GetCSRFToken,ResetPassword,RegisterNewAccount,RecipeEmailSubmit


from . import views


router = routers.DefaultRouter()
router.register("foods", FoodViewSet),
router.register('foodTags',FoodTagsViewSet) 
router.register('steps',StepsViewSet) 
router.register('url',UrlViewSet) 
router.register('ingredients',IngredientsViewSet) 
router.register('ingredient',IngredientViewSet) 
router.register('unit',UnitViewSet) 
router.register('imagefood',ImageFoodViewSet) 
router.register('users',UsersViewSet) 



urlpatterns = [
    path('', include(router.urls)),
    path('register', RegisterNewAccount.as_view(), name='register'),
    path('login', views.loginView),
    path('logout', UserLogoutView.as_view(), name='logout'),
    path('api/token/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),
    path('forgot-password/', ForgotPassword.as_view(), name='forgot-password'),
    path('reset-password/', ResetPassword.as_view(), name='reset-password'),
    path('userslist/', UserView.as_view(), name='users'),
    path('csrf_cookie/', GetCSRFToken.as_view()),
    path('recipesubmit/', RecipeEmailSubmit.as_view(), name='recipesubmit'),


] 

urlpatterns += static (settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)