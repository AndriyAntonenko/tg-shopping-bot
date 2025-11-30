import stripe
from ..config import settings

stripe.api_key = settings.stripe_api_key

class PaymentService:
    async def create_checkout_session(
        self, order_id: int, product_name: str, price: float, currency: str
    ) -> tuple[str, str]:
        """
        Creates a Stripe Checkout Session.
        Returns (session_id, payment_url).
        """
        # Stripe expects amount in cents for most currencies
        unit_amount = int(price * 100)

        success_url = f"https://t.me/{settings.bot_name}?start=order_{order_id}"
        cancel_url = f"https://t.me/{settings.bot_name}?start=order_{order_id}"
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": currency,
                        "product_data": {
                            "name": product_name,
                        },
                        "unit_amount": unit_amount,
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "order_id": str(order_id),
            },
        )
        return session.id, session.url

    async def check_payment_status(self, session_id: str) -> str:
        """
        Checks the status of a Stripe Checkout Session.
        Returns the payment status (e.g., 'paid', 'unpaid').
        """
        session = stripe.checkout.Session.retrieve(session_id)
        return session.payment_status
