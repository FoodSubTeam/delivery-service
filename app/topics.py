from enum import Enum

class Topic(Enum):
    KITCHEN_ORDER = "kitchen.order"


class MessageType(Enum):
    GENERATE_KITCHEN_ORDERS = "generate_kitchen_orders"