from rest_framework import viewsets, mixins
from FilkaRecepty.serializers import FoodSerializer, FoodTagSerializer,IngredientsSerializer, IngredientSerializer, StepSerializer, UnitSerializer,ImageFoodSerializer#, VolumeSerializer
from FilkaRecepty.models import Foods, FoodTags,Steps, Ingredients ,Ingredient, Unit,ImageFood#, Volume
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
from rest_framework.pagination import LimitOffsetPagination,PageNumberPagination, LargeResultsSetPagination #CustomPagination,OneByOneItems,
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from FilkaRecepty.pagination import BlogListCreatePagination




def list_foods_api(request):   
        page_number = request.GET.get("page", 1)
        per_page = request.GET.get("per_page", 2)
        startswith = request.GET.get("startswith", "")
        keywords = Foods.objects.filter(
            name__startswith=startswith
        )
        paginator = Paginator(keywords, per_page)
        page_obj = paginator.get_page(page_number)
        data = [{"name": kw.name} for kw in page_obj.object_list]
        payload = {
            "page": {
                "current": page_obj.number,
                "has_next": page_obj.has_next(),
                "has_previous": page_obj.has_previous(),
            },
            "data": data
        }
        return JsonResponse(payload)
def foodslist(request, page):
        # queryset = self.get_queryset()
        # serializer = FoodSerializer(queryset, many=True)
        # serializer_class = FoodSerializer(queryset, many=True)
        # serializer_class = FoodSerializer
        queryset = Foods.objects.all().order_by("name") 
        page_list = request.GET.get(page)
        # queryset = Foods.objects.all().order_by("name") 
        paginator = Paginator(queryset,2)
        page_object  = paginator.get_page(page_list)
        context = {"data": page_object}
        return Response (context)

# class MyModelViewSet(viewsets.ModelViewSet):
#     queryset = MyModel.objects.order_by('-creation_date')
#     serializer_class = MyModelSerializer
#     parser_classes = (MultiPartParser, FormParser)
#     permission_classes = [
#         permissions.IsAuthenticatedOrReadOnly]

#     def perform_create(self, serializer):
#         serializer.save(creator=self.request.user)

    # return render(request, "Forms/keyword_list.html", context)
class FoodViewSet(viewsets.ModelViewSet):

    serializer_class = FoodSerializer
    queryset = Foods.objects.all().order_by("name")  
    pagination_class = LargeResultsSetPagination
    # pagination_class = BlogListCreatePagination
    filter_backends = [DjangoFilterBackend,SearchFilter]
    filterset_fields  = ['foodTags__foodTag'] 
    search_fields  = ['name']
    # pagination_class = OneByOneItems
    # @list_route(methods=['get'], url_path='foods/(?P<page>[^/]+)')
    # def get_lection(self, request, pk):
    #     self.pagination_class = OneByOneItems
    #     queryset = self.filter_queryset(self.queryset.filter(course=pk))
    #     page = self.paginate_queryset(queryset)
    #     if page is not None:
    #         serializer = self.get_serializer(page, many=True)
    #         return self.get_paginated_response(serializer.data)
    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data) 
    
    # def post(self, request, *args, **kwargs):
    #         name = request.data['name']
    #         # image = request.data['image']
    #         ingredients = request.data['ingredients']
    #         steps = request.data['steps']
    #         date = request.data['date']
    #         foodTags = request.data['foodTags']

    #         Foods.objects.create(
    #             name=name, 
    #             ingredients=ingredients,
    #             steps=steps,
    #             date=date,
    #             foodTags=foodTags,
                
    #             # image=image
    #             )
    #         return HttpResponse({'message': 'Food created'}, status=200)
# @api_view()
# @permision_classes([allowAny])
class SearchFoodViewSet(viewsets.ModelViewSet):
    serializer_class = FoodSerializer
    queryset = Foods.objects.all()#.order_by("name")
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields  = ['name']

class FilterFoodViewSet(viewsets.ModelViewSet):
# class FilterFoodViewSet(generics.ListCreateAPIView):
    serializer_class = FoodSerializer
    queryset = Foods.objects.all()#.order_by("name")
    pagination_class = BlogListCreatePagination
    filter_backends = [DjangoFilterBackend,SearchFilter]
    filterset_fields  = ['foodTags__foodTags'] 
    search_fields  = ['name']
   

    # def get_queryset(self ):
    #     queryset = Foods.objects.all()
    #     return queryset 

    # def retrieve(self, request, *args, **kwargs):
    #      params = kwargs
    #      print(params)
    #      return Response({})
        #  return super().retrieve(request, *args, **kwargs)   
    
    # def get_queryset(self ):
    #     request = self.queryset
    #     if 'q' in request.GET:
    #           search_query = request.GET['g']
    #           if len(search_query)> 0:
    #             search_result = Foods.objects.filter(name__icontains=search_query)
    #     else:
    #           search_result = Foods.objects.all().order_by("name") 
    #     return search_result
    # def get_queryset(self):
    #     queryset = self.queryset
    #     query_set = queryset.filter(user=self.request.user)
    #     return query_set

         
    # parser_classes = (MultiPartParser, FormParser)
    # permission_classes = [
    #     permissions.IsAuthenticatedOrReadOnly]
   
    # context_object_name = 'page'
    # paginate_by = 2
    # def get_object(self):
    #     return get_object_or_404(Foods, pk=1)

    # def get_queryset(self):
    #     return Foods.objects.all().order_by('name')

    # def perform_destroy(self, instance):
    #     # instance.is_active = False
    #     instance.save()

    # def list(self,request):
    #     # queryset = self.get_queryset()
    #     # serializer = FoodSerializer(queryset, many=True)
    #     # serializer_class = FoodSerializer(queryset, many=True)
    #     queryset = Foods.objects.all().order_by("name") 
    #     serializer_class = FoodSerializer(queryset, many=True)
    #     page_list = request.GET.get("page")
    #     # queryset = Foods.objects.all().order_by("name") 
    #     paginator = Paginator(serializer_class,2)
    #     page_object  = paginator.get_page(page_list)
    #     context = {"data": page_object}
    #     return Response (context)

 
    


    # def perform_create(self, serializer):
    #     serializer.save(creator=self.request.user)            



class FoodTagsViewSet(viewsets.ModelViewSet):
    serializer_class = FoodTagSerializer
    queryset = FoodTags.objects.all()       

class StepsViewSet(viewsets.ModelViewSet):
    serializer_class = StepSerializer
    queryset = Steps.objects.all()      

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