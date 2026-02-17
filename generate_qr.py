import qrcode

for table_no in range(1, 6):
    url = f"http://192.168.0.108:5000/menu/{table_no}"
    img = qrcode.make(url)
    img.save(f"table_{table_no}.png")
