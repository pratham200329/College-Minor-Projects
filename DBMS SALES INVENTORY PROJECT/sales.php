<?php
$page_title = "Record a New Sale";
require_once('db.php');
require_once('header.php');

// Fetch data for dropdowns
$customers = $pdo->query("SELECT customer_id, name FROM customers ORDER BY name")->fetchAll(PDO::FETCH_ASSOC);
$products = $pdo->query("SELECT product_id, name, quantity_in_stock FROM products WHERE quantity_in_stock > 0 ORDER BY name")->fetchAll(PDO::FETCH_ASSOC);

// --- Handle Form Submission ---
if (isset($_POST['complete_sale']) && !empty($_POST['sale_items_json'])) {
    $customer_id = $_POST['customer_id'];
    $sale_items = json_decode($_POST['sale_items_json'], true);
    $total_amount = 0;

    // Use a transaction
    $pdo->beginTransaction();
    try {
        // 1. Calculate total and check stock
        foreach ($sale_items as $item) {
            $stmt = $pdo->prepare("SELECT quantity_in_stock, cost_price FROM products WHERE product_id = ?");
            $stmt->execute([$item['id']]);
            $product = $stmt->fetch(PDO::FETCH_ASSOC);

            if (!$product) {
                throw new Exception("Product with ID " . $item['id'] . " not found.");
            }
            if ($product['quantity_in_stock'] < $item['quantity']) {
                throw new Exception("Not enough stock for " . $item['name'] . ". Available: " . $product['quantity_in_stock']);
            }
            // Use the price from the item list, which was fetched (and potentially edited)
            $total_amount += $item['quantity'] * $item['price'];
        }

        // 2. Create the main sale record
        $sql = "INSERT INTO sales (customer_id, sale_date, total_amount) VALUES (?, NOW(), ?)";
        $stmt = $pdo->prepare($sql);
        $stmt->execute([$customer_id, $total_amount]);
        $sale_id = $pdo->lastInsertId();

        // 3. Add items to sale_items and update stock
        $sql_item = "INSERT INTO sale_items (sale_id, product_id, quantity, price_per_unit, cost_per_unit) VALUES (?, ?, ?, ?, ?)";
        $sql_stock = "UPDATE products SET quantity_in_stock = quantity_in_stock - ? WHERE product_id = ?";
        
        $stmt_item = $pdo->prepare($sql_item);
        $stmt_stock = $pdo->prepare($sql_stock);

        foreach ($sale_items as $item) {
            // Fetch product's cost_price at the time of sale
            $stmt_cost = $pdo->prepare("SELECT cost_price FROM products WHERE product_id = ?");
            $stmt_cost->execute([$item['id']]);
            $product_cost = $stmt_cost->fetchColumn();

            // Insert into sale_items
            $stmt_item->execute([
                $sale_id,
                $item['id'],
                $item['quantity'],
                $item['price'], // The (potentially edited) price at the time of sale
                $product_cost  // The cost at the time of sale
            ]);

            // Update product stock
            $stmt_stock->execute([$item['quantity'], $item['id']]);
        }

        // All good, commit the transaction
        $pdo->commit();
        header("Location: sales.php"); // Redirect to clear form
        exit;

    } catch (Exception $e) {
        // Something went wrong, roll back
        $pdo->rollBack();
        echo '<div class="container alert alert-warning" style="margin-top: 20px;"><strong>Error:</strong> ' . $e->getMessage() . '</div>';
    }
}

// --- Search and Pagination for All Sales ---
$limit = 10;
$page = isset($_GET['page']) ? (int)$_GET['page'] : 1;
$offset = ($page - 1) * $limit;
$search_type = $_GET['search_type'] ?? 'customer_id';
$search_term = $_GET['search'] ?? '';

// Handle search form submission
if (isset($_GET['search_customer']) && $_GET['search_type'] == 'customer_id') {
    $search_term = $_GET['search_customer'];
} elseif (isset($_GET['search_id']) && $_GET['search_type'] == 'sale_id') {
    $search_term = $_GET['search_id'];
}

$where_clause = "";
$params = [];
if (!empty($search_term)) {
    if ($search_type == 'customer_id') {
        $where_clause = "WHERE s.customer_id = ?"; $params[] = $search_term;
    } elseif ($search_type == 'sale_id') {
        $where_clause = "WHERE s.sale_id = ?"; $params[] = $search_term;
    }
}
$count_stmt = $pdo->prepare("SELECT COUNT(*) FROM sales s $where_clause");
$count_stmt->execute($params);
$total_records = $count_stmt->fetchColumn();
$total_pages = ceil($total_records / $limit);
$sql = "SELECT s.sale_id, s.sale_date, c.name as customer_name, s.total_amount
        FROM sales s
        LEFT JOIN customers c ON s.customer_id = c.customer_id
        $where_clause
        ORDER BY s.sale_date DESC
        LIMIT $limit OFFSET $offset";
$sales_stmt = $pdo->prepare($sql);
$sales_stmt->execute($params);
$sales_list = $sales_stmt->fetchAll(PDO::FETCH_ASSOC);
?>

<!-- "Record a New Sale" Form -->
<div class="container">
    <h2><i data-feather="shopping-cart"></i> Record a New Sale</h2>
    
    <form action="sales.php" method="POST" id="sale-form" onsubmit="return finalizeSale();">
        <div class="form-grid-2">
            <div>
                <label for="customer_id">Customer</label>
                <select id="customer_id" name="customer_id" required>
                    <option value="">Select a Customer</option>
                    <?php foreach ($customers as $customer): ?>
                        <option value="<?php echo $customer['customer_id']; ?>"><?php echo htmlspecialchars($customer['name']); ?></option>
                    <?php endforeach; ?>
                </select>
            </div>
            <div>
                <label for="product_select">Add Product</label>
                <select id="product_select" onchange="addProductToSale()">
                    <option value="">Select a Product to Add</option>
                    <?php foreach ($products as $product): ?>
                        <option value="<?php echo $product['product_id']; ?>">
                            <?php echo htmlspecialchars($product['name']); ?> (Stock: <?php echo $product['quantity_in_stock']; ?>)
                        </option>
                    <?php endforeach; ?>
                </select>
            </div>
        </div>

        <h3>Sale Items</h3>
        <table class="data-table" id="sale-items-table">
            <thead>
                <tr>
                    <th>Product</th>
                    <th style="width: 120px;">Price</th>
                    <th style="width: 100px;">Quantity</th>
                    <th style="width: 120px;">Total</th>
                    <th style="width: 100px;">Action</th>
                </tr>
            </thead>
            <tbody>
                <!-- Items will be added here by JavaScript -->
            </tbody>
            <tfoot>
                <tr>
                    <th colspan="3" style="text-align: right;">Grand Total:</th>
                    <th id="grand-total">$0.00</th>
                    <th></th>
                </tr>
            </tfoot>
        </table>

        <!-- This hidden input will store the list of items -->
        <input type="hidden" name="sale_items_json" id="sale-items-json">
        
        <button type="submit" name="complete_sale">Complete Sale</button>
    </form>
</div>

<!-- "All Sales" Table -->
<div class="container">
    <h2><i data-feather="list"></i> All Sales</h2>

    <!-- Search Form -->
    <form action="sales.php" method="GET" class="search-form" id="search-form">
        <select name="search_type" id="search-type-select">
            <option value="customer_id" <?php echo ($search_type == 'customer_id') ? 'selected' : ''; ?>>Filter by Customer</option>
            <option value="sale_id" <?php echo ($search_type == 'sale_id') ? 'selected' : ''; ?>>Search by Sale ID</option>
        </select>
        
        <!-- Customer Dropdown (for customer filter) -->
        <select name="search_customer" id="customer-search-dropdown" class="<?php echo ($search_type != 'customer_id') ? 'hidden' : ''; ?>">
            <option value="">All Customers</option>
            <?php foreach ($customers as $customer): ?>
                <option value="<?php echo $customer['customer_id']; ?>" <?php echo ($search_type == 'customer_id' && $search_term == $customer['customer_id']) ? 'selected' : ''; ?>>
                    <?php echo htmlspecialchars($customer['name']); ?>
                </option>
            <?php endforeach; ?>
        </select>
        
        <!-- ID Text Input (for ID search) -->
        <input type="text" name="search_id" id="id-search-input" class="<?php echo ($search_type != 'sale_id') ? 'hidden' : ''; ?>" 
               value="<?php echo ($search_type == 'sale_id') ? htmlspecialchars($search_term) : ''; ?>" placeholder="Enter Sale ID...">
        
        <button type="submit">Search</button>
    </form>

    <table class="data-table">
        <thead>
            <tr>
                <th>Sale ID</th>
                <th>Date</th>
                <th>Customer</th>
                <th>Total Amount</th>
            </tr>
        </thead>
        <tbody>
            <?php if (empty($sales_list)): ?>
                <tr><td colspan="4" style="text-align: center;">No sales found.</td></tr>
            <?php else: ?>
                <?php foreach ($sales_list as $sale): ?>
                    <tr>
                        <td><?php echo $sale['sale_id']; ?></td>
                        <td><?php echo htmlspecialchars(date('Y-m-d H:i', strtotime($sale['sale_date']))); ?></td>
                        <td><?php echo htmlspecialchars($sale['customer_name'] ?? 'N/A'); ?></td>
                        <td>$<?php echo number_format($sale['total_amount'], 2); ?></td>
                    </tr>
                <?php endforeach; ?>
            <?php endif; ?>
        </tbody>
    </table>

    <!-- Pagination -->
    <div class="pagination">
        <?php for ($i = 1; $i <= $total_pages; $i++): ?>
            <!-- Build the query string for pagination links -->
            <?php
            $query_params = [
                'page' => $i,
                'search_type' => $search_type,
                'search_customer' => ($search_type == 'customer_id') ? $search_term : '',
                'search_id' => ($search_type == 'sale_id') ? $search_term : ''
            ];
            ?>
            <a href="?<?php echo http_build_query($query_params); ?>" 
               class="<?php echo ($i == $page) ? 'active' : ''; ?>">
               <?php echo $i; ?>
            </a>
        <?php endfor; ?>
    </div>
</div>

<!-- JavaScript for "Add to Cart" -->
<script>
    let saleItems = {}; // Holds item data

    function addProductToSale() {
        const productSelect = document.getElementById('product_select');
        const productId = productSelect.value;
        if (!productId || saleItems[productId]) {
            productSelect.value = ''; return;
        }
        fetch(`fetch_product.php?id=${productId}`)
            .then(response => response.json())
            .then(product => {
                if (product.error) {
                    alert('Error: ' + product.error);
                    return;
                }
                saleItems[productId] = {
                    id: productId,
                    name: product.name,
                    price: parseFloat(product.sale_price),
                    quantity: 1,
                    stock: parseInt(product.quantity_in_stock)
                };
                updateSaleTable();
                productSelect.value = '';
            }).catch(err => console.error('Fetch error:', err));
    }

    function updateSaleTable() {
        const tableBody = document.getElementById('sale-items-table').getElementsByTagName('tbody')[0];
        tableBody.innerHTML = '';
        let grandTotal = 0;
        for (const productId in saleItems) {
            const item = saleItems[productId];
            const itemTotal = item.price * item.quantity;
            grandTotal += itemTotal;
            const row = tableBody.insertRow();
            row.innerHTML = `
                <td>${item.name} (Stock: ${item.stock})</td>
                <!-- NEW FEATURE: Price is now an input field -->
                <td><input type="number" class="item-price" value="${item.price.toFixed(2)}" step="0.01" onchange="updatePrice(${productId}, this.value)" style="width: 90px;"></td>
                <td><input type="number" class="item-quantity" value="${item.quantity}" min="1" max="${item.stock}" onchange="updateQuantity(${productId}, this.value)" style="width: 70px;"></td>
                <td id="total-${productId}">$${itemTotal.toFixed(2)}</td>
                <td><button type="button" class="delete-btn-small" onclick="removeItem(${productId})">Remove</button></td>
            `;
        }
        document.getElementById('grand-total').textContent = `$${grandTotal.toFixed(2)}`;
    }

    // NEW FUNCTION to update price
    function updatePrice(productId, newPrice) {
         if (saleItems[productId]) {
            const item = saleItems[productId];
            newPrice = parseFloat(newPrice);
            if (newPrice < 0) newPrice = 0;
            item.price = newPrice;
            
            const itemTotal = item.price * item.quantity;
            document.getElementById(`total-${productId}`).textContent = `$${itemTotal.toFixed(2)}`;
            updateGrandTotal();
         }
    }

    function updateQuantity(productId, newQuantity) {
        if (saleItems[productId]) {
            const item = saleItems[productId];
            newQuantity = parseInt(newQuantity);
            if (newQuantity < 1) newQuantity = 1;
            if (newQuantity > item.stock) {
                newQuantity = item.stock;
                alert('Not enough stock. Maximum available: ' + item.stock);
            }
            item.quantity = newQuantity;
            // Use the (potentially edited) price
            const itemTotal = item.price * item.quantity;
            document.getElementById(`total-${productId}`).textContent = `$${itemTotal.toFixed(2)}`;
            updateGrandTotal();
        }
    }
    
    function updateGrandTotal() {
        let grandTotal = 0;
        for (const productId in saleItems) {
            // Use the (potentially edited) price
            grandTotal += saleItems[productId].price * saleItems[productId].quantity;
        }
        document.getElementById('grand-total').textContent = `$${grandTotal.toFixed(2)}`;
    }

    function removeItem(productId) {
        if (saleItems[productId]) {
            delete saleItems[productId];
            updateSaleTable();
        }
    }
    
    function finalizeSale() {
        if (Object.keys(saleItems).length === 0) {
            alert('Cannot complete sale. No items have been added.');
            return false; // Prevent form submission
        }
        document.getElementById('sale-items-json').value = JSON.stringify(Object.values(saleItems));
        return true; // Allow form submission
    }

    // JS for search form toggle
    document.getElementById('search-type-select').addEventListener('change', function() {
        const isCustomerId = this.value === 'customer_id';
        document.getElementById('customer-search-dropdown').classList.toggle('hidden', !isCustomerId);
        document.getElementById('id-search-input').classList.toggle('hidden', isCustomerId);
    });
    
    // *** THIS IS THE BUG FIX ***
    // Sync search inputs before submit
    document.getElementById('search-form').addEventListener('submit', function(e) {
        const searchType = document.getElementById('search-type-select').value;
        const idInput = document.getElementById('id-search-input');
        const customerDropdown = document.getElementById('customer-search-dropdown');
        
        // This ensures the correct name attribute is set for the search term
        if (searchType === 'customer_id') {
            idInput.name = ''; // Disable ID input
            customerDropdown.name = 'search_customer'; // Enable Customer input
        } else {
            idInput.name = 'search_id'; // Enable ID input
            customerDropdown.name = ''; // Disable Customer input
        }
    });
</script>

<?php
require_once('footer.php');
?>

