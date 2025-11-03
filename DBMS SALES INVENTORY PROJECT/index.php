<?php
$page_title = "Dashboard";
require_once('db.php'); // Ensure this uses $pdo
require_once('header.php');

// --- Dashboard Stats ---
// Ensure all queries use $pdo

// 1. Total Products
$stmt = $pdo->query("SELECT COUNT(*) FROM products");
$total_products = $stmt->fetchColumn();

// 2. Low Stock Items (quantity < 10)
$stmt = $pdo->query("SELECT COUNT(*) FROM products WHERE quantity_in_stock < 10");
$low_stock_count = $stmt->fetchColumn();

// 3. Total Sales Value
$stmt = $pdo->query("SELECT SUM(total_amount) FROM sales");
$total_sales = $stmt->fetchColumn();

// 4. Total Customers
$stmt = $pdo->query("SELECT COUNT(*) FROM customers");
$total_customers = $stmt->fetchColumn();


// --- Dynamic Content ---
if ($low_stock_count > 0) {
    // Query for low stock items
    $low_stock_items = $pdo->query("SELECT product_id, name, quantity_in_stock 
                                    FROM products 
                                    WHERE quantity_in_stock < 10 
                                    LIMIT 5")
                            ->fetchAll(PDO::FETCH_ASSOC);
} else {
    // Query for last 5 transactions (both sales and purchases)
    $recent_transactions = $pdo->query("
        (SELECT 
            'Sale' as type, 
            s.sale_id as id, 
            s.sale_date as date, 
            c.name as party_name, 
            s.total_amount as amount
        FROM sales s
        JOIN customers c ON s.customer_id = c.customer_id
        ORDER BY s.sale_date DESC
        LIMIT 3)
        
        UNION ALL
        
        (SELECT 
            'Purchase' as type, 
            p.purchase_id as id, 
            p.purchase_date as date, 
            sup.name as party_name, 
            p.total_amount as amount
        FROM purchases p
        JOIN suppliers sup ON p.supplier_id = sup.supplier_id
        ORDER BY p.purchase_date DESC
        LIMIT 2)
        
        ORDER BY date DESC
        LIMIT 5
    ")->fetchAll(PDO::FETCH_ASSOC);
}

?>

<section class="stats-grid">
    <!-- Card 1: Total Products -->
    <a href="products.php" class="stat-card green">
        <div class="stat-info">
            <h3>Total Products</h3>
            <p><?php echo $total_products; ?></p>
        </div>
        <div class="stat-icon">
            <i data-feather="package"></i>
        </div>
    </a>

    <!-- Card 2: Low Stock Items -->
    <a href="products.php" class="stat-card red">
        <div class="stat-info">
            <h3>Low Stock Items</h3>
            <p><?php echo $low_stock_count; ?></p>
        </div>
        <div class="stat-icon">
            <i data-feather="alert-triangle"></i>
        </div>
    </a>

    <!-- Card 3: Total Sales -->
    <a href="sales.php" class="stat-card blue">
        <div class="stat-info">
            <h3>Total Sales</h3>
            <p>$<?php echo number_format($total_sales, 2); ?></p>
        </div>
        <div class="stat-icon">
            <i data-feather="dollar-sign"></i>
        </div>
    </a>

    <!-- Card 4: Total Customers -->
    <a href="customers.php" class="stat-card purple">
        <div class="stat-info">
            <h3>Total Customers</h3>
            <p><?php echo $total_customers; ?></p>
        </div>
        <div class="stat-icon">
            <i data-feather="users"></i>
        </div>
    </a>
</section>

<!-- Dynamic Content: Low Stock OR Recent Transactions -->
<section class="container">
    
    <?php if ($low_stock_count > 0): ?>
        <h2><i data-feather="alert-triangle" style="color: #e74c3c;"></i> Low Stock Alerts (Under 10)</h2>
        <div class="alert alert-warning">
            The following items are running low on stock.
        </div>
        <table class="data-table">
            <thead>
                <tr>
                    <th>Product ID</th>
                    <th>Product Name</th>
                    <th>Quantity in Stock</th>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($low_stock_items as $item): ?>
                    <tr>
                        <td><?php echo htmlspecialchars($item['product_id']); ?></td>
                        <td><?php echo htmlspecialchars($item['name']); ?></td>
                        <td><?php echo htmlspecialchars($item['quantity_in_stock']); ?></td>
                    </tr>
                <?php endforeach; ?>
            </tbody>
        </table>

    <?php else: ?>
        <h2><i data-feather="clock"></i> Recent Transactions</h2>
        <div class="alert alert-info">
            All products are sufficiently stocked (stock > 10). Well done!
        </div>
        <table class="data-table">
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Type</th>
                    <th>Customer/Supplier</th>
                    <th>Amount</th>
                </tr>
            </thead>
            <tbody>
                <?php if (empty($recent_transactions)): ?>
                    <tr>
                        <td colspan="4" style="text-align: center;">No transactions found.</td>
                    </tr>
                <?php else: ?>
                    <?php foreach ($recent_transactions as $tx): ?>
                        <tr>
                            <td><?php echo htmlspecialchars(date('Y-m-d H:i', strtotime($tx['date']))); ?></td>
                            <td>
                                <?php if ($tx['type'] == 'Sale'): ?>
                                    <span class="transaction-type-label sale">Sale</span>
                                <?php else: ?>
                                    <span class="transaction-type-label purchase">Purchase</span>
                                <?php endif; ?>
                            </td>
                            <td><?php echo htmlspecialchars($tx['party_name']); ?></td>
                            <td>$<?php echo number_format($tx['amount'], 2); ?></td>
                        </tr>
                    <?php endforeach; ?>
                <?php endif; ?>
            </tbody>
        </table>
    <?php endif; ?>
    
</section>

<?php
require_once('footer.php');
?>

