from django.core.management.base import BaseCommand
from django.utils import timezone
from orders.models import Order, OrderTracking


STATUS_FLOW = [
    Order.Status.CONFIRMED,
    Order.Status.PROCESSING,
    Order.Status.SHIPPED,
    Order.Status.OUT_FOR_DELIVERY,
    Order.Status.DELIVERED,
]

MESSAGES = {
    Order.Status.CONFIRMED: "Order confirmed by seller",
    Order.Status.PROCESSING: "Order is being packed",
    Order.Status.SHIPPED: "Order shipped from warehouse",
    Order.Status.OUT_FOR_DELIVERY: "Out for delivery in your area",
    Order.Status.DELIVERED: "Order delivered successfully",
}


class Command(BaseCommand):
    help = "Advance order to next tracking status (demo for viva)"

    def add_arguments(self, parser):
        parser.add_argument("order_id", type=int)

    def handle(self, *args, **options):
        order = Order.objects.get(pk=options["order_id"])
        current = order.status
        try:
            idx = STATUS_FLOW.index(current) if current in STATUS_FLOW else -1
            next_status = STATUS_FLOW[idx + 1]
        except (ValueError, IndexError):
            if current == Order.Status.PENDING:
                next_status = Order.Status.CONFIRMED
            else:
                self.stdout.write(self.style.WARNING(f"Order #{order.id} already at {current}"))
                return

        order.status = next_status
        order.save(update_fields=["status", "updated_at"])
        OrderTracking.objects.create(
            order=order,
            status=next_status,
            message=MESSAGES.get(next_status, f"Status: {next_status}"),
            location="Warehouse Hub",
        )
        self.stdout.write(self.style.SUCCESS(f"Order #{order.id} → {next_status}"))
