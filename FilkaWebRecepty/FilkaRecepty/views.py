from rest_framework import viewsets, mixins
from FilkaRecepty.serializers import FoodSerializer, FoodTagSerializer,IngredientsSerializer, IngredientSerializer, StepSerializer, UnitSerializer,ImageFoodSerializer#, VolumeSerializer
from FilkaRecepty.models import Foods, FoodTags,Steps, Ingredients ,Ingredient, Unit,ImageFood#, Volume
#  
from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib import messages
from rest_framework import permissions
from rest_framework.parsers import MultiPartParser, FormParser



# class MyModelViewSet(viewsets.ModelViewSet):
#     queryset = MyModel.objects.order_by('-creation_date')
#     serializer_class = MyModelSerializer
#     parser_classes = (MultiPartParser, FormParser)
#     permission_classes = [
#         permissions.IsAuthenticatedOrReadOnly]

#     def perform_create(self, serializer):
#         serializer.save(creator=self.request.user)

class FoodViewSet(viewsets.ModelViewSet):
    serializer_class = FoodSerializer
    # parser_classes = (MultiPartParser, FormParser)
    # permission_classes = [
    #     permissions.IsAuthenticatedOrReadOnly]
    queryset = Foods.objects.all()   
    def post(self, request, *args, **kwargs):
            name = request.data['name']
            # image = request.data['image']
            ingredients = request.data['ingredients']
            steps = request.data['steps']
            date = request.data['date']
            foodTags = request.data['foodTags']

            Foods.objects.create(
                name=name, 
                ingredients=ingredients,
                steps=steps,
                date=date,
                foodTags=foodTags,
                # image=image
                )
            return HttpResponse({'message': 'Food created'}, status=200)

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