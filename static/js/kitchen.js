function updateStatus(orderId, status) {
  fetch("/kitchen/order/update", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded"
    },
    body: `order_id=${orderId}&status=${status}`
  });
}
