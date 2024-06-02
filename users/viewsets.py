from django.contrib.auth import logout, get_user_model,login
from rest_framework.viewsets import ModelViewSet
from .serializers import UserSerializer,FriendRequestSerializer
from .models import MyUser,FriendRequest
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, JSONParser
from base.api.pagination import StandardResultsSetPagination
from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import UserRateThrottle

# from .permissions import UserPermissions

class UserViewSet(ModelViewSet):
    """
    API to search other users by email and name(paginate up to 10 records per page).
    """
    queryset  = MyUser.objects.all()
    # permission_classes = UserPermissions
    permission_classes = [IsAuthenticated,]
    serializer_class = UserSerializer
    parser_classes = (JSONParser, MultiPartParser)
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        obj = self.request.query_params.get('search', None)
        queryset = MyUser.objects.all()
        if obj is not None:
            queryset = queryset.filter(Q(name__icontains=obj) | Q(email__icontains=obj))
        return queryset
    
class FriendRequestViewSet(ModelViewSet):
    """
    handle friend request.
    """
    queryset  = FriendRequest.objects.all()
    # permission_classes = UserPermissions
    permission_classes = [IsAuthenticated,]
    serializer_class = FriendRequestSerializer
    parser_classes = (JSONParser, MultiPartParser)
    pagination_class = StandardResultsSetPagination
    
    def get_throttles(self):
        if self.action == 'create':
            throttle_classes = [UserRateThrottle]
        else:
            throttle_classes = []  # No throttle for other actions
        return [throttle() for throttle in throttle_classes]
    
    def get_queryset(self):
        return FriendRequest.objects.filter(to_user=self.request.user)

    def create(self, request, *args, **kwargs):
        '''API to send friend request'''
        from_user = request.user
        if 'to_user' not in request.data:
            return Response({"error": "Please select user to make Friend"}, status=status.HTTP_400_BAD_REQUEST)
        to_user_id = request.data.get('to_user')
        if from_user.id == to_user_id:
            return Response({"error": "You cannot send a friend request to yourself."}, status=status.HTTP_400_BAD_REQUEST)

        if FriendRequest.objects.filter(from_user=from_user, to_user_id=to_user_id).exists():
            return Response({"error": "Friend request already sent."}, status=status.HTTP_400_BAD_REQUEST)

        friend_request = FriendRequest(from_user=from_user, to_user_id=to_user_id)
        friend_request.save()
        return Response({"status": "Friend request sent."}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        '''API to accept friend request'''
        try:
            friend_request = self.get_object()
            if friend_request.to_user != request.user:
                return Response({"error": "You cannot accept this friend request."}, status=status.HTTP_403_FORBIDDEN)
            friend_request.is_accepted = True
            friend_request.save()
            return Response({"status": "Friend request accepted."}, status=status.HTTP_200_OK)
        except FriendRequest.DoesNotExist:
            return Response({"error": "Friend request not found."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        '''API to reject friend request'''
        try:
            friend_request = self.get_object()
            if friend_request.to_user != request.user:
                return Response({"error": "You cannot reject this friend request."}, status=status.HTTP_403_FORBIDDEN)
            friend_request.delete()
            return Response({"status": "Friend request rejected."}, status=status.HTTP_200_OK)
        except FriendRequest.DoesNotExist:
            return Response({"error": "Friend request not found."}, status=status.HTTP_404_NOT_FOUND)
        
    @action(detail=False, methods=['get'])
    def friendlist(self, request, pk=None):
        '''API to list friends(list of users who have accepted friend request)'''
        obj=FriendRequest.objects.filter(from_user=self.request.user.id,is_accepted=True)
        return Response(FriendRequestSerializer(obj,many=True).data)
    
    @action(detail=False, methods=['get'])
    def friendrequestpending(self, request, pk=None):
        '''List pending friend requests(received friend request)'''
        obj=FriendRequest.objects.filter(to_user=self.request.user,is_accepted=False)
        return Response(FriendRequestSerializer(obj,many=True).data)