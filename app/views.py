from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from app.serializers import *


@api_view(['GET', 'PUT', 'DELETE'])
def queue(request, code):
    if request.method == 'GET':
        current_queue = Queue.objects.filter(code=code)
        if current_queue.exists():
            members = current_queue[0].members
            serializer = MemberSerializer(members, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)

    elif request.method == 'PUT':
        if request.user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        current_queue = Queue.objects.filter(code=code)
        if current_queue.exists():
            member = Member.objects.filter(user_id=request.user.id, queue_id=current_queue[0].id)
            if member.exists():
                serializer = MemberSerializer(instance=member[0], data=request.data, many=False)
                if serializer.is_valid():
                    serializer.save()
                    return Response(status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            serializer = MemberSerializer(data=request.data, context={'user': request.user, 'queue': current_queue[0]})
            if serializer.is_valid():
                serializer.save()
                current_queue = Queue.objects.get(id=current_queue[0].id)
                current_queue.quantity += 1
                current_queue.save()
                return Response(status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(status=status.HTTP_404_NOT_FOUND)

    elif request.method == 'DELETE':
        if request.user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        current_queue = Queue.objects.filter(code=code)
        if current_queue.exists():
            if current_queue[0].owner_id == request.user.id:
                current_queue[0].delete()
                return Response(status=status.HTTP_200_OK)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def queue_info(request, code):
    queue_data = Queue.objects.filter(code=code)
    if queue_data.exists():
        serializer = QueueSerializer(queue_data[0])
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
def queue_remove(request, code):
    if request.user.is_anonymous:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    current_queue = Queue.objects.filter(code=code)
    if current_queue.exists():
        if request.data.get('by_id') and current_queue[0].owner_id == request.user.id:
            member = Member.objects.get(queue_id=current_queue[0].id, user_id=request.data.get('id'))
            if member.active:
                member.active = False
                member.save()
        else:
            member = Member.objects.get(queue_id=current_queue[0].id, user_id=request.user.id)
            if member.active:
                member.active = False
                member.save()
        return Response(status=status.HTTP_200_OK)
    return Response(status=status.HTTP_404_NOT_FOUND)


class QueueAPIView(APIView):
    @classmethod
    def get(cls, request):
        if request.user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        queues = request.user.queues
        serializer = QueueSerializer(queues, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @classmethod
    def post(cls, request):
        if request.user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        serializer = QueueSerializer(data=request.data, context={'owner': request.user})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserAPIView(APIView):
    @classmethod
    def get(cls, request):
        if request.user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        user = UserSerializer(request.user)
        return Response(user.data, status=status.HTTP_200_OK)

    @classmethod
    def post(cls, request):
        if not request.data.get('username') or not request.data.get('password') or not request.data.get('first_name'):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if len(request.data.get('username')) < 4 or User.objects.filter(username=request.data.get('username')).exists():
            return Response({"username": "exists or length less than 4"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=request.data.get('username'), password=request.data.get('password'))
        user.first_name = request.data.get('first_name')
        user.last_name = request.data.get('last_name')
        user.save()
        return Response(status=status.HTTP_201_CREATED)
