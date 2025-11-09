from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Reward
from .serializers import RewardSerializer

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_reward_balance(request):
    if request.user.user_type != 'customer':
        return Response({'error': 'Only customers have reward balances.'}, status=status.HTTP_403_FORBIDDEN)
    
    reward, created = Reward.objects.get_or_create(customer=request.user)
    serializer = RewardSerializer(reward)
    return Response(serializer.data)