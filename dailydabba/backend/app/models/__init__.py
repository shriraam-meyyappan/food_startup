"""Import all mappings so Base.metadata includes the complete Phase 3 design."""

from app.models.catalog import DailyMenu, FoodCategory, FoodItem, MenuItem
from app.models.commerce import Cart, CartItem, DeliverySlot, Order, OrderItem
from app.models.identity import Address, CustomerProfile, User
from app.models.operations import AuditLog, KitchenOrder, Notification
from app.models.payments import Payment, PaymentWebhookEvent, Refund
from app.models.subscriptions import (
    CreditAccount,
    CreditTransaction,
    Subscription,
    SubscriptionEvent,
    SubscriptionPlan,
)

__all__ = [
    "Address",
    "AuditLog",
    "Cart",
    "CartItem",
    "CreditAccount",
    "CreditTransaction",
    "CustomerProfile",
    "DailyMenu",
    "DeliverySlot",
    "FoodCategory",
    "FoodItem",
    "KitchenOrder",
    "MenuItem",
    "Notification",
    "Order",
    "OrderItem",
    "Payment",
    "PaymentWebhookEvent",
    "Refund",
    "Subscription",
    "SubscriptionEvent",
    "SubscriptionPlan",
    "User",
]
