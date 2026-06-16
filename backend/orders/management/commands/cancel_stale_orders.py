from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from orders.models import Order, Payment
from orders.services import cancel_stale_razorpay_order


class Command(BaseCommand):
    help = "Cancel unpaid Razorpay orders older than 60 minutes and restore stock."

    def add_arguments(self, parser):
        parser.add_argument("--minutes", type=int, default=60)

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(minutes=options["minutes"])
        stale = Order.objects.filter(
            status=Order.Status.PENDING,
            payment__payment_method=Payment.Method.RAZORPAY,
            payment__status=Payment.Status.PENDING,
            order_date__lt=cutoff,
        )
        count = 0
        for order in stale:
            if cancel_stale_razorpay_order(order):
                count += 1
        self.stdout.write(self.style.SUCCESS(f"Cancelled {count} stale Razorpay order(s)."))
