import os
import shutil
from fastapi import FastAPI, Request, Depends, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from urllib.parse import quote

from app.database import engine, get_db
from app import models, schemas
from app.services.pdf_service import generate_quotation_pdf
from app.services.chatbot_service import process_aunty_bree_bot

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="The MunchBox by Aunty Bree's", version="3.0.0")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/")
def read_root(request: Request, db: Session = Depends(get_db)):
    products = db.query(models.Product).all()
    return templates.TemplateResponse(request, "index.html", {"products": products})

@app.get("/specials")
def read_specials(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(request, "specials.html", {})

@app.get("/admin")
def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    orders = db.query(models.Order).order_by(models.Order.created_at.desc()).all()
    return templates.TemplateResponse(request, "admin.html", {"orders": orders})

@app.post("/api/orders")
def create_order(order_data: schemas.OrderCreate, db: Session = Depends(get_db)):
    total_amount = sum(item.price * item.qty for item in order_data.items)

    db_order = models.Order(
        customer_name=order_data.full_name,
        phone=order_data.phone_number,
        area=order_data.delivery_area,
        address=order_data.street_address,
        event_type=order_data.event_type,
        pickup_date=order_data.pickup_date,
        pickup_time=order_data.pickup_time,
        total=total_amount
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    for item in order_data.items:
        db_item = models.OrderItem(
            order_id=db_order.id,
            product_id=item.product_id,
            quantity=item.qty,
            unit_price=item.price
        )
        db.add(db_item)
    db.commit()

    # Generate PDF Quotation
    pdf_path = generate_quotation_pdf(
        order_id=db_order.id,
        customer_name=db_order.customer_name,
        phone=db_order.phone,
        event_type=db_order.event_type,
        items=order_data.items,
        total=total_amount
    )

    items_summary = "\n".join([f"- {item.qty}x {item.name} (R{item.price:.2f})" for item in order_data.items])
    
    whatsapp_message = (
        f"🍔 *NEW ORDER QUOTATION #{db_order.id} - THE MUNCHBOX* 📦\n\n"
        f"🎉 *Event:* {db_order.event_type}\n"
        f"👤 *Customer:* {db_order.customer_name}\n"
        f"📞 *Phone:* {db_order.phone}\n"
        f"📅 *Pickup Date/Time:* {db_order.pickup_date} at {db_order.pickup_time}\n"
        f"📍 *Pickup Address:* 19 Eastwood Road, Rosebank\n\n"
        f"*Order Items:*\n{items_summary}\n\n"
        f"💰 *Total Amount:* R{total_amount:.2f}\n\n"
        f"🏦 *Deposit Banking Details:*\n"
        f"• Bank: Capitec\n"
        f"• Holder: Doone B Johns\n"
        f"• Acc: 160 351 9228\n\n"
        f"Please upload your proof of payment on the website to secure your order!"
    )

    encoded_message = quote(whatsapp_message)
    whatsapp_url = f"https://wa.me/27680162552?text={encoded_message}"

    return {
        "status": "success",
        "order_id": db_order.id,
        "whatsapp_url": whatsapp_url,
        "pdf_url": f"/{pdf_path}"
    }

@app.post("/api/orders/{order_id}/deposit")
async def upload_deposit_proof(order_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    os.makedirs("app/static/deposits", exist_ok=True)
    file_path = f"app/static/deposits/order_{order_id}_{file.filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    order.deposit_proof_path = f"/{file_path}"
    order.status = "Deposit Uploaded (Verifying)"
    db.commit()
    
    return {"status": "success", "message": "Deposit proof uploaded successfully!"}

@app.post("/api/admin/orders/{order_id}/notify")
def admin_notify_client(order_id: int, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    order.status = "Ready for Pickup / Confirmed"
    db.commit()
    
    notification_msg = (
        f"🎉 *ORDER READY - THE MUNCHBOX* 📦\n\n"
        f"Hello {order.customer_name}, your order #{order.id} is confirmed and ready for pickup!\n\n"
        f"📍 *Location:* 19 Eastwood Road, Rosebank, Gauteng, 2091\n"
        f"📅 *Pickup Schedule:* {order.pickup_date} at {order.pickup_time}\n"
        f"📞 *Inquiries:* 068 016 2552\n\n"
        f"Thank you for choosing Aunty Bree's MunchBox!"
    )
    
    encoded_msg = quote(notification_msg)
    client_whatsapp_url = f"https://wa.me/{order.phone}?text={encoded_msg}"
    
    return {"status": "success", "client_whatsapp_url": client_whatsapp_url}

@app.post("/api/whatsapp/webhook")
async def whatsapp_webhook(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    try:
        incoming_message = data["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"]
        sender_phone = data["entry"][0]["changes"][0]["value"]["messages"][0]["from"]
        
        reply_text = process_aunty_bree_bot(sender_phone, incoming_message, db)
        return {"status": "success", "reply": reply_text}
    except (KeyError, IndexError):
        return {"status": "ignored", "reason": "Not a valid text message payload"}