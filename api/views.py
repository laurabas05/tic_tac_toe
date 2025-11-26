from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime
from .serializer import StatusSerializer, ErrorSerializer
from .models import ErrorReport
from rest_framework import status

# Create your views here.
@api_view(['GET'])
def get_server_status(request):
    return Response(StatusSerializer(
        {'status': 'running', 'date': datetime.now()}
    ).data)

@api_view(['GET'])
def get_errors(request):
    errors = ErrorReport.objects.all()
    serialized_error = ErrorSerializer(errors, many=True)
    return Response(serialized_error.data)

@api_view(['GET'])
def get_error_from_code(request, code):
    error = ErrorReport.objects.get(code=code)
    serialized_error = ErrorSerializer(error)
    return Response(serialized_error.data)

@api_view(['POST'])
def create_error(request):
    serialized_error = ErrorSerializer(data=request.data)
    if serialized_error.is_valid():
        serialized_error.save()
        return Response(serialized_error.data, status=status.HTTP_201_CREATED)
    return Response(serialized_error.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT', 'DELETE'])
def object_update(request, id):
    try:
        object = ErrorReport.objects.get(id=id)
    except ErrorReport.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'PUT':
        serialized_error = ErrorSerializer(object, data=request.data)
        if serialized_error.is_valid():
            serialized_error.save()
            return Response(serialized_error.data)
        return Response(serialized_error.errors, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'DELETE':
        object.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)