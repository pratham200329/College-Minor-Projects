# Inventory & Sales Management System

This is a complete **Inventory, Sales, and Purchase Management System** built using **PHP, MySQL, HTML, CSS, and JavaScript**.  
It allows you to manage products, customers, suppliers, purchase transactions, sales transactions, stock levels, and financial reports from a clean and responsive dashboard.

---

## 📌 Key Features

### 🔹 Dashboard (index.php)
- View all important business statistics
- Quick access navigation to all modules

### 📦 Product Management (products.php)
- Add new products with price & quantity
- Edit / Delete product records
- Automatic stock updates from sales/purchases

### 🧑‍🤝‍🧑 Customer Records (customers.php)
- Save customer names, contact numbers, and details
- Manage and update customer information

### 🚚 Supplier Records (suppliers.php)
- Store supplier business and contact information
- Connected to purchase records

### 🛍 Purchase Management (purchases.php)
- Record new stock purchases
- Add multiple products in one purchase invoice
- Stock increases automatically

### 🛒 Sales Management (sales.php)
- Create new sale transactions with dynamic total calculation
- Auto fetch product price using AJAX
- Stock decreases automatically

### 📑 Reports (reports.php)
- View and analyze sales and purchase history
- Track profit and remaining stock levels

---

## 📝 Database Structure

The system uses MySQL Database.  
Your provided database file contains tables such as:

| Table Name     | Purpose |
|----------------|---------|
| `customers`    | Stores customer records |
| `suppliers`    | Stores supplier records |
| `products`     | Stores product information & stock levels |
| `sales`        | Stores sale transactions |
| `sale_items`   | Stores each sold item in a sale transaction |
| `purchases`    | Stores purchase transactions |
| `purchase_items` | Stores each product purchased |

Import the database file:
