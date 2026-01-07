from rest_framework import viewsets, mixins
from FilkaRecepty.serializers import FoodSerializer, FoodTagSerializer,IngredientsSerializer, IngredientSerializer, StepSerializer, UnitSerializer,ImageFoodSerializer,UrlSerializer,UserSerializer,UsersSerializer,LoginSerializer
from FilkaRecepty.models import Foods, FoodTags,Steps, Ingredients ,Ingredient, Unit,ImageFood, Url,CustomUser,PasswordReset
from django.views.generic import ListView
from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib import messages,auth
from django.contrib.auth import authenticate
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.paginator import Paginator
from django.core.serializers import serialize
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from rest_framework import generics
from rest_framework import exceptions as rest_exceptions, response, decorators as rest_decorators, permissions as rest_permissions
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.shortcuts import render, redirect
# from rest_framework.pagination import  LimitOffsetPagination,PageNumberPagination  #CustomPagination,OneByOneItems,

# from FilkaRecepty.paginate import PageNumberPagination

from django.db.models import Q
from rest_framework.permissions import IsAuthenticated,AllowAny,IsAdminUser
from django.middleware import csrf


from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from FilkaRecepty.pagination import  BlogListCreatePagination ,NewPagePagination,LargeResultsSetPagination
from rest_framework.pagination import BasePagination, PageNumberPagination, NewPagePagination
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer,TokenRefreshSerializer
from rest_framework_simplejwt.exceptions import TokenError,InvalidToken
from rest_framework_simplejwt import tokens
from django.contrib.auth import get_user_model
from django.contrib.auth import logout
from django.conf import settings
from django.urls import reverse
from django.core.mail import EmailMessage

from typing import Any, Dict
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.settings import api_settings

from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.exceptions import InvalidToken
import unicodedata
from django.db.models.signals import m2m_changed, post_delete
from django.db.models import Value
from django.db.models.functions import Replace
import re
from django.dispatch import receiver
import unicodedata
from django.db import transaction

def normalize_text(text: str) -> str:
    """
    Remove diacritics from Slovak (or any accented) characters.
    Example: 'čokoláda' -> 'cokolada'
    """
    return ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )

# @receiver(m2m_changed, sender=Foods.images.through)
# def cleanup_images_on_food_change(sender, instance, action, reverse, pk_set, **kwargs):
#     if action in ["post_remove", "post_clear"]:
#         for pk in pk_set or []:
#             image = ImageFood.objects.get(pk=pk)
#             if not image.images.exists():  # no Foods using this image
#                 image.delete()


# @receiver(post_delete, sender=Foods)
# def cleanup_images_on_food_delete(sender, instance, **kwargs):
#     for image in instance.images.all():
#         if not image.images.exists():  # no other Foods using this image
#             image.delete()
class DiacriticInsensitiveSearchFilter(SearchFilter):
    """
    SearchFilter that removes Slovak diacritics from BOTH the DB fields
    and the search terms.
    """

    # Map of Slovak diacritics to base chars
    diacritic_map = {
        'á': 'a', 'ä': 'a', 'č': 'c', 'ď': 'd', 'ľ': 'l', 'ĺ': 'l',
        'ň': 'n', 'ó': 'o', 'ô': 'o', 'ŕ': 'r', 'š': 's', 'ť': 't',
        'ú': 'u', 'ý': 'y', 'ž': 'z',
        'Á': 'A', 'Ä': 'A', 'Č': 'C', 'Ď': 'D', 'Ľ': 'L', 'Ĺ': 'L',
        'Ň': 'N', 'Ó': 'O', 'Ô': 'O', 'Ŕ': 'R', 'Š': 'S', 'Ť': 'T',
        'Ú': 'U', 'Ý': 'Y', 'Ž': 'Z',
    }

    def normalize_queryset(self, queryset, search_fields):
        """
        Annotate queryset with diacritic-free versions of search fields.
        """
        annotations = {}
        for field in search_fields:
            norm_field = f"norm_{re.sub('[^0-9a-zA-Z_]', '_', field)}"
            expr = Replace(field, Value(" "), Value(" "))  # placeholder

            # Apply all replacements in diacritic_map
            for src, target in self.diacritic_map.items():
                expr = Replace(expr, Value(src), Value(target))

            annotations[norm_field] = expr

        return queryset.annotate(**annotations)

    def get_search_terms(self, request):
        params = super().get_search_terms(request)
        return [normalize_text(p) for p in params]

    def filter_queryset(self, request, queryset, view):
        search_fields = self.get_search_fields(request, view)
        search_terms = self.get_search_terms(request)

        if not search_fields or not search_terms:
            return queryset

        # normalize DB side
        queryset = self.normalize_queryset(queryset, search_fields)

        orm_lookups = [
            f"norm_{re.sub('[^0-9a-zA-Z_]', '_', field)}__icontains"
            for field in search_fields
        ]

        for term in search_terms:
            or_queries = Q()
            for lookup in orm_lookups:
                or_queries |= Q(**{lookup: term})
            queryset = queryset.filter(or_queries)

        return queryset  
# class DiacriticInsensitiveSearchFilter(SearchFilter):
#     """
#     Custom SearchFilter that removes diacritics from search terms
#     so searching works with/without accents.
#     """

#     def get_search_terms(self, request):
#         params = super().get_search_terms(request)
#         return [normalize_text(p) for p in params]

#     def filter_queryset(self, request, queryset, view):
#         search_fields = self.get_search_fields(request, view)
#         search_terms = self.get_search_terms(request)

#         if not search_fields or not search_terms:
#             return queryset

#         # Build a Q object for each search term/field
#         orm_lookups = [
#             self.construct_search(str(search_field))
#             for search_field in search_fields
#         ]

#         base = queryset
#         for search_term in search_terms:
#             or_queries = Q()
#             for lookup in orm_lookups:
#                 # Use icontains on normalized text
#                 or_queries |= Q(**{lookup: search_term})
#             base = base.filter(or_queries)
#         return base
      
class FoodViewSet(viewsets.ModelViewSet):
    # permission_classes = (IsAuthenticated,)
    serializer_class = FoodSerializer
    queryset = Foods.objects.all() 
    pagination_class = BlogListCreatePagination
    # filter_backends = [SlovakAccentInsensitiveSearchFilter,OrderingFilter]
    filter_backends = [DjangoFilterBackend,DiacriticInsensitiveSearchFilter,OrderingFilter]
    filterset_fields  = ['foodTags__foodTag'] 
    search_fields  = ['name', 'steps__step', 'ingredients__ingredientName__ingredient']
    # search_fields  = [ 'ingredients__ingredientName__ingredient']
    ordering_fields = ['name','date']
    ordering = ['-date']

    def get_queryset(self):
            queryset = Foods.objects.all()
            search_query = self.request.query_params.get('search', '')

            if search_query:
                search_query = self.remove_accents(search_query.lower())  # Normalize input

                # Store matching object IDs instead of full objects
                matching_ids = []
                for obj in queryset:
                    if hasattr(obj, 'name') and isinstance(obj.name, str):
                        name_normalized = self.remove_accents(obj.name.lower())
                    else:
                        name_normalized = ''

                    if hasattr(obj, 'steps'):
                        for st in obj.steps.all():
                            if isinstance(st.step, str):
                                description_normalized = self.remove_accents(st.step.lower())
                            else:
                                description_normalized = ''
                    # if hasattr(obj, 'step') and isinstance(obj.steps, str):

                    #     description_normalized = self.remove_accents(obj.steps.lower())
                    # else:
                    #     description_normalized = ''

                    if search_query in name_normalized or search_query in description_normalized:
                        matching_ids.append(obj.id)  # Store ID instead of object

                # Return a QuerySet filtered by the matched IDs (preserves ordering)
                return queryset.filter(id__in=matching_ids)

            return queryset  # Default QuerySet

    def remove_accents(self, text):
            """ Remove diacritics from Slovak text safely. """
            if not isinstance(text, str):  # Ensure input is a string
                return text
            nfkd_form = unicodedata.normalize('NFKD', text)
            return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])


class FoodTagsViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = FoodTagSerializer
    queryset = FoodTags.objects.all()       

class StepsViewSet(viewsets.ModelViewSet):
    # permission_classes = (IsAuthenticated,)
    serializer_class = StepSerializer
    queryset = Steps.objects.all()      

    def get_queryset(self):
        queryset = super().get_queryset()
        food = self.request.query_params.get("food")  # ?food=...
        if food:
            queryset = queryset.filter(food__id=food)  # if you want by name
            # or: queryset = queryset.filter(food_id=food)  # if you want by id
        return queryset    
class UrlViewSet(viewsets.ModelViewSet):
    # permission_classes = (IsAuthenticated,)
    serializer_class = UrlSerializer
    queryset = Url.objects.all()  

    def get_queryset(self):
        queryset = super().get_queryset()
        food = self.request.query_params.get("food")  # ?food=...
        if food:
            queryset = queryset.filter(food__id=food)  # if you want by name
            # or: queryset = queryset.filter(food_id=food)  # if you want by id
        return queryset       


class IngredientsViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = IngredientsSerializer
    queryset = Ingredients.objects.all()   

    def perform_create(self, serializer):
        with transaction.atomic():
            serializer.save()

    def perform_update(self, serializer):
        with transaction.atomic():
            serializer.save()

    def perform_destroy(self, instance):
        with transaction.atomic():
            instance.delete()

class IngredientViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()   

    def perform_create(self, serializer):
        with transaction.atomic():
            serializer.save()

    def perform_update(self, serializer):
        with transaction.atomic():
            serializer.save()

    def perform_destroy(self, instance):
        with transaction.atomic():
            instance.delete()

class UnitViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = UnitSerializer
    queryset = Unit.objects.all()          

    def perform_create(self, serializer):
        with transaction.atomic():
            serializer.save()

    def perform_update(self, serializer):
        with transaction.atomic():
            serializer.save()

    def perform_destroy(self, instance):
        with transaction.atomic():
            instance.delete()
            
class ImageFoodViewSet(viewsets.ModelViewSet):
    # permission_classes = (IsAuthenticated,)
    serializer_class = ImageFoodSerializer
    queryset = ImageFood.objects.all()  

    def get_queryset(self):
        queryset = super().get_queryset()
        food = self.request.query_params.get("food")  # ?food=...
        if food:
            queryset = queryset.filter(food__id=food)  # if you want by name
            # or: queryset = queryset.filter(food_id=food)  # if you want by id
        return queryset    

class UsersViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = UsersSerializer
    queryset = CustomUser.objects.all()       




class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer
    
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer

    def post(self, request, *args, **kwargs):

        # Proceed with the parent method to handle token generation
        try:
            response = super().post(request, *args, **kwargs)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        # get username from form submission
        email = request.data["email"]
        if email:
            # Add user details to the response

            user = CustomUser.objects.get(email=email)
            user_serializer = UserSerializer(user)
            response.data['user'] = user_serializer.data

        return response
@method_decorator(csrf_protect, name='dispatch')
class RegisterView(APIView):
    permission_classes = (AllowAny, )
    http_method_names = ['post']

    def post(self, request,*args, **kwargs):
        password = request.data["password"]
        email = request.data["email"] 
        if CustomUser.objects.filter(email=email).exists():
             return Response(
                data={"success": False, "message": "email"},
                status=status.HTTP_409_CONFLICT,
            )
        serializer = UserSerializer(data=self.request.data)
        if serializer.is_valid():
            get_user_model().objects.create_user(**serializer.validated_data)





            return Response(status=HTTP_201_CREATED)
        return Response(status=HTTP_400_BAD_REQUEST, data={'errors': serializer.errors})
    
class UserView(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request):
      user = self.request.user
      if user.is_superuser:
        items = CustomUser.objects.all()
        serializer = UsersSerializer(items, many=True)
      return Response(serializer.data, status=status.HTTP_200_OK)
    
class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated,]
    # permission_classes = (AllowAny, )

    def post(self, request):
        auth.logout(request)
        return Response({'detail': 'Successfully logged out.'},status=status.HTTP_204_NO_CONTENT)
    
@api_view(('GET',))
def logout_view(request):
    auth.logout(request)
    return Response({'detail': 'Successfully logged out.'},status=status.HTTP_204_NO_CONTENT)



class CookieTokenObtainPairView(TokenObtainPairView):
  def finalize_response(self, request, response, *args, **kwargs):
    email = request.data["email"]
    if email:
        user = CustomUser.objects.get(email=email)
        user_serializer = UserSerializer(user)
        response.data['user'] = user_serializer.data
    if response.data.get('refresh'):
        cookie_max_age = 3600 * 24 * 14 # 14 days
        response.set_cookie('refresh_token', response.data['refresh'], max_age=cookie_max_age, httponly=True )
        del response.data['refresh']
    return super().finalize_response(request, response, *args, **kwargs)




class GetUser(TokenRefreshSerializer):
    token_class = RefreshToken
    
    def validates_user(self, attrs: Dict[str, Any]) -> Dict[str, str]:
        refresh = self.token_class(attrs["refresh"])
        user_id = refresh.payload.get(api_settings.USER_ID_CLAIM, None)
        email = CustomUser.objects.get(id = user_id)
        user_serializer = UserSerializer( email)
        return ({"access":super().validate(attrs),"user":user_serializer.data})
                 
         
        

    
class CookieTokenRefreshSerializer(GetUser):


    refresh = None

    def validate(self, attrs):
        attrs['refresh'] = self.context['request'].COOKIES.get('refresh')
        if attrs['refresh']:
            return super().validates_user(attrs)
        else:
            raise InvalidToken(
                'No valid token found in cookie \'refresh\'')


class CookieTokenRefreshView(TokenRefreshView):
    serializer_class  = CookieTokenRefreshSerializer

    def finalize_response(self, request, response, *args, **kwargs):
        
        if response.data.get("refresh"):
            response.set_cookie(
                key=settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'],
                value=response.data['refresh'],
                expires=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
            )
            del response.data["refresh"]

        response["X-CSRFToken"] = request.COOKIES.get("csrftoken")
        return super().finalize_response(request, response, *args, **kwargs)
    
    
def get_user_tokens(user):
    refresh = tokens.RefreshToken.for_user(user)
    return {
            "refresh_token": str(refresh),
            "access_token": str(refresh.access_token)
        }
    
@rest_decorators.api_view(["POST"])
@rest_decorators.permission_classes([])
def loginView(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    email = serializer.validated_data["email"]
    password = serializer.validated_data["password"]

    user = authenticate(email=email, password=password)
    if user is not None:
            tokens = get_user_tokens(user)
            res = response.Response()
            
            res.set_cookie(
                key=settings.SIMPLE_JWT['AUTH_COOKIE'],
                value=tokens["access_token"],
                expires=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
            )

            res.set_cookie(
                key=settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'],
                value=tokens["refresh_token"],
                expires=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
            )

            res.data = {"access_token":tokens.get("access_token")}

            user_serializer = UserSerializer(user)
            res.data['user'] = user_serializer.data

            # res.set_cookie(
            #     key=settings.SIMPLE_JWT['AUTH_COOKIE_USER'],
            #     value=user_serializer.data['email'],
            #     httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],

            # )

            
            res["X-CSRFToken"] = csrf.get_token(request)
            return res
    raise rest_exceptions.AuthenticationFailed(
        "Email or Password is incorrect!")


@method_decorator(csrf_protect, name='dispatch')
class ForgotPassword(APIView):
    permission_classes = (AllowAny, )

    
    def post(self, request, *args, **kwargs):
        if request.method == "POST":
            print("request", request)
            email = request.POST.get('email')
            print("Email", email)
            email = request.data["email"] 
             
            if CustomUser.objects.filter(email=email).exists():
                user =  CustomUser.objects.get(email=email)
                new_password_reset = PasswordReset(user=user)
                new_password_reset.save()
                domain= 'localhost:3000'
                reset_password= 'reset_password'
                full_password_reset_url = f'{request.scheme}://{domain}/{reset_password}/{new_password_reset.reset_id}/'
                email_body = f'Reset your password using the link below:\n\n\n{full_password_reset_url}'
                email_message = EmailMessage(
                'Reset your password', 
                email_body,
                settings.EMAIL_HOST_USER, 
                [email] 
            )
                email_message.fail_silently = True
                email_message.send()

                return Response(status=HTTP_201_CREATED,
                    data={'url_reset' :'password-reset-sent', 'reset_id':new_password_reset.reset_id})



            return Response(
                data={"success": False, "message": f"Provided email: '{email} ' does not exist"},
                status=status.HTTP_409_CONFLICT,
                )
        return Response(
                
                status=status.HTTP_409_CONFLICT,
                )
    
@method_decorator(ensure_csrf_cookie, name='dispatch')
class GetCSRFToken(APIView):
    permission_classes = (permissions.AllowAny, )

    def get(self, request, format=None):
        # resp=Response()
        # resp.set_cookie("testing","testing_token",sametime="String")
        # return resp
        # print("CSFRTOken GET")
        return Response({ 'success': 'CSRF cookie set' })


@method_decorator(csrf_protect, name='dispatch')
class ResetPassword(APIView):
    permission_classes = (AllowAny, )
    def post(self,request):
        data = self.request.data

        password = data['password']
        confirm_password = data['confirm_password']
        reset_id  = data['reset_id']
        password_reset_id = PasswordReset.objects.get(reset_id=reset_id)
        if password_reset_id:
                
                print("password_reset_id :",password_reset_id)
                passwords_have_error = False                   
                if password != confirm_password:
                            passwords_have_error = True
                            print("passwords do not match")
                            return Response(
                        data={"success": False, "message": 'Passwords do not match'},
                        status=status.HTTP_409_CONFLICT,
                        )

                if len(password) < 8:
                            passwords_have_error = True
                            return Response(
                        data={"success": False, "message": 'Password must be at least 8 characters long'},
                        status=status.HTTP_409_CONFLICT,
                            )
                expiration_time = password_reset_id.created_when + timezone.timedelta(seconds=5)
                print("expiration_time :",expiration_time)
                print("timezone.now() :",timezone.now())
                if timezone.now() > expiration_time:
                            passwords_have_error = True
                            password_reset_id.delete()
                            return Response(
                        data={"success": False, "message": 'Cas vyprsal'},
                        status=status.HTTP_408_REQUEST_TIMEOUT,
                            )
                            
                if not passwords_have_error:
                            user = password_reset_id.user
                            user.set_password(password)
                            user.save()
                            password_reset_id.delete()
                            return Response(
                        data={"success": True, "message": 'Password reset. Proceed to login'},
                        status=status.HTTP_201_CREATED,
                        )

        else :

            return Response(
                        data={"success": False, "message":'Invalid reset id' },
                        status=status.HTTP_409_CONFLICT,
                        )
                    

@method_decorator(csrf_protect, name='dispatch')
class RegisterNewAccount(APIView):
    permission_classes = (IsAdminUser, )
    def post(self,request):
        data = self.request.data
        first_name = data['first_name']
        last_name = data['last_name']
        email = data['email']

        if CustomUser.objects.filter(email=email).exists():
            return Response(
                data={"success": False, "message": f"Provided email: '{email} ' is alredy registered!"},
                status=status.HTTP_409_CONFLICT,
                )
        else: 
            
            password = CustomUser.objects.make_random_password(12)
            new_user = CustomUser.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email, 
                password=password
            )

            domain= 'localhost:3000'
            reset_password= 'login'
            full_password_reset_url = f'{request.scheme}://{domain}/{reset_password}/'
                # full_password_reset_url = f'{request.scheme}://{request.get_host()}{password_reset_url}'
            email_body = f'Bol Vám vytvorený nový účet na stránke www.filka.sk/. Dole uvedené prístupové heslo si zmeňte v čo najkratšej dobe.\n\nVaše prístupové údaje sú:\nKrsne meno: {new_user.first_name}\nPriezvisko: {new_user.last_name}\nEmailova adresa : {new_user.email}\nPrístupové heslo : {password}\n\n\n\nPre pristup na stranku kliknite na dole uvedený link: \n{full_password_reset_url}\n\nS pozdravom \nAdmin.'
            email_message = EmailMessage(
                'Novy ucet na stranke www.filka.sk/', # email subject
            email_body,
            settings.EMAIL_HOST_USER, # email sender
            [email] # email  receiver 
            )
            email_message.fail_silently = True
            email_message.send()

            return Response(
                        data={"success": True, "message": 'New account for {first_name}{last_name}{email} has been created!'},
                        status=status.HTTP_201_CREATED,
                        )


from operator import attrgetter

class RecipeEmailSubmit(APIView):


    def get(self,request):
        data = self.request.data
        recipe = data['recipe']
        print(recipe) 
        foodID = Foods.objects.get(id=recipe)
        food_serializer = FoodSerializer(foodID)
        print (food_serializer.data)
        if food_serializer:
            name = food_serializer.data.get("name")
            print (name)
            ingredients = food_serializer.data.get("ingredients")
            print (ingredients)
            steps = food_serializer.data.get("steps")
            ingredietsBox=[]
            stepsBox=[]
            for x in ingredients:
                    print (x)
                    ingre = Ingredients.objects.get(id=x)
                    ingre_serializer = IngredientsSerializer(ingre)
                    quantity = ingre_serializer.data.get("quantity")
                    units = ingre_serializer.data.get("units")
                    ingredientName = ingre_serializer.data.get("ingredientName")
                    for y in units:
                        unit = Unit.objects.get(id=y)
                        unit_serializer = UnitSerializer(unit)
                        unitname = unit_serializer.data.get("unit")
                        for t in ingredientName:
                            ingrename = Ingredient.objects.get(id=t)
                            ingrename_serializer = IngredientSerializer(ingrename)
                            ingredientname = ingrename_serializer.data.get("ingredient")
                            ingredietsBox.insert(1,f'{quantity}  {unitname}  {ingredientname}\n') 
            for index,x  in enumerate(steps):
                step = Steps.objects.get(id=x)
                step_serializer = StepSerializer(step)
                stepsBox.insert(3,step_serializer.data)
      
            a = sorted(stepsBox, key=lambda x: x["position"], reverse=False)
            print(a)
            newStepList = []
            for i in enumerate(a) :
                newStepList.insert(i.step)
            print(newStepList)


            return Response(
                        data={"success": True, "message": 'Recept odoslany!'},
                        status=status.HTTP_201_CREATED,
                        )
