import re
import unicodedata
from typing import Any, Dict

from django.conf import settings
from django.contrib import auth
from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.db import transaction
from django.db.models import ProtectedError, Q, Value
from django.db.models.functions import Replace
from django.middleware import csrf
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import decorators as rest_decorators

# from rest_framework.pagination import  LimitOffsetPagination,PageNumberPagination  #CustomPagination,OneByOneItems,
# from FilkaRecepty.paginate import PageNumberPagination
from rest_framework import exceptions as rest_exceptions
from rest_framework import permissions, response, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework_simplejwt import tokens
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from FilkaRecepty.models import (
    CustomUser,
    Foods,
    FoodTags,
    ImageFood,
    Ingredient,
    Ingredients,
    PasswordReset,
    Steps,
    TagGroups,
    Unit,
    Url,
)
from FilkaRecepty.pagination import BlogListCreatePagination
from FilkaRecepty.serializers import (
    FoodSerializer,
    FoodTagSerializer,
    ImageFoodSerializer,
    IngredientSerializer,
    IngredientsSerializer,
    LoginSerializer,
    StepSerializer,
    TagGroupSerializer,
    UnitSerializer,
    UrlSerializer,
    UserSerializer,
    UsersSerializer,
)


def normalize_text(text: str) -> str:
    """
    Remove diacritics from Slovak (or any accented) characters.
    Example: 'čokoláda' -> 'cokolada'
    """
    return "".join(
        c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn"
    )


class DiacriticInsensitiveSearchFilter(SearchFilter):
    """
    SearchFilter that removes Slovak diacritics from BOTH the DB fields
    and the search terms.
    """

    # Map of Slovak diacritics to base chars
    diacritic_map = {
        "á": "a",
        "ä": "a",
        "č": "c",
        "ď": "d",
        "ľ": "l",
        "ĺ": "l",
        "ň": "n",
        "ó": "o",
        "ô": "o",
        "ŕ": "r",
        "š": "s",
        "ť": "t",
        "ú": "u",
        "ý": "y",
        "ž": "z",
        "Á": "A",
        "Ä": "A",
        "Č": "C",
        "Ď": "D",
        "Ľ": "L",
        "Ĺ": "L",
        "Ň": "N",
        "Ó": "O",
        "Ô": "O",
        "Ŕ": "R",
        "Š": "S",
        "Ť": "T",
        "Ú": "U",
        "Ý": "Y",
        "Ž": "Z",
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


class FoodViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = FoodSerializer
    queryset = Foods.objects.all()
    pagination_class = BlogListCreatePagination

    filter_backends = [
        DjangoFilterBackend,
        DiacriticInsensitiveSearchFilter,
        OrderingFilter,
    ]
    filterset_fields = ["foodTags__foodTag"]
    search_fields = ["name", "steps__step", "ingredients__ingredientName__ingredient"]
    # search_fields  = [ 'ingredients__ingredientName__ingredient']
    ordering_fields = ["name", "date"]
    ordering = ["-date"]

    def get_queryset(self):
        queryset = Foods.objects.all()
        search_query = self.request.query_params.get("search", "")

        if search_query:
            search_query = self.remove_accents(search_query.lower())

            matching_ids = []
            for obj in queryset:
                if hasattr(obj, "name") and isinstance(obj.name, str):
                    name_normalized = self.remove_accents(obj.name.lower())
                else:
                    name_normalized = ""

                if hasattr(obj, "steps"):
                    for st in obj.steps.all():
                        if isinstance(st.step, str):
                            description_normalized = self.remove_accents(
                                st.step.lower()
                            )
                        else:
                            description_normalized = ""

                if (
                    search_query in name_normalized
                    or search_query in description_normalized
                ):
                    matching_ids.append(obj.id)

            return queryset.filter(id__in=matching_ids)

        return queryset

    def remove_accents(self, text):
        """Remove diacritics from Slovak text safely."""
        if not isinstance(text, str):
            return text
        nfkd_form = unicodedata.normalize("NFKD", text)
        return "".join([c for c in nfkd_form if not unicodedata.combining(c)])


class FoodTagsViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = FoodTagSerializer
    queryset = FoodTags.objects.all()

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]
    filterset_fields = ["foodTags"]

    search_fields = ["foodTags"]
    ordering_fields = ["foodTags"]
    ordering = ["foodTags"]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)

        except ValidationError as e:
            error_message = e.message if hasattr(e, "message") else str(e)
            return Response(
                {"detail": error_message},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except ProtectedError:
            return Response(
                {
                    "detail": "Tento záznam je chránený. Najskôr musíte odstrániť všetky prepojené položky."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception:
            return Response(
                {"detail": "Vyskytla sa neočakávaná chyba na serveri."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def get_queryset(self):
        queryset = FoodTags.objects.all()
        search_query = self.request.query_params.get("search", None)

        if search_query:
            search_query = self.remove_accents(search_query.lower())

            matching_ids = []
            for obj in queryset:
                if obj.ingredient:
                    normalized_db_value = self.remove_accents(obj.ingredient.lower())
                    if search_query in normalized_db_value:
                        matching_ids.append(obj.id)

            return queryset.filter(id__in=matching_ids)

        return queryset

    def remove_accents(self, text):
        """Identická funkcia na normalizáciu textu ako vo FoodViewSet."""
        if not isinstance(text, str):
            return text
        nfkd_form = unicodedata.normalize("NFKD", text)
        return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

    def perform_create(self, serializer):
        with transaction.atomic():
            serializer.save()

    def perform_update(self, serializer):
        with transaction.atomic():
            serializer.save()

    def perform_destroy(self, instance):
        with transaction.atomic():
            instance.delete()


class TagGroupViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = TagGroupSerializer
    queryset = TagGroups.objects.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        except ProtectedError:
            return Response(
                {"detail": "Túto skupinu nie je možné vymazať, pokiaľ obsahuje tagy."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except ValidationError as e:
            # Toto zachytí tvoju vlastnú funkciu delete na FoodTags
            return Response({"detail": e.message}, status=status.HTTP_400_BAD_REQUEST)

        except Exception:
            # Ak sa stane niečo iné, vrátiš 500
            return Response(
                {"detail": "Problem so serverom."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UsersViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = UsersSerializer
    queryset = CustomUser.objects.all()


class StepsViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = StepSerializer
    queryset = Steps.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        food = self.request.query_params.get("food")
        if food:
            queryset = queryset.filter(food__id=food)

        return queryset


class UrlViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = UrlSerializer
    queryset = Url.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        food = self.request.query_params.get("food")
        if food:
            queryset = queryset.filter(food__id=food)

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
    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]
    filterset_fields = ["ingredient"]

    search_fields = ["ingredient"]
    ordering_fields = ["ingredient"]
    ordering = ["ingredient"]

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        search_query = self.request.query_params.get("search", None)

        if search_query:
            search_query = self.remove_accents(search_query.lower())

            matching_ids = []
            for obj in queryset:
                if obj.ingredient:
                    normalized_db_value = self.remove_accents(obj.ingredient.lower())
                    if search_query in normalized_db_value:
                        matching_ids.append(obj.id)

            return queryset.filter(id__in=matching_ids)

        return queryset

    def remove_accents(self, text):
        """Identická funkcia na normalizáciu textu ako vo FoodViewSet."""
        if not isinstance(text, str):
            return text
        nfkd_form = unicodedata.normalize("NFKD", text)
        return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

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
    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]
    filterset_fields = ["unit"]

    search_fields = ["unit"]
    ordering_fields = ["unit"]
    ordering = ["unit"]

    def get_queryset(self):
        queryset = Unit.objects.all()
        search_query = self.request.query_params.get("search", None)

        if search_query:
            search_query = self.remove_accents(search_query.lower())

            matching_ids = []
            for obj in queryset:
                if obj.unit:
                    normalized_name = self.remove_accents(obj.unit.lower())
                    if search_query in normalized_name:
                        matching_ids.append(obj.id)

            return queryset.filter(id__in=matching_ids)

        return queryset

    def remove_accents(self, text):
        if not isinstance(text, str):
            return text
        nfkd_form = unicodedata.normalize("NFKD", text)
        return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

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
    permission_classes = (IsAuthenticated,)
    serializer_class = ImageFoodSerializer
    queryset = ImageFood.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        food = self.request.query_params.get("food")
        if food:
            queryset = queryset.filter(food__id=food)

        return queryset


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer


@method_decorator(csrf_protect, name="dispatch")
class RegisterView(APIView):
    permission_classes = (AllowAny,)
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
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
        return Response(status=HTTP_400_BAD_REQUEST, data={"errors": serializer.errors})


class UsersView(APIView):
    permission_classes = (IsAuthenticated,)
    queryset = CustomUser.objects.all()

    def get(self, request):
        user = self.request.user

        if user.is_superuser:
            items = CustomUser.objects.all()
            serializer = UsersSerializer(items, many=True, context={"request": request})
        else:
            serializer = UserSerializer(user, context={"request": request})

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserLogoutView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request):
        response = Response(
            {"detail": "Successfully logged out."}, status=status.HTTP_204_NO_CONTENT
        )
        auth.logout(request)
        return response


@api_view(("GET",))
def logout_view(request):
    auth.logout(request)
    return Response(
        {"detail": "Successfully logged out."}, status=status.HTTP_204_NO_CONTENT
    )


class CookieTokenObtainPairView(TokenObtainPairView):
    def finalize_response(self, request, response, *args, **kwargs):
        email = request.data["email"]
        if email:
            user = CustomUser.objects.get(email=email)
            user_serializer = UserSerializer(user)
            response.data["user"] = user_serializer.data
        if response.data.get("refresh"):
            cookie_max_age = 3600 * 24 * 14  # 14 days
            response.set_cookie(
                "refresh_token",
                response.data["refresh"],
                max_age=cookie_max_age,
                httponly=True,
            )
            del response.data["refresh"]
        return super().finalize_response(request, response, *args, **kwargs)


class GetUser(TokenRefreshSerializer):
    token_class = RefreshToken

    def validates_user(self, attrs: Dict[str, Any]) -> Dict[str, str]:
        refresh = self.token_class(attrs["refresh"])
        user_id = refresh.payload.get(api_settings.USER_ID_CLAIM, None)
        email = CustomUser.objects.get(id=user_id)
        user_serializer = UserSerializer(email)
        return {"access": super().validate(attrs), "user": user_serializer.data}


class CookieTokenRefreshSerializer(GetUser):
    refresh = None

    def validate(self, attrs):
        attrs["refresh"] = self.context["request"].COOKIES.get("refresh")
        if attrs["refresh"]:
            return super().validates_user(attrs)
        else:
            raise InvalidToken("No valid token found in cookie 'refresh'")


class CookieTokenRefreshView(TokenRefreshView):
    serializer_class = CookieTokenRefreshSerializer

    def finalize_response(self, request, response, *args, **kwargs):
        if response.data.get("refresh"):
            response.set_cookie(
                key=settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"],
                value=response.data["refresh"],
                expires=settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"],
                secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
                httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
                samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
            )
            del response.data["refresh"]

        response["X-CSRFToken"] = request.COOKIES.get("csrftoken")
        return super().finalize_response(request, response, *args, **kwargs)


def get_user_tokens(user):
    refresh = tokens.RefreshToken.for_user(user)
    return {"refresh_token": str(refresh), "access_token": str(refresh.access_token)}


@rest_decorators.api_view(["POST"])
@rest_decorators.permission_classes([])
def loginView(request):
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return response.Response(
            {
                "message": "Chýbajúce údaje alebo nesprávny formát.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    serializer.is_valid(raise_exception=True)

    email = serializer.validated_data["email"]
    password = serializer.validated_data["password"]

    user = authenticate(email=email, password=password)
    if user is not None:
        if not user.is_active:
            return response.Response(
                {"message": "Účet je deaktivovaný."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        tokens = get_user_tokens(user)
        res = response.Response(
            {
                "success": True,
            },
            status=status.HTTP_200_OK,
        )
        res.set_cookie(
            key=settings.SIMPLE_JWT["AUTH_COOKIE"],
            value=tokens["access_token"],
            expires=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
            secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
            httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
            samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
        )

        res.set_cookie(
            key=settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"],
            value=tokens["refresh_token"],
            expires=settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"],
            secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
            httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
            samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
        )

        res.data = {"access_token": tokens.get("access_token")}

        user_serializer = UserSerializer(user)
        res.data["user"] = user_serializer.data

        # res.set_cookie(
        #     key=settings.SIMPLE_JWT['AUTH_COOKIE_USER'],
        #     value=user_serializer.data['email'],
        #     httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],

        # )

        res["X-CSRFToken"] = csrf.get_token(request)
        return res
    raise rest_exceptions.AuthenticationFailed("Zadaný email alebo heslo je neplatné!")


# def loginView(request):
#     serializer = LoginSerializer(data=request.data)
#     if not serializer.is_valid():
#         return response.Response(
#             {
#                 "message": "Chýbajúce údaje alebo nesprávny formát.",
#                 "errors": serializer.errors,
#             },
#             status=status.HTTP_400_BAD_REQUEST,
#         )
#     serializer.is_valid(raise_exception=True)

#     email = serializer.validated_data["email"]
#     password = serializer.validated_data["password"]

#     user = authenticate(email=email, password=password)
#     if user is not None:
#         if not user.is_active:
#             return response.Response(
#                 {"message": "Účet je deaktivovaný."},
#                 status=status.HTTP_401_UNAUTHORIZED,
#             )

#         tokens = get_user_tokens(user)
#         user_serializer = UserSerializer(user, context={"request": request})
#         res = response.Response(
#             {
#                 "access": tokens["access_token"],
#                 "user": user_serializer.data,
#                 "success": True,
#             },
#             status=status.HTTP_200_OK,
#         )

#         cookie_settings = {
#             "secure": settings.SIMPLE_JWT.get("AUTH_COOKIE_SECURE", False),
#             "httponly": settings.SIMPLE_JWT.get("AUTH_COOKIE_HTTP_ONLY", True),
#             "samesite": settings.SIMPLE_JWT.get("AUTH_COOKIE_SAMESITE", "Lax"),
#         }

#         res.set_cookie(
#             key=settings.SIMPLE_JWT["AUTH_COOKIE"],
#             value=tokens["access_token"],
#             expires=timezone.now() + settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
#             **cookie_settings,
#         )

#         res.set_cookie(
#             key=settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"],
#             value=tokens["refresh_token"],
#             expires=timezone.now() + settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"],
#             **cookie_settings,
#         )

#         res["X-CSRFToken"] = csrf.get_token(request)
#         return res
#     return response.Response(
#         {"message": "Nesprávny email alebo heslo."}, status=status.HTTP_401_UNAUTHORIZED
#     )


@method_decorator(csrf_protect, name="dispatch")
class ForgotPassword(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        if request.method == "POST":
            print("request", request)
            email = request.POST.get("email")
            print("Email", email)
            email = request.data["email"]

            if CustomUser.objects.filter(email=email).exists():
                user = CustomUser.objects.get(email=email)
                new_password_reset = PasswordReset(user=user)
                new_password_reset.save()
                domain = "localhost:3000"
                reset_password = "reset_password"
                full_password_reset_url = f"{request.scheme}://{domain}/{reset_password}/{new_password_reset.reset_id}/"
                email_body = f"Pre vytvorenie nového hesla kliknite na tento odkaz:\n\n\n{full_password_reset_url}"
                email_message = EmailMessage(
                    "Zmena helsa", email_body, settings.EMAIL_HOST_USER, [email]
                )
                email_message.fail_silently = True
                email_message.send()

                return Response(
                    status=HTTP_201_CREATED,
                    data={
                        "url_reset": "password-reset-sent",
                        "reset_id": new_password_reset.reset_id,
                    },
                )

            return Response(
                data={
                    "success": False,
                    "message": f"Zadaná e-mailová adresa,\n'{email}' neexistuje.",
                },
                status=status.HTTP_409_CONFLICT,
            )
        return Response(
            status=status.HTTP_409_CONFLICT,
        )


@method_decorator(ensure_csrf_cookie, name="dispatch")
class GetCSRFToken(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None):
        # resp=Response()
        # resp.set_cookie("testing","testing_token",sametime="String")
        # return resp
        # print("CSFRTOken GET")
        return Response({"success": "CSRF cookie set"})


@method_decorator(csrf_protect, name="dispatch")
class ResetPassword(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        data = self.request.data

        password = data["password"]
        confirm_password = data["confirm_password"]
        reset_id = data["reset_id"]
        password_reset_id = PasswordReset.objects.get(reset_id=reset_id)
        if password_reset_id:
            print("password_reset_id :", password_reset_id)
            passwords_have_error = False
            if password != confirm_password:
                passwords_have_error = True
                print("passwords do not match")
                return Response(
                    data={"success": False, "message": "Hesla sa nezhoduju"},
                    status=status.HTTP_409_CONFLICT,
                )

            if len(password) < 8:
                passwords_have_error = True
                return Response(
                    data={
                        "success": False,
                        "message": "Heslo musi mat aspon 8 znakov",
                    },
                    status=status.HTTP_409_CONFLICT,
                )
            expiration_time = password_reset_id.created_when + timezone.timedelta(
                hours=1
            )
            print("expiration_time :", expiration_time)
            print("timezone.now() :", timezone.now())
            if timezone.now() > expiration_time:
                passwords_have_error = True
                password_reset_id.delete()
                return Response(
                    data={"success": False, "message": "Čas na zmenu hesla vypršal"},
                    status=status.HTTP_408_REQUEST_TIMEOUT,
                )

            if not passwords_have_error:
                user = password_reset_id.user
                user.set_password(password)
                user.save()
                password_reset_id.delete()
                return Response(
                    data={
                        "success": True,
                        "message": "Password reset. Proceed to login",
                    },
                    status=status.HTTP_201_CREATED,
                )

        else:
            return Response(
                data={"success": False, "message": "Neplane reset id"},
                status=status.HTTP_409_CONFLICT,
            )


@method_decorator(csrf_protect, name="dispatch")
class RegisterNewAccount(APIView):
    permission_classes = (IsAdminUser,)

    def post(self, request):
        data = self.request.data
        first_name = data["first_name"]
        last_name = data["last_name"]
        email = data["email"]

        if CustomUser.objects.filter(email=email).exists():
            return Response(
                data={
                    "success": False,
                    "message": f"Účet s emailom: '{email} ' je už registrovaný!",
                },
                status=status.HTTP_409_CONFLICT,
            )
        else:
            password = CustomUser.objects.make_random_password(12)
            new_user = CustomUser.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
            )

            domain = "localhost:3000"
            reset_password = "login"
            full_password_reset_url = f"{request.scheme}://{domain}/{reset_password}/"
            # full_password_reset_url = f'{request.scheme}://{request.get_host()}{password_reset_url}'
            email_body = f"Bol Vám vytvorený nový účet na stránke www.filka.sk/. Dole uvedené prístupové heslo si zmeňte v čo najkratšej dobe.\n\nVaše prístupové údaje sú:\nKrsne meno: {new_user.first_name}\nPriezvisko: {new_user.last_name}\nEmailova adresa : {new_user.email}\nPrístupové heslo : {password}\n\n\n\nPre pristup na stranku kliknite na dole uvedený link: \n{full_password_reset_url}\n\nS pozdravom \nAdmin."
            email_message = EmailMessage(
                "Novy ucet na stranke www.rodinnerecepty.sk/",
                email_body,
                settings.EMAIL_HOST_USER,
                [email],
            )
            email_message.fail_silently = True
            email_message.send()

            return Response(
                data={
                    "success": True,
                    "message": "Nový účet pre {first_name}{last_name}{email} bol vytvorený!",
                },
                status=status.HTTP_201_CREATED,
            )


class RecipeEmailSubmit(APIView):
    def get(self, request):
        data = self.request.data
        recipe = data["recipe"]
        print(recipe)
        foodID = Foods.objects.get(id=recipe)
        food_serializer = FoodSerializer(foodID)
        print(food_serializer.data)
        if food_serializer:
            name = food_serializer.data.get("name")
            print(name)
            ingredients = food_serializer.data.get("ingredients")
            print(ingredients)
            steps = food_serializer.data.get("steps")
            ingredietsBox = []
            stepsBox = []
            for x in ingredients:
                print(x)
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
                        ingredietsBox.insert(
                            1, f"{quantity}  {unitname}  {ingredientname}\n"
                        )
            for index, x in enumerate(steps):
                step = Steps.objects.get(id=x)
                step_serializer = StepSerializer(step)
                stepsBox.insert(3, step_serializer.data)

            a = sorted(stepsBox, key=lambda x: x["position"], reverse=False)
            print(a)
            newStepList = []
            for i in enumerate(a):
                newStepList.insert(i.step)
            print(newStepList)

            return Response(
                data={"success": True, "message": "Recept odoslany!"},
                status=status.HTTP_201_CREATED,
            )
