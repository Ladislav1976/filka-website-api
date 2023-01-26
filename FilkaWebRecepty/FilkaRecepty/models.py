from django.db import models
from django.db.models import Count
from django.db.models import F, Count
# # Create your models here.
# class FoodTags(models.Model):
#     foodTag = models.CharField(max_length=60, unique=True)
    
#     def __str__(self):
#         return self.foodTag  

# class Steps(models.Model):
#     step = models.CharField(max_length=500, unique=True)
    
#     def __str__(self):
#         return self.step           

# class Unit(models.Model):
#     unit = models.CharField(max_length=60, unique=True)
    
#     def __str__(self):
#         return self.unit    

# class Volume(models.Model):
#     volume = models.CharField(max_length=60, unique=True)
    
#     def __str__(self):
#         return self.volume                        
 
# class Ingredient(models.Model):
#     ingredient = models.CharField(max_length=60, unique=True)
    
#     def __str__(self):
#         return self.ingredient 

# class Ingredients(models.Model):
#     # id_ingredients= models.IntegerField()
#     units = models.ManyToManyField(Unit, related_name='units')
#     volumes = models.ManyToManyField(Volume, related_name='volumes')
#     ingredientName = models.ManyToManyField(Volume, related_name='ingredientName')
#     def __str__(self):
#         return self.ingredientName 


# def get_upload_path(instance, filename):
#     return '/'.join(['image', str(instance.name), filename])

# class Foods(models.Model):
#     name = models.CharField(max_length=60)
#     image = models.ImageField(blank=True, null=True, upload_to=get_upload_path, verbose_name ="Food image")
#     ingredients = models.ManyToManyField(Ingredients, related_name='ingredients')
#     steps = models.ForeignKey(
#         Steps,
#         to_field='step',
#         on_delete=models.CASCADE)
#     #     primary_key=True,
#     # ) 
#     date = models.DateField() 
#     foodTags = models.ManyToManyField(FoodTags, related_name='foodTags')
    
#     def __str__(self):
#         return self.name 

#     def __unicode__(self):
#         return self.name 

#     def image_img(self):
#         if self.image:
#             return u'<img src="%s" width="50" height="50" />' % self.image.url 
#         else:
#             return '(Sin imagen)'
#     image_img.short_description = 'Thumb'
#     image_img.allow_tags = True    





# Create your models here.
class FoodTags(models.Model):
    foodTag = models.CharField(max_length=60)
    
    def __str__(self):
        return self.foodTag  

class Steps(models.Model):
    step = models.CharField(max_length=500, unique=True)
    
    def __str__(self):
        return self.step           

class Unit(models.Model):
    unit = models.CharField(max_length=60, unique=True)
    
    def __str__(self):
        return self.unit    

# class Volume(models.Model):
#     volume = models.CharField(max_length=60, unique=True)
    
#     def __str__(self):
#         return self.volume                        
 
class Ingredient(models.Model):
    ingredient = models.CharField(max_length=60, unique=True)
    
    def __str__(self):
        return self.ingredient 

class Ingredients(models.Model):
    # ingredientsName= models.CharField(max_length=60)
    units = models.ManyToManyField(Unit, related_name='units')
    volume = models.CharField(max_length=60)
    # volumes = models.ManyToManyField(Volume, related_name='volumes')
    ingredientName = models.ManyToManyField(Ingredient, related_name='ingredientName')
    # def __str__(self):
    #     return self.units 
  





class Foods(models.Model):
    name = models.CharField(max_length=60)
    # image = models.ImageField(blank=True, null=True, upload_to=get_upload_path, verbose_name ="Food image")
    ingredients = models.ManyToManyField(Ingredients, related_name='ingredients')
    steps=models.ManyToManyField(Steps, related_name='steps')
    # steps = models.ForeignKey(
    #     Steps,
    #     null=True,
    #     # to_field='step',
    #     on_delete=models.CASCADE)
    # #     primary_key=True,
    # # ) 
    date = models.DateTimeField()
    foodTags = models.ManyToManyField(FoodTags, related_name='foodTags')
    

    def __str__(self):
        return self.name


def get_upload_path(instance, filename):
    return '/'.join(['image', str(instance.name), filename])
class ImageFood(models.Model):
    name = models.CharField(max_length=255)
    food = models.ForeignKey(Foods, on_delete=models.CASCADE)
    image = models.ImageField(blank=True, null=True, upload_to=get_upload_path, verbose_name ="Food image")
    date = models.DateTimeField()

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name 

    def image_img(self):
        if self.image:
            return u'<img src="%s" width="50" height="50" />' % self.image.url 
        else:
            return '(Sin imagen)'
    image_img.short_description = 'Thumb'
    image_img.allow_tags = True    