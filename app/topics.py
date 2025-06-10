from enum import Enum

class Topic(Enum):
    DELIVERY_ORDER = "delivery.order"


class MessageType(Enum):
    GENERATE_DELIVERY_ORDERS = "generate_delivery_orders"