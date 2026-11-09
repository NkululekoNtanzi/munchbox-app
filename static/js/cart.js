document.addEventListener("DOMContentLoaded", () => {
    let cart = JSON.parse(localStorage.getItem("munchbox_cart")) || [];
    updateCartCount();

    // If on homepage, load menu
    const menuContainer = document.getElementById("menu-container");
    if (menuContainer) {
        fetch('/api/menu')
            .then(res => res.json())
            .then(products => {
                menuContainer.innerHTML = "";
                products.forEach(p => {
                    let variantOptions = "";
                    if (p.variants && p.variants.length > 0) {
                        variantOptions = `<div class="form-group"><label>Preparation:</label><select id="variant-${p.product_id}">` +
                            p.variants.map(v => `<option value="${v.preparation_type}">${v.preparation_type.replace('_', ' ')}</option>`).join("") +
                            `</select></div>`;
                    }

                    const card = document.createElement("div");
                    card.className = "product-card";
                    card.innerHTML = `
                        <div>
                            <h3>${p.name}</h3>
                            <p class="price">R${p.base_price.toFixed(2)}</p>
                            ${variantOptions}
                        </div>
                        <button class="btn-primary" onclick="addToCart(${p.product_id}, '${p.name}', ${p.base_price})">Add to Cart</button>
                    `;
                    menuContainer.appendChild(card);
                });
            });
    }

    // If on checkout page, render summary & handle submit
    const checkoutList = document.getElementById("checkout-items-list");
    if (checkoutList) {
        renderCheckoutSummary();

        const form = document.getElementById("order-form");
        form.addEventListener("submit", (e) => {
            e.preventDefault();
            const fullName = document.getElementById("full_name").value;
            const phone = document.getElementById("phone_number").value;
            const area = document.getElementById("delivery_area").value;
            const address = document.getElementById("street_address").value;
            const notes = document.getElementById("notes").value;
            const errorDiv = document.getElementById("error-message");

            if (area === "Other") {
                errorDiv.textContent = "Delivery is currently restricted to Rosebank and Randburg zones.";
                return;
            }

            const total = cart.reduce((sum, item) => sum + (item.price * item.qty), 0);

            const payload = {
                full_name: fullName,
                phone_number: phone,
                delivery_area: area,
                street_address: address,
                items: cart,
                notes: notes,
                total_amount: total
            };

            fetch('/api/orders', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            })
            .then(res => res.json().then(data => ({ status: res.status, body: data })))
            .then(response => {
                if (response.status === 200 && response.body.success) {
                    localStorage.removeItem("munchbox_cart");
                    window.location.href = response.body.whatsapp_url;
                } else {
                    errorDiv.textContent = response.body.detail || "Error processing order.";
                }
            })
            .catch(err => {
                errorDiv.textContent = "Network error. Please try again.";
            });
        });
    }
});

function addToCart(productId, name, price) {
    let cart = JSON.parse(localStorage.getItem("munchbox_cart")) || [];
    const variantSelect = document.getElementById(`variant-${productId}`);
    const prepType = variantSelect ? variantSelect.value : "READY_TO_EAT";

    const existing = cart.find(item => item.product_id === productId && item.preparation_type === prepType);
    if (existing) {
        existing.qty += 1;
    } else {
        cart.push({
            product_id: productId,
            name: name,
            preparation_type: prepType,
            qty: 1,
            price: price
        });
    }

    localStorage.setItem("munchbox_cart", JSON.stringify(cart));
    updateCartCount();
    alert(`${name} added to cart!`);
}

function updateCartCount() {
    let cart = JSON.parse(localStorage.getItem("munchbox_cart")) || [];
    const count = cart.reduce((sum, item) => sum + item.qty, 0);
    const badge = document.getElementById("cart-count");
    if (badge) badge.textContent = count;
}

function renderCheckoutSummary() {
    let cart = JSON.parse(localStorage.getItem("munchbox_cart")) || [];
    const container = document.getElementById("checkout-items-list");
    const totalPriceSpan = document.getElementById("checkout-total-price");

    if (cart.length === 0) {
        container.innerHTML = "<p>Your cart is empty.</p>";
        totalPriceSpan.textContent = "0.00";
        return;
    }

    let html = "";
    let total = 0;
    cart.forEach(item => {
        let itemTotal = item.price * item.qty;
        total += itemTotal;
        html += `<div style="display:flex; justify-content:space-between; margin-bottom:0.5rem;">
            <span>${item.qty}x ${item.name} [${item.preparation_type}]</span>
            <span>R${itemTotal.toFixed(2)}</span>
        </div>`;
    });
    container.innerHTML = html;
    totalPriceSpan.textContent = total.toFixed(2);
}