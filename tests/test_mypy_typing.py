from typing import Literal

# type definition
Status = Literal["open", "closed", "pending"]

def update_order(order_id: int, new_status: Status):
    print(f"Order {order_id} is now {new_status}")

# OK: This matches the Literal
update_order(101, "open")

# FAIL: Mypy will catch this because "shipped" is not in our Status list
update_order(102, "shipped")