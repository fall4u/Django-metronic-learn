# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import generics, mixins, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import UploadedImage
from .serialize import UploadedImageSerializer


# Create your views here.



class uploadimages(generics.CreateAPIView):
	# Get /Update /Delete a libbook
	queryset = UploadedImage.objects.all()
	serializer_class = UploadedImageSerializer


class imageList(mixins.ListModelMixin,
				mixins.DestroyModelMixin,
				generics.GenericAPIView):
	queryset = UploadedImage.objects.all()
	serializer_class  = UploadedImageSerializer

	def get_queryset(self):
		isbn = self.kwargs['isbn']
		return UploadedImage.objects.filter(isbn=isbn)

	def destroy(self, request, *args, **kwargs):
		print "+++destroy +++"
		qs = self.get_queryset()
		pk = request.data['pk']
		instance = qs.filter(pk=pk)
		self.perform_destroy(instance)
		return Response(status=status.HTTP_204_NO_CONTENT)

	def get(self, request, *args, **kwargs):
		#isbn = kwargs.pop('isbn')
		qs = self.get_queryset()
		serializer = self.get_serializer(qs, many=True)
		return Response(serializer.data)


	def delete(self, request, *args, **kwargs):
		return self.destroy(request, *args, **kwargs)



@api_view(['POST'])
def imagesMoveUp(request):
	pk = request.POST['pk']
	isbn = request.POST['isbn']
	image = UploadedImage.objects.get(pk=pk)

	if image:
		image.up(isbn)
		return Response({"code": 0, "msg": "OK", "data": []}, status=status.HTTP_200_OK)
	else:
		return Response({"code": 400, "msg": "Pic not found", "data": []}, status=status.HTTP_400_BAD_REQUEST)

	return Response({"code": 400, "msg": "fail", "data": []}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def imagesMoveDown(request):
	pk = request.POST['pk']
	isbn = request.POST['isbn']
	image = UploadedImage.objects.get(pk=pk)
	if image:
		image.down(isbn)
		return Response({"code": 0, "msg": "OK", "data": []}, status=status.HTTP_200_OK)
	else:
		return Response({"code": 400, "msg": "Pic not found", "data": []}, status=status.HTTP_400_BAD_REQUEST)

	return Response({"code": 400, "msg": "fail", "data": []}, status=status.HTTP_400_BAD_REQUEST)

