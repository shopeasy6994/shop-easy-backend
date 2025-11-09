from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import ItemRequest
from .serializers import ItemRequestSerializer

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def submit_item_request(request):
    if request.user.user_type != 'customer':
        return Response({'error': 'Only customers can submit requests.'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = ItemRequestSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(customer=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)