from django.db import models
from service.models.appointment import Appointment
import uuid
from django.utils import timezone
from django.conf import settings
import urllib.parse


class Payment(models.Model):
    class PaymentMethod(models.TextChoices):
        CASH = "cash", "Cash"
        BANK_TRANSFER = "bank_transfer", "Bank Transfer"
        MOMO = "momo", "MoMo"
        ZALO_PAY = "zalo_pay", "ZaloPay"
        VNPAY = "vn_pay", "VNPay"
        OTHER = "other", "Other"

    class PaymentStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"
        CANCELED = "canceled", "Canceled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    invoice_id = models.CharField(max_length=15, unique=True, blank=True, null=True)

    appointment = models.OneToOneField(
        Appointment, on_delete=models.CASCADE, related_name="payment"
    )

    method = models.CharField(
        max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.CASH
    )

    status = models.CharField(
        max_length=10, choices=PaymentStatus.choices, default=PaymentStatus.PENDING
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    transaction_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )

    qr_code_url = models.TextField(null=True, blank=True)

    paid_at = models.DateTimeField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)

    create_at = models.DateTimeField(default=timezone.now)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment for Appointment {self.appointment.id} - {self.status}"

    @staticmethod
    def generate_invoice_id():
        last_payment = Payment.objects.all().order_by("create_at").last()
        if last_payment:
            last_number = int(last_payment.invoice_id[3:])
            new_number = last_number + 1
        else:
            new_number = 1

        return f"PAG{new_number:06}"

    def save(self, *args, **kwargs):
        if not self.invoice_id:
            self.invoice_id = Payment.generate_invoice_id()

        if not self.qr_code_url:
            bank_id = getattr(settings, "BANK_ID", "VCB")
            account_no = getattr(settings, "ACCOUNT_NO", "0123456789")
            account_name = getattr(settings, "ACCOUNT_NAME", "Prestige Garage")

            encoded_name = urllib.parse.quote(account_name)
            base_url = f"https://img.vietqr.io/image/{bank_id}-{account_no}-basic.png"
            params = f"?amount={int(self.amount)}&addInfo={self.invoice_id}&accountName={encoded_name}"
            self.qr_code_url = base_url + params

        super().save(*args, **kwargs)

    def get_create_at(self):
        if self.create_at:
            localized_time = timezone.localtime(self.create_at)
            return localized_time
        return None

    def get_update_at(self):
        if self.update_at:
            localized_time = timezone.localtime(self.update_at)
            return localized_time
        return None

    class Meta:
        db_table = "payment"
