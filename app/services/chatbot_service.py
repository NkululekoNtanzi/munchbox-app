from sqlalchemy.orm import Session
from app import models

def process_aunty_bree_bot(sender_phone: str, message_body: str, db: Session) -> str:
    text = message_body.strip().lower()

    if "stock" in text or "menu" in text or "available" in text:
        products = db.query(models.Product).all()
        menu_str = "\n".join([f"• {p.name} ({p.category}): R{p.base_price:.2f}" for p in products])
        return (
            "👩‍🍳 *Aunty Bree's Kitchen Stock & Menu* 📦\n\n"
            f"{menu_str}\n\n"
            "Visit our website to place your order or book custom event platters!"
        )

    elif "history" in text or "my orders" in text:
        orders = db.query(models.Order).filter(models.Order.phone == sender_phone).all()
        if not orders:
            return "You have no past orders registered with this phone number."
        
        history_str = "\n".join([f"• Order #{o.id}: R{o.total:.2f} [{o.status}] on {o.created_at}" for o in orders[-3:]])
        return f"📋 *Your Recent MunchBox Orders:*\n\n{history_str}"

    elif "bank" in text or "deposit" in text or "account" in text:
        return (
            "🏦 *The MunchBox Banking Details*\n\n"
            "• **Account Holder:** Doone B Johns\n"
            "• **Bank:** Capitec Bank\n"
            "• **Account Number:** 160 351 9228\n\n"
            "Please send proof of payment to secure your booking!"
        )

    elif "event" in text or "party" in text or "booking" in text or "occas" in text:
        return (
            "🎉 *Planning an Event with Aunty Bree?*\n"
            "We cater for birthdays, weddings, festive gatherings, and corporate functions! "
            "Please specify your **Event Type, Guest Count, and Date** on our website checkout to receive your instant quotation and PDF invoice."
        )

    else:
        return (
            "👋 Welcome to **The MunchBox by Aunty Bree's**!\n"
            "I'm Aunty Bree, your virtual assistant. How can I help you today?\n\n"
            "• Type **Stock** to see available boxes.\n"
            "• Type **History** to check your order status.\n"
            "• Type **Banking** for our deposit account details.\n"
            "• Type **Event** for party and festive platters.\n\n"
            "📞 Contact: 068 016 2552 | 📍 Pickup: 19 Eastwood Road, Rosebank"
        )