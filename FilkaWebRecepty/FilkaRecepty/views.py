from rest_framework import viewsets, mixins
from FilkaRecepty.serializers import FoodSerializer, FoodTagSerializer,IngredientsSerializer, IngredientSerializer, StepSerializer, UnitSerializer,ImageFoodSerializer,UrlSerializer#, VolumeSerializer
from FilkaRecepty.models import Foods, FoodTags,Steps, Ingredients ,Ingredient, Unit,ImageFood, Url#, Volume
from django.views.generic import ListView
from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib import messages
from rest_framework import permissions
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.paginator import Paginator
from django.core.serializers import serialize
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from rest_framework import generics
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import LimitOffsetPagination,PageNumberPagination , LargeResultsSetPagination #CustomPagination,OneByOneItems,
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from FilkaRecepty.pagination import BlogListCreatePagination


class FoodViewSet(viewsets.ModelViewSet):

    serializer_class = FoodSerializer
    queryset = Foods.objects.all().order_by("name")  
    pagination_class = LargeResultsSetPagination
    # pagination_class = BlogListCreatePagination
    filter_backends = [DjangoFilterBackend,SearchFilter]
    filterset_fields  = ['foodTags__foodTag'] 
    search_fields  = ['name']

# class SearchFoodViewSet(viewsets.ModelViewSet):
#     serializer_class = FoodSerializer
#     queryset = Foods.objects.all()#.order_by("name")
#     pagination_class = PageNumberPagination
#     filter_backends = [DjangoFilterBackend, SearchFilter]
#     search_fields  = ['name']

# class FilterFoodViewSet(viewsets.ModelViewSet):
# # class FilterFoodViewSet(generics.ListCreateAPIView):
#     serializer_class = FoodSerializer
#     queryset = Foods.objects.all()#.order_by("name")
#     pagination_class = BlogListCreatePagination
#     filter_backends = [DjangoFilterBackend,SearchFilter]
#     filterset_fields  = ['foodTags__foodTags'] 
#     search_fields  = ['name']


class FoodTagsViewSet(viewsets.ModelViewSet):
    serializer_class = FoodTagSerializer
    queryset = FoodTags.objects.all()       

class StepsViewSet(viewsets.ModelViewSet):
    serializer_class = StepSerializer
    queryset = Steps.objects.all()      

class UrlViewSet(viewsets.ModelViewSet):
    serializer_class = UrlSerializer
    queryset = Url.objects.all()         

class IngredientsViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientsSerializer
    queryset = Ingredients.objects.all()   

class IngredientViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()   

class UnitViewSet(viewsets.ModelViewSet):
    serializer_class = UnitSerializer
    queryset = Unit.objects.all()          

class ImageFoodViewSet(viewsets.ModelViewSet):
    serializer_class = ImageFoodSerializer
    queryset = ImageFood.objects.all()          





# class VolumeViewSet(viewsets.ModelViewSet):
#     serializer_class = VolumeSerializer
#     queryset = Volume.objects.all() 


 



# Create your views here.
# def home_view(request):
#     context = {}
#     context['form'] = GeeksForm()
#     return render( request, "home.html", context)
# class ImageAlbumViewSet(viewsets.ModelViewSet):
#     serializer_class = ImageAlbumSerializer
#     queryset = ImageAlbum.objects.all()     

# class ImageViewSet(viewsets.ModelViewSet):
#     serializer_class = VolumeSerializer
#     queryset = Image.objects.all()      


# Create your views here.
# def home_view(request):
#     context = {}
#     if request.method == "POST":
#         form = ImageForm(request.POST, request.FILES)
#         if form.is_valid():
#             name = form.cleaned_data.get("name")
#             img = form.cleaned_data.get("image_field")
#             queryset = Foods.objects.create(
#                                  name = name,
#                                  img = img
#                                  )
#             queryset.save()
#             print(queryset)
#     else:
#         form = ImageForm()
#     context['form']= form
#     return render(request, "home.html", context)           

# def create_project(request):

#     if request.method == "POST":
#         form = FoodForm(request.POST)
#         files = request.FILES.getlist("image")
#         if form.is_valid():
#             f = form.save(commit=False)
#             # f.user = request.user
#             f.save()
#             for i in files:
#                 Image.objects.create(project=f, image=i)
#             messages.success(request, "New Project Added")
#             return HttpResponseRedirect('foods')
#         else:
#             print(form.errors)
#     else:
#         form = FoodForm()
#         imageform = ImageForm()

#     return render(request, "create_project.html", {"form": form, "imageform": imageform})