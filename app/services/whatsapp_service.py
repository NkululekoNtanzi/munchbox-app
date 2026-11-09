import urllib.parse

def generate_whatsapp_order_link(order, items):
    phone_number = "27678833868"  # Replace with actual business WhatsApp number
    message = f"Hello! New MunchBox Order #{order.id}\nName: {order.customer_name}\nAddress: {order.address}, {order.area}\nTotal: R{order.total:.2f}"
    encoded_message = urllib.parse.quote(message)
    return f"https://wa.me/{phone_number}?text={encoded_message}"