<?php
$page_title = "Record a New Purchase (Stock-in)";
require_once('db.php');
require_once('header.php');

// Fetch data for dropdowns - Suppliers, not Customers
$suppliers = $pdo->query("SELECT supplier_id, name FROM suppliers ORDER BY name")->fetchAll(PDO::FETCH_ASSOC);
$products = $pdo->query("SELECT product_id, name, quantity_in_stock FROM products ORDER BY name")->fetchAll(PDO::FETCH_ASSOC);

// --- Handle Form Submission ---
if (isset($_POST['complete_purchase']) && !empty($_POST['purchase_items_json'])) {
    $supplier_id = $_POST['supplier_id'];
    $purchase_items = json_decode($_POST['purchase_items_json'], true);
    $total_amount = 0;

    // Use a transaction
    $pdo->beginTransaction();
    try {
        // 1. Calculate total
        foreach ($purchase_items as $item) {
            // Use the cost price from the item list
            $total_amount += $item['quantity'] * $item['cost'];
        }

        // 2. Create the main purchase record
        $sql = "INSERT INTO purchases (supplier_id, purchase_date, total_amount) VALUES (?, NOW(), ?)";
        $stmt = $pdo->prepare($sql);
        $stmt->execute([$supplier_id, $total_amount]);
        $purchase_id = $pdo->lastInsertId();

        // 3. Add items to purchase_items and update stock
        $sql_item = "INSERT INTO purchase_items (purchase_id, product_id, quantity, cost_per_unit) VALUES (?, ?, ?, ?)";
        // INCREASES stock, not decreases
        $sql_stock = "UPDATE products SET quantity_in_stock = quantity_in_stock + ? WHERE product_id = ?";
        
        $stmt_item = $pdo->prepare($sql_item);
        $stmt_stock = $pdo->prepare($sql_stock);

        foreach ($purchase_items as $item) {
            // Insert into purchase_items
            $stmt_item->execute([
                $purchase_id,
                $item['id'],
                $item['quantity'],
                $item['cost'] // The cost at the time of purchase
            ]);

            // Update product stock
            $stmt_stock->execute([$item['quantity'], $item['id']]);
        }

        // All good, commit the transaction
        $pdo->commit();
        header("Location: purchases.php"); // Redirect to clear form
        exit;

    } catch (Exception $e) {
        // Something went wrong, roll back
        $pdo->rollBack();
        echo '<div class="container alert alert-warning" style="margin-top: 20px;"><strong>Error:</strong> ' . $e->getMessage() . '</div>';
    }
}

// --- Search and Pagination for All Purchases ---
$limit = 10;
$page = isset($_GET['page']) ? (int)$_GET['page'] : 1;
$offset = ($page - 1) * $limit;
$search_type = $_GET['search_type'] ?? 'supplier_id';
$search_term = $_GET['search'] ?? '';

// Handle search form submission
if (isset($_GET['search_supplier']) && $_GET['search_type'] == 'supplier_id') {
    $search_term = $_GET['search_supplier'];
} elseif (isset($_GET['search_id']) && $_GET['search_type'] == 'purchase_id') {
    $search_term = $_GET['search_id'];
}

$where_clause = "";
$params = [];
if (!empty($search_term)) {
    if ($search_type == 'supplier_id') {
        $where_clause = "WHERE p.supplier_id = ?"; $params[] = $search_term;
    } elseif ($search_type == 'purchase_id') {
        $where_clause = "WHERE p.purchase_id = ?"; $params[] = $search_term;
    }
}

$count_stmt = $pdo->prepare("SELECT COUNT(*) FROM purchases p $where_clause");
$count_stmt->execute($params);
$total_records = $count_stmt->fetchColumn();
$total_pages = ceil($total_records / $limit);

$sql = "SELECT p.purchase_id, p.purchase_date, s.name as supplier_name, p.total_amount
        FROM purchases p
        LEFT JOIN suppliers s ON p.supplier_id = s.supplier_id
        $where_clause
        ORDER BY p.purchase_date DESC
        LIMIT $limit OFFSET $offset";
$purchases_stmt = $pdo->prepare($sql);
$purchases_stmt->execute($params);
$purchases_list = $purchases_stmt->fetchAll(PDO::FETCH_ASSOC);
?>

<!-- "Record a New Purchase" Form -->
<div class="container">
    <h2><i data-feather="truck"></i> Record a New Purchase (Stock-in)</h2>
    
    <form action="purchases.php" method="POST" id="purchase-form" onsubmit="return finalizePurchase();">
        <div class="form-grid-2">
            <div>
                <label for="supplier_id">Supplier</label>
                <select id="supplier_id" name="supplier_id" required>
                    <option value="">Select a Supplier</option>
                    <?php foreach ($suppliers as $supplier): ?>
                        <option value="<?php echo $supplier['supplier_id']; ?>"><?php echo htmlspecialchars($supplier['name']); ?></option>
                    <?php endforeach; ?>
                </select>
            </div>
            <div>
                <label for="product_select">Add Product</label>
                <select id="product_select" onchange="addProductToPurchase()">
                    <option value="">Select a Product to Add</option>
                    <?php foreach ($products as $product): ?>
                        <option value="<?php echo $product['product_id']; ?>">
                            <?php echo htmlspecialchars($product['name']); ?> (Current Stock: <?php echo $product['quantity_in_stock']; ?>)
                        </option>
                    <?php endforeach; ?>
                </select>
            </div>
        </div>

        <h3>Purchase Items</h3>
        <table class="data-table" id="purchase-items-table">
            <thead>
                <tr>
                    <th>Product</th>
                    <th style="width: 120px;">Cost per Unit</th>
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
        <input type="hidden" name="purchase_items_json" id="purchase-items-json">
        
        <button type="submit" name="complete_purchase">Complete Purchase</button>
    </form>
</div>

<!-- "All Purchases" Table -->
<div class="container">
    <h2><i data-feather="list"></i> All Purchases</h2>

    <!-- Search Form -->
    <form action="purchases.php" method="GET" class="search-form" id="search-form">
        <select name="search_type" id="search-type-select">
            <option value="supplier_id" <?php echo ($search_type == 'supplier_id') ? 'selected' : ''; ?>>Filter by Supplier</option>
            <option value="purchase_id" <?php echo ($search_type == 'purchase_id') ? 'selected' : ''; ?>>Search by Purchase ID</option>
        </select>
        
        <!-- Supplier Dropdown (for supplier filter) -->
        <select name="search_supplier" id="supplier-search-dropdown" class="<?php echo ($search_type != 'supplier_id') ? 'hidden' : ''; ?>">
            <option value="">All Suppliers</option>
            <?php foreach ($suppliers as $supplier): ?>
                <option value="<?php echo $supplier['supplier_id']; ?>" <?php echo ($search_type == 'supplier_id' && $search_term == $supplier['supplier_id']) ? 'selected' : ''; ?>>
                    <?php echo htmlspecialchars($supplier['name']); ?>
                </option>
            <?php endforeach; ?>
        </select>
        
        <!-- ID Text Input (for ID search) -->
        <input type="text" name="search_id" id="id-search-input" class="<?php echo ($search_type != 'purchase_id') ? 'hidden' : ''; ?>" 
               value="<?php echo ($search_type == 'purchase_id') ? htmlspecialchars($search_term) : ''; ?>" placeholder="Enter Purchase ID...">
        
        <button type="submit">Search</button>
    </form>

    <table class="data-table">
        <thead>
            <tr>
                <th>Purchase ID</th>
                <th>Date</th>
                <th>Supplier</th>
                <th>Total Amount</th>
            </tr>
        </thead>
        <tbody>
            <?php if (empty($purchases_list)): ?>
                <tr><td colspan="4" style="text-align: center;">No purchases found.</td></tr>
            <?php else: ?>
                <?php foreach ($purchases_list as $purchase): ?>
                    <tr>
                        <td><?php echo $purchase['purchase_id']; ?></td>
                        <td><?php echo htmlspecialchars(date('Y-m-d H:i', strtotime($purchase['purchase_date']))); ?></td>
                        <td><?php echo htmlspecialchars($purchase['supplier_name'] ?? 'N/A'); ?></td>
                        <td>$<?php echo number_format($purchase['total_amount'], 2); ?></td>
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
                'search_supplier' => ($search_type == 'supplier_id') ? $search_term : '',
                'search_id' => ($search_type == 'purchase_id') ? $search_term : ''
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
    let purchaseItems = {}; // Holds item data

    function addProductToPurchase() {
        const productSelect = document.getElementById('product_select');
        const productId = productSelect.value;
        if (!productId || purchaseItems[productId]) {
            productSelect.value = ''; return;
        }
        fetch(`fetch_product.php?id=${productId}`)
            .then(response => response.json())
            .then(product => {
                if (product.error) {
                    alert('Error: ' + product.error);
                    return;
                }
                // USES cost_price, not sale_price
                purchaseItems[productId] = {
                    id: productId,
                    name: product.name,
                    cost: parseFloat(product.cost_price), // Key difference!
                    quantity: 1,
                    stock: parseInt(product.quantity_in_stock)
                };
                updatePurchaseTable();
                productSelect.value = '';
            }).catch(err => console.error('Fetch error:', err));
    }

    function updatePurchaseTable() {
        const tableBody = document.getElementById('purchase-items-table').getElementsByTagName('tbody')[0];
        tableBody.innerHTML = '';
        let grandTotal = 0;
        for (const productId in purchaseItems) {
            const item = purchaseItems[productId];
            const itemTotal = item.cost * item.quantity; // Uses cost
            grandTotal += itemTotal;
            const row = tableBody.insertRow();
            row.innerHTML = `
                <td>${item.name} (Stock: ${item.stock})</td>
                <td><input type="number" class="item-cost" value="${item.cost.toFixed(2)}" step="0.01" onchange="updateCost(${productId}, this.value)" style="width: 90px;"></td>
                <td><input type="number" class="item-quantity" value="${item.quantity}" min="1" onchange="updateQuantity(${productId}, this.value)" style="width: 70px;"></td>
                <td id="total-${productId}">$${itemTotal.toFixed(2)}</td>
                <td><button type="button" class="delete-btn-small" onclick="removeItem(${productId})">Remove</button></td>
            `;
        }
        document.getElementById('grand-total').textContent = `$${grandTotal.toFixed(2)}`;
    }

    // New function to update cost if needed
    function updateCost(productId, newCost) {
         if (purchaseItems[productId]) {
            const item = purchaseItems[productId];
            newCost = parseFloat(newCost);
            if (newCost < 0) newCost = 0;
            item.cost = newCost;
            
            const itemTotal = item.cost * item.quantity;
            document.getElementById(`total-${productId}`).textContent = `$${itemTotal.toFixed(2)}`;
            updateGrandTotal();
         }
    }

    function updateQuantity(productId, newQuantity) {
        if (purchaseItems[productId]) {
            const item = purchaseItems[productId];
            newQuantity = parseInt(newQuantity);
            if (newQuantity < 1) newQuantity = 1;
            
            // No stock limit for purchases
            item.quantity = newQuantity;
            const itemTotal = item.cost * item.quantity;
            document.getElementById(`total-${productId}`).textContent = `$${itemTotal.toFixed(2)}`;
            updateGrandTotal();
        }
    }
    
    function updateGrandTotal() {
        let grandTotal = 0;
        for (const productId in purchaseItems) {
            grandTotal += purchaseItems[productId].cost * purchaseItems[productId].quantity;
        }
        document.getElementById('grand-total').textContent = `$${grandTotal.toFixed(2)}`;
    }

    function removeItem(productId) {
        if (purchaseItems[productId]) {
            delete purchaseItems[productId];
            updatePurchaseTable();
        }
    }
    
    function finalizePurchase() {
        if (Object.keys(purchaseItems).length === 0) {
            alert('Cannot complete purchase. No items have been added.');
            return false; // Prevent form submission
        }
        document.getElementById('purchase-items-json').value = JSON.stringify(Object.values(purchaseItems));
        return true; // Allow form submission
    }

    // JS for search form toggle
    document.getElementById('search-type-select').addEventListener('change', function() {
        const isSupplierId = this.value === 'supplier_id';
        document.getElementById('supplier-search-dropdown').classList.toggle('hidden', !isSupplierId);
        document.getElementById('id-search-input').classList.toggle('hidden', isSupplierId);
    });
    
    // Sync search inputs before submit
    document.getElementById('search-form').addEventListener('submit', function(e) {
        const searchType = document.getElementById('search-type-select').value;
        const idInput = document.getElementById('id-search-input');
        const supplierDropdown = document.getElementById('supplier-search-dropdown');
        
        if (searchType === 'supplier_id') {
            idInput.name = ''; 
            supplierDropdown.name = 'search_supplier';
        } else {
            idInput.name = 'search_id';
            supplierDropdown.name = '';
        }
    });
</script>

<?php
require_once('footer.php');
?>
