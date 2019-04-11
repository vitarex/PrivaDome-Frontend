""" API endpoint views. """
import pdb

import datetime

import procbridge
import json

from rest_framework import permissions, viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.reverse import reverse
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.exceptions import PermissionDenied, server_error
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

from django.contrib.auth.models import User
from django.conf import settings

from .serializers import UserListSerializer,\
                         UserCreateSerializer,\
                         UserUpdateSerializer

from .permissions import IsAdminOrSelf

PROC_HOST = settings.PRIVADOME_CORE_HOST
PROC_PORT_POLICY = 8077
PROC_PORT_DATA = 8090


# Create your views here.
@api_view(['GET'])
def api_root(request, format=None):
    """ API root endpoint. """
    return Response({
        'users': reverse('user-list', request=request, format=format),
    })

@api_view(['GET'])
def api_procbridge_test(request, format=None):
    """ Procbridge test. """
    response = generic_procbridge_request('read_state')
    return response

class ObtainExpiringAuthToken(ObtainAuthToken):
    """
    Expiring token obtain.
    """
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)

            utc_now = datetime.datetime.utcnow()
            if not created and token.created < utc_now - datetime.timedelta(hours=1):
                token.delete()
                token = Token.objects.create(user=user)
                token.created = datetime.datetime.utcnow()
                token.save()

            #return Response({'token': token.key})
            return Response({'token': token.key})


class UserViewSet(mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    """
    User endpoint.
    This viewset provides User with `list`, `create`,
    `update` and `destroy` actions.
    """

    queryset = User.objects.all()
    permission_classes = (permissions.IsAuthenticated, IsAdminOrSelf)
    serializer_class = UserListSerializer

    def list(self, request, *args, **kwargs):
        if request.user and request.user.is_superuser:
            queryset = User.objects.all()
        else:
            queryset = User.objects.filter(username=request.user.username)

        serializer = UserListSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        if not (request.user and request.user.is_superuser):
            raise PermissionDenied("You do not have permission"
                                   " to create new users")

        create_serializer = UserCreateSerializer(data=request.data)
        create_serializer.is_valid(raise_exception=True)

        instance = create_serializer.save()

        read_serializer = UserListSerializer(instance)

        return Response(read_serializer.data, status=status.HTTP_201_CREATED)

    #def update(self, request, pk=None, *args, **kwargs):
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        update_serializer = UserUpdateSerializer(instance, data=request.data,
                                                 partial=partial)
        update_serializer.is_valid(raise_exception=True)

        new_instance = update_serializer.save()

        if getattr(new_instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            new_instance._prefetched_objects_cache = {}

        read_serializer = UserListSerializer(new_instance)

        return Response(read_serializer.data)

@api_view(['POST'])
@parser_classes((JSONParser,))
@permission_classes((permissions.IsAuthenticated,))
def tiles_data(request):
    """
    Get data for a specific tile
    """
    try:
        if 'name' in request.data:
            response = generic_procbridge_request(request.data['name'], None, PROC_PORT_DATA)
        else:
            raise ProcessLookupError("Invalid request")
    except Exception as e:
        print(e)
        return server_error(request)
    return response

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def module_config(request):
    """
    Get the current module configurations
    """
    try:
        response = generic_procbridge_request('read_state')
    except:
        return server_error(request)
    return response

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def module_schema(request):
    """
    Get the schema information of modules
    """
    try:
        response = generic_procbridge_request('get_module_configs')
    except:
        return server_error(request)
    return response

@api_view(['POST'])
@parser_classes((JSONParser,))
@permission_classes((permissions.IsAuthenticated,))
def add_policy_group(request):
    """
    Add a group policy level
    """
    try:
        response = generic_procbridge_request('add_group', request.body)
    except:
        return server_error(request)
    return response

@api_view(['POST'])
@parser_classes((JSONParser,))
@permission_classes((permissions.IsAuthenticated,))
def add_policy_address(request):
    """
    Add an address policy level
    """
    try:
        response = generic_procbridge_request('add_client', request.body)
    except:
        return server_error(request)
    return response

@api_view(['POST'])
@parser_classes((JSONParser,))
@permission_classes((permissions.IsAuthenticated,))
def delete_policy_group(request):
    """
    Delete a group policy level
    """
    try:
        response = generic_procbridge_request('delete_group', request.body)
    except:
        return server_error(request)
    return response

@api_view(['POST'])
@parser_classes((JSONParser,))
@permission_classes((permissions.IsAuthenticated,))
def delete_policy_address(request):
    """
    Delete an address policy level
    """
    try:
        response = generic_procbridge_request('delete_client', request.body)
    except:
        return server_error(request)
    return response

@api_view(['POST'])
@parser_classes((JSONParser,))
@permission_classes((permissions.IsAuthenticated,))
def update_policy_network(request):
    """
    Update the network policy level
    """
    try:
        response = generic_procbridge_request('update_network_policy', request.body)
    except Exception as e:
        print(e)
        return server_error(request)
    return response

@api_view(['POST'])
@parser_classes((JSONParser,))
@permission_classes((permissions.IsAuthenticated,))
def update_policy_group(request):
    """
    Update a group policy level
    """
    try:
        response = generic_procbridge_request('update_group_policy', request.body)
    except:
        return server_error(request)
    return response

@api_view(['POST'])
@parser_classes((JSONParser,))
@permission_classes((permissions.IsAuthenticated,))
def update_policy_address(request):
    """
    Update an address policy level
    """
    try:
        response = generic_procbridge_request('update_client_policy', request.body)
    except:
        return server_error(request)
    return response

def generic_procbridge_request(api_identifier, body=None, port=PROC_PORT_POLICY):
    """
    Generic request function to the procbridge server
    """
    try:
        client = procbridge.Client(PROC_HOST, port)
        if body is None:
            response = client.request(api_identifier)
        else:
            response = client.request(api_identifier, json.loads(body))
    except:
        raise LookupError('Error')
    return Response(response, status=status.HTTP_200_OK)
