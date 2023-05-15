from django.contrib.auth import login, authenticate, logout, update_session_auth_hash

from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.exceptions import NotFound
from rest_framework.viewsets import GenericViewSet
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from drf_yasg.utils import swagger_auto_schema

from .models import User, UserType
from .serializers import LoginSerializer, UserSerializer, UserTypeSerializer, PasswordChangeSerializer
from .permissions import IsAuthenticatedNonAdminUser, UserAccessPermission
from .documentations import (
    logout_view_operation_description, login_view_operation_description, user_create_operation_description,
    user_partial_update_operation_description, change_password_operation_description, not_found_response,
    UserResponse, UserListResponse
)



@swagger_auto_schema(method='POST', security=[], request_body=LoginSerializer, 
                     responses={200: UserResponse, 400: 'message: No matching user.\nbody의 username, password 틀렸을 때\n'}, 
                     operation_description=login_view_operation_description)
@api_view(['POST'])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    username = serializer.validated_data['username']
    password = serializer.validated_data['password']
    user = authenticate(username=username, password=password)

    if user is None:
        raise NotFound('No matching user.')

    login(request, user)
    return Response(UserSerializer(user).data)


@swagger_auto_schema(method='POST', security=[], responses={200: ''}, operation_description=logout_view_operation_description)
@api_view(['POST'])
@authentication_classes([])
def logout_view(request):
    logout(request)
    return Response()


@swagger_auto_schema(method='GET', security=[], responses={200: UserTypeSerializer(many=True)}, operation_description='모든 user type 데이터 조회')
@api_view(['GET'])
@authentication_classes([])
def get_all_user_type(request):
    queryset = UserType.objects.all()
    serializer = UserTypeSerializer(queryset, many=True)
    return Response(serializer.data)


@swagger_auto_schema(method='PATCH', request_body=PasswordChangeSerializer, responses={200: '', 400: '데이터 형식 확인'}, operation_description=change_password_operation_description)
@api_view(['PATCH'])
@permission_classes([IsAuthenticatedNonAdminUser])
def change_password(request):
    serializer = PasswordChangeSerializer(request.user, data=request.data)
    serializer.is_valid(raise_exception=True)

    new_password = serializer.validated_data['new_password']
    request.user.set_password(new_password)
    request.user.save()
    update_session_auth_hash(request, request.user)

    return Response()


class UserViewSet(GenericViewSet):
    __normal_user_patchable_fields = ('name', 'email')
    lookup_value_regex = r'[0-9]+'
    queryset = User.objects.all().order_by('user_type', 'username')
    serializer_class = UserSerializer
    permission_classes = [UserAccessPermission]

    def __get_user(self):
        if self.request.user.is_admin():
            return self.get_object()
        return self.request.user

    def __validate_data_contains_non_patchable_fields(self):
        if not self.request.user.is_admin():
            return set(self.request.data).difference(self.__normal_user_patchable_fields)
        return False

    @swagger_auto_schema(responses={200: UserResponse, 404: not_found_response}, operation_description='id에 해당하는 유저 정보 조회')
    def retrieve(self, request, pk):
        user = self.__get_user()
        serializer = self.get_serializer(user)
        return Response(serializer.data)
    
    @swagger_auto_schema(responses={200: UserListResponse}, operation_description='모든 user 정보 조회')
    def list(self, request):
        queryset = self.get_queryset()
        if 'username' in request.query_params:
            queryset = queryset.filter(username=request.query_params['username'])

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(request_body=UserSerializer, responses={201: '', 400: '데이터 형식 확인'}, operation_description=user_create_operation_description)
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(status=HTTP_201_CREATED, headers={'Location': user.id})
    
    @swagger_auto_schema(request_body=UserSerializer, responses={201: '', 400: '데이터 형식 확인', 404: not_found_response},
                         operation_description=user_partial_update_operation_description)
    def partial_update(self, request, pk):
        if self.__validate_data_contains_non_patchable_fields():
            return Response('The data contains fields cannot be updated.', status=HTTP_400_BAD_REQUEST)
        user = self.__get_user()

        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response()
    
    @swagger_auto_schema(responses={200: '', 404: not_found_response}, operation_description='id에 해당하는 유저 삭제')
    def destroy(self, request, pk):
        user = self.__get_user()
        user.delete()
        return Response()
