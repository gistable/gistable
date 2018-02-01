"""views_push.py: Views for push notifications, to register a device that would like to get push notifications."""

__author__ = "Alex 'Chozabu' P-B"
__copyright__ = "Copyright 2016, IAgree"

from push_notifications.api import rest_framework

from dj_represent import settings

from rest_framework.response import Response
from rest_framework import status

from push_notifications.models import GCMDevice, APNSDevice


class APNSDeviceAuthorizedViewSet(rest_framework.APNSDeviceAuthorizedViewSet):

	def create(self, request, *args, **kwargs):
		serializer = None
		if settings.DPN_auto_update_matching_reg_id:
			instance = APNSDevice.objects.filter(registration_id=request.data['registration_id']).first()
			if instance:
				serializer = self.get_serializer(instance, data=request.data)
		if not serializer:
			serializer = self.get_serializer(data=request.data)

		serializer.is_valid(raise_exception=True)
		self.perform_create(serializer)
		headers = self.get_success_headers(serializer.data)
		return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class GCMDeviceAuthorizedViewSet(rest_framework.GCMDeviceAuthorizedViewSet):

	def create(self, request, *args, **kwargs):
		serializer = None
		if settings.DPN_auto_update_matching_reg_id:
			instance = GCMDevice.objects.filter(registration_id=request.data['registration_id']).first()
			if instance:
				serializer = self.get_serializer(instance, data=request.data)
		if not serializer:
			serializer = self.get_serializer(data=request.data)

		serializer.is_valid(raise_exception=True)
		self.perform_create(serializer)
		headers = self.get_success_headers(serializer.data)
		return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
