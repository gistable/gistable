## views.py

import tempfile
import os
import commands
import cgi

from django import http
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.conf import settings

from joldit.apps.payments.models import Order


SUCCESS_RESPONSE = 'ACEPTADO'
FAILURE_RESPONSE = 'RECHAZADO'
VALID_MAC_RESPONSE = 'CORRECTO'


@csrf_exempt
def success(request):
  return render(request, 'payments/success.html')


def fail(request):
  return render(request, 'payments/fail.html')


@require_POST
@csrf_exempt
def callback(request):
  transaction_code = request.POST.get('TBK_RESPUESTA')
  unique_id = request.POST.get('TBK_ORDEN_COMPRA')
  amount = int(request.POST.get('TBK_MONTO')) / 100
  authorization_code = request.POST.get('TBK_CODIGO_AUTORIZACION')
  transaction_id = request.POST.get('TBK_ID_TRANSACCION')
  last_4_digits = request.POST.get('TBK_FINAL_NUMERO_TARJETA')

  success = False
  qs = _get_qs(request)

  order_obj = Order.objects.get(unique_id=unique_id)
  order_obj.transaction_code = transaction_code
  order_obj.gateway_response = qs
  order_obj.transaction_id = transaction_id
  order_obj.last_4_digits = last_4_digits

  if transaction_code == '0' and _valid_mac(qs) == VALID_MAC_RESPONSE:
    if order_obj.amount == amount and not order_obj.authorization_code:
      order_obj.authorization_code = authorization_code
      order_obj.status = order_obj.PAID
      success = True
    else:
      order_obj.status = order_obj.INVALID_AMOUNT
  else:
    order_obj.status = order_obj.INVALID

  order_obj.save()

  if success:
    order_obj.notify_reservation()
    return http.HttpResponse(SUCCESS_RESPONSE)
  return http.HttpResponse(FAILURE_RESPONSE)


def _get_qs(request):
  return '&'.join(['%s=%s' % (k,v) for k,v in cgi.parse_qsl(request.body)])


def _valid_mac(qs):
  descriptor, temp_path = tempfile.mkstemp()
  f = os.fdopen(descriptor, 'w')
  f.write(qs)
  f.close()
  command = '%(mac)s %(temp_path)s' % {
    'mac': settings.WEBPAY_MAC_CGI,
    'temp_path': temp_path
  }
  valid_mac = commands.getoutput(command).strip() == VALID_MAC_RESPONSE
  os.remove(temp_path)
  return VALID_MAC_RESPONSE if valid_mac else FAILURE_RESPONSE


## models.py

from django.db import models
from django.utils.translation import ugettext_lazy as _

from joldit.apps.spaces.models import Reservation


TRANSACTION_CODES = {
  '0': _('Transaction approved.'),
  '-1': _('Transaction denied.'),
  '-2': _('Transaction must retry.'),
  '-3': _('Error in transaction.'),
  '-4': _('Transaction denied.'),
  '-5': _('Denied by error in rate.'),
  '-6': _('Exceeds monthly limit.'),
  '-7': _('Exceeds daily limit by transaction.'),
  '-8': _('Not authorized.')
}


class Order(models.Model):
  WEBPAY = 'webpay'
  TRANSFER = 'transfer'
  SOURCES = (
    (WEBPAY, _('Webpay Chile')),
    (TRANSFER, _('Transfer'))
  )
  PENDING, PAID, CANCELED, INVALID, INVALID_AMOUNT = range(5)
  STATUSES = (
    (PENDING, _('Pending')),
    (PAID, _('Paid')),
    (CANCELED, _('Canceled')),
    (INVALID, _('Invalid')),
    (INVALID_AMOUNT, _('Invalid Amount'))
  )

  reservation = models.ForeignKey(Reservation)
  unique_id = models.CharField(max_length=42, unique=True)
  status = models.PositiveSmallIntegerField(choices=STATUSES, default=PENDING)
  source = models.CharField(max_length=10, choices=SOURCES, blank=True)
  amount = models.PositiveIntegerField(default=0)
  transaction_code = models.IntegerField(default=0)
  authorization_code = models.CharField(max_length=80, blank=True)
  last_4_digits = models.CharField(max_length=4, blank=True)
  transaction_id  = models.CharField(max_length=80, blank=True)
  received_at = models.DateTimeField()
  created_at = models.DateTimeField(auto_now_add=True)
  gateway_response = models.TextField()

  class Meta:
    db_table = 'orders'

  def __unicode__(self):
    return '%s:%s' % (self.unique_id, self.get_status_display())

  def get_receipt_number(self):
    return '%06d' % self.id

  def get_transaction_message(self):
    return TRANSACTION_CODES.get(self.transaction_code)

  def notify_reservation(self):
    """Notifies the reservation about this order being paid."""
    reservation = self.reservation
    if self.amount >= reservation.total:
      reservation.change_and_log(reservation.from_user, Reservation.PAID,
                                 'Paid by order_unique_id %s' % self.unique_id)