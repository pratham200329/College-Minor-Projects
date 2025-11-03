<?php
$page_title = "Product Management";
require_once('db.php');
require_once('header.php'); // <-- FIXED

// --- C.R.U.D. LOGIC ---

$is_editing = false;
$product_to_edit = null;

// -- Handle UPDATE (Edit) ---
if (isset($_POST['update_product'])) {
    $product_id = $_POST['product_id'];
    $name = $_POST['name'];
    $sku = $_POST['sku'];
    $description = $_POST['description'];
    $supplier_id = !empty($_POST['supplier_id']) ? $_POST['supplier_id'] : null;
    $cost_price = $_POST['cost_price'];
    $sale_price = $_POST['sale_price'];
    $quantity_in_stock = $_POST['quantity_in_stock'];
    $low_stock_threshold = $_POST['low_stock_threshold'];

    $sql = "UPDATE products SET 
                name = ?, 
                sku = ?, 
                description = ?, 
                supplier_id = ?, 
                cost_price = ?, 
                sale_price = ?, 
                quantity_in_stock = ?, 
                low_stock_threshold = ? 
            WHERE product_id = ?";
    $stmt = $pdo->prepare($sql);
    $stmt->execute([
        $name, $sku, $description, $supplier_id, 
        $cost_price, $sale_price, $quantity_in_stock, 
        $low_stock_threshold, $product_id
    ]);
    
    header("Location: products.php"); // Redirect to clear form
    exit;
}

// -- Handle CREATE (Add) ---
if (isset($_POST['add_product'])) {
    $name = $_POST['name'];
    $sku = $_POST['sku'];
    $description = $_POST['description'];
    $supplier_id = !empty($_POST['supplier_id']) ? $_POST['supplier_id'] : null;
    $cost_price = $_POST['cost_price'];
    $sale_price = $_POST['sale_price'];
    $quantity_in_stock = $_POST['quantity_in_stock'];
    $low_stock_threshold = $_POST['low_stock_threshold'];

    $sql = "INSERT INTO products (name, sku, description, supplier_id, cost_price, sale_price, quantity_in_stock, low_stock_threshold) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)";
    $stmt = $pdo->prepare($sql);
    $stmt->execute([
        $name, $sku, $description, $supplier_id, 
        $cost_price, $sale_price, $quantity_in_stock, 
        $low_stock_threshold
    ]);
    
    header("Location: products.php");
    exit;
}

// -- Handle DELETE ---
if (isset($_GET['delete'])) {
    $product_id = $_GET['delete'];
    try {
        $sql = "DELETE FROM products WHERE product_id = ?";
        $stmt = $pdo->prepare($sql);
        $stmt->execute([$product_id]);
    } catch (PDOException $e) {
        // Handle constraint violation
        echo '<div class="container alert alert-warning" style="margin-top: 20px;"><strong>Error:</strong> Cannot delete this product. It is linked to existing sales or purchases.</div>';
    }
    // We don't redirect here so the user can see the error message if one occurs
}

// -- Handle READ (for editing) ---
if (isset($_GET['edit'])) {
    $is_editing = true;
    $product_id = $_GET['edit'];
    $stmt = $pdo->prepare("SELECT * FROM products WHERE product_id = ?");
    $stmt->execute([$product_id]);
    $product_to_edit = $stmt->fetch(PDO::FETCH_ASSOC);
}

// --- DATA FOR PAGE ---
$suppliers = $pdo->query("SELECT supplier_id, name FROM suppliers ORDER BY name")->fetchAll(PDO::FETCH_ASSOC);
$all_products = $pdo->query("
    SELECT p.*, s.name as supplier_name 
    FROM products p 
    LEFT JOIN suppliers s ON p.supplier_id = s.supplier_id 
    ORDER BY p.name
")->fetchAll(PDO::FETCH_ASSOC);

?>

<div class="container">
    <!-- Form will now change based on whether we are editing or adding -->
    <h2>
        <i data-feather="<?php echo $is_editing ? 'edit' : 'plus-circle'; ?>"></i>
        <?php echo $is_editing ? 'Edit Product' : 'Add New Product'; ?>
    </h2>

    <form action="products.php" method="POST">
        <!-- Hidden input to store product ID when editing -->
        <?php if ($is_editing): ?>
            <input type="hidden" name="product_id" value="<?php echo $product_to_edit['product_id']; ?>">
        <?php endif; ?>

        <!-- Full-width fields -->
        <div class="form-grid-1">
            <div>
                <label for="name">Product Name</label>
                <input type="text" id="name" name="name" value="<?php echo htmlspecialchars($product_to_edit['name'] ?? ''); ?>" required>
            </div>
            <div>
                <label for="sku">SKU (Stock Keeping Unit)</label>
                <input type="text" id="sku" name="sku" value="<?php echo htmlspecialchars($product_to_edit['sku'] ?? ''); ?>">
            </div>
            <div>
                <label for="description">Description</label>
                <textarea id="description" name="description"><?php echo htmlspecialchars($product_to_edit['description'] ?? ''); ?></textarea>
            </div>
        </div>

        <!-- Two-column grid for smaller fields -->
        <div class="form-grid-2">
            <div>
                <label for="supplier_id">Supplier</label>
                <select id="supplier_id" name="supplier_id">
                    <option value="">None</option>
                    <?php foreach ($suppliers as $supplier): ?>
                        <option value="<?php echo $supplier['supplier_id']; ?>" 
                            <?php echo (isset($product_to_edit) && $product_to_edit['supplier_id'] == $supplier['supplier_id']) ? 'selected' : ''; ?>>
                            <?php echo htmlspecialchars($supplier['name']); ?>
                        </option>
                    <?php endforeach; ?>
                </select>
            </div>
             <div>
                <label for="quantity_in_stock">Quantity in Stock</label>
                <input type="number" id="quantity_in_stock" name="quantity_in_stock" value="<?php echo $product_to_edit['quantity_in_stock'] ?? 0; ?>" required>
            </div>
            <div>
                <label for="cost_price">Cost Price ($)</label>
                <input type="number" id="cost_price" name="cost_price" step="0.01" min="0" value="<?php echo $product_to_edit['cost_price'] ?? 0.00; ?>" required>
            </div>
            <div>
                <label for="sale_price">Sale Price ($)</label>
                <input type="number" id="sale_price" name="sale_price" step="0.01" min="0" value="<?php echo $product_to_edit['sale_price'] ?? 0.00; ?>" required>
            </div>
            <div>
                <label for="low_stock_threshold">Low Stock Threshold</label>
                <input type="number" id="low_stock_threshold" name="low_stock_threshold" value="<?php echo $product_to_edit['low_stock_threshold'] ?? 10; ?>" required>
            </div>
        </div>
        
        <!-- Submit button changes text based on action -->
        <div class="form-actions">
            <?php if ($is_editing): ?>
                <button type="submit" name="update_product">Update Product</button>
                <a href="products.php" class="cancel-btn">Cancel Edit</a>
            <?php else: ?>
                <button type="submit" name="add_product">Add Product</button>
            <?php endif; ?>
        </div>
    </form>
</div>

<div class="container">
    <h2><i data-feather="package"></i> All Products</h2>
    
    <table class="data-table">
        <thead>
            <tr>
                <th>Name</th>
                <th>SKU</th>
                <th>Supplier</th>
                <th>Cost</th>
                <th>Price</th>
                <th>Stock</th>
                <th>Low Stock At</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            <?php if (empty($all_products)): ?>
                <tr><td colspan="8" style="text-align: center;">No products found.</td></tr>
            <?php else: ?>
                <?php foreach ($all_products as $product): ?>
                    <tr>
                        <td><?php echo htmlspecialchars($product['name']); ?></td>
                        <td><?php echo htmlspecialchars($product['sku']); ?></td>
                        <td><?php echo htmlspecialchars($product['supplier_name'] ?? 'N/A'); ?></td>
                        <td>$<?php echo number_format($product['cost_price'], 2); ?></td>
                        <td>$<?php echo number_format($product['sale_price'], 2); ?></td>
                        <td><?php echo $product['quantity_in_stock']; ?></td>
                        <td><?php echo $product['low_stock_threshold']; ?></td>
                        <td class="action-buttons">
                            <!-- NEW "Edit" button -->
                            <a href="products.php?edit=<?php echo $product['product_id']; ?>" class="edit-btn" title="Edit">
                                <i data-feather="edit-2"></i>
                            </a>
                            <!-- Delete button (now a form for safety) -->
                            <form action="products.php?delete=<?php echo $product['product_id']; ?>" method="POST" style="display: inline;" onsubmit="return confirm('Are you sure you want to delete this product?');">
                                <button type="submit" class="delete-btn" title="Delete">
                                    <i data-feather="trash-2"></i>
                                </button>
                            </form>
                        </td>
                    </tr>
                <?php endforeach; ?>
            <?php endif; ?>
        </tbody>
    </table>
</div>

<?php
require_once('footer.php'); // <-- FIXED
?>

