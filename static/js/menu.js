let cart = [];

fetch("/menu")
  .then(res => res.json())
  .then(data => {
    let html = "";
    data.menu.forEach(item => {
      html += `
        <div class="menu-card">
          <img src="/static/images/default_food.jpg">
          <h4>${item.name}</h4>
          <p>⭐ 4.5 • 20 min</p>
          <div class="price">₹${item.price}</div>
          <button onclick="addToCart(${item.item_id})">Add</button>
        </div>
      `;
    });
    document.getElementById("menu").innerHTML = html;
  });

function addToCart(id) {
  cart.push({ item_id: id, quantity: 1 });
  alert("Added to cart");
}

function placeOrder() {
  fetch("/order", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      table_number: TABLE_NO,
      items: cart
    })
  })
  .then(res => res.json())
  .then(data => {
    alert("Order placed! Order ID: " + data.order_id);
  });
}
