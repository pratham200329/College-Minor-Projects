<?php
require 'db.php';
$message = '';
$error = '';
$edit_customer = null;

// --- Handle Form Submissions (Create, Update, Delete) ---
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    try {
        // --- ADD NEW CUSTOMER ---
        if (isset($_POST['add_customer'])) {
            $sql = "INSERT INTO customers (name, email, phone, address) VALUES (?, ?, ?, ?)";
            $stmt = $pdo->prepare($sql);
            $stmt->execute([$_POST['name'], $_POST['email'], $_POST['phone'], $_POST['address']]);
            $message = "Customer added successfully!";
        }

        // --- UPDATE CUSTOMER ---
        if (isset($_POST['update_customer'])) {
            $sql = "UPDATE customers SET name = ?, email = ?, phone = ?, address = ? WHERE customer_id = ?";
            $stmt = $pdo->prepare($sql);
            $stmt->execute([$_POST['name'], $_POST['email'], $_POST['phone'], $_POST['address'], $_POST['customer_id']]);
            $message = "Customer updated successfully!";
        }

        // --- DELETE CUSTOMER ---
        if (isset($_POST['delete_customer'])) {
            // Check for relations before deleting (e.g., in sales)
            $stmt = $pdo->prepare("SELECT COUNT(*) FROM sales WHERE customer_id = ?");
            $stmt->execute([$_POST['customer_id']]);
            if ($stmt->fetchColumn() > 0) {
                $error = "Cannot delete customer. They are linked to existing sales. You could mark them as 'inactive' instead.";
            } else {
                $sql = "DELETE FROM customers WHERE customer_id = ?";
                $stmt = $pdo->prepare($sql);
                $stmt->execute([$_POST['customer_id']]);
                $message = "Customer deleted successfully!";
            }
        }
    } catch (PDOException $e) {
        // Check for unique constraint violation (e.g., duplicate email)
        if ($e->getCode() == 23000) {
            $error = "Error: A customer with this email already exists.";
        } else {
            $error = "Database error: " . $e->getMessage();
        }
    }
}

// --- Handle Edit Request ---
if (isset($_GET['action']) && $_GET['action'] == 'edit' && isset($_GET['id'])) {
    $stmt = $pdo->prepare("SELECT * FROM customers WHERE customer_id = ?");
    $stmt->execute([$_GET['id']]);
    $edit_customer = $stmt->fetch();
}

// --- Fetch All Customers ---
$customers = $pdo->query("SELECT * FROM customers ORDER BY name ASC")->fetchAll();

require 'header.php';
?>

<header>
    <h1>Customer Management</h1>
</header>

<?php if ($message): ?><div class="alert alert-success"><?php echo $message; ?></div><?php endif; ?>
<?php if ($error): ?><div class="alert alert-danger"><?php echo $error; ?></div><?php endif; ?>

<!-- Add/Edit Customer Form -->
<section class="container">
    <h2><?php echo $edit_customer ? 'Edit Customer' : 'Add New Customer'; ?></h2>
    <form action="customers.php" method="POST">
        <?php if ($edit_customer): ?>
            <input type="hidden" name="customer_id" value="<?php echo $edit_customer['customer_id']; ?>">
        <?php endif; ?>
        
        <div class="form-grid">
            <div class="form-group">
                <label for="name">Customer Name</label>
                <input type="text" id="name" name="name" value="<?php echo htmlspecialchars($edit_customer['name'] ?? ''); ?>" required>
            </div>
            <div class="form-group">
                <label for="email">Email</label>
                <input type="email" id="email" name="email" value="<?php echo htmlspecialchars($edit_customer['email'] ?? ''); ?>">
            </div>
            <div class="form-group">
                <label for="phone">Phone</label>
                <input type="text" id="phone" name="phone" value="<?php echo htmlspecialchars($edit_customer['phone'] ?? ''); ?>">
            </div>
            <div class="form-group">
                <label for="address">Address</label>
                <input type="text" id="address" name="address" value="<?php echo htmlspecialchars($edit_customer['address'] ?? ''); ?>">
            </div>
        </div>
        <div class="form-group" style="margin-top: 20px;">
            <?php if ($edit_customer): ?>
                <button type="submit" name="update_customer" class="btn btn-primary">Update Customer</button>
                <a href="customers.php" class="btn btn-secondary">Cancel Edit</a>
            <?php else: ?>
                <button type="submit" name="add_customer" class="btn btn-primary">Add Customer</button>
            <?php endif; ?>
        </div>
    </form>
</section>

<!-- Customer List -->
<section class="container">
    <h2>All Customers</h2>
    <table class="data-table">
        <thead>
            <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Phone</th>
                <th>Address</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            <?php foreach ($customers as $customer): ?>
            <tr>
                <td><?php echo htmlspecialchars($customer['name']); ?></td>
                <td><?php echo htmlspecialchars($customer['email']); ?></td>
                <td><?php echo htmlspecialchars($customer['phone']); ?></td>
                <td><?php echo htmlspecialchars($customer['address']); ?></td>
                <td class="actions">
                    <a href="customers.php?action=edit&id=<?php echo $customer['customer_id']; ?>" class="btn btn-secondary btn-sm">Edit</a>
                    <form action="customers.php" method="POST" onsubmit="return confirm('Are you sure? This may fail if the customer is linked to sales.');" style="display:inline;">
                        <input type="hidden" name="customer_id" value="<?php echo $customer['customer_id']; ?>">
                        <button type="submit" name="delete_customer" class="btn btn-danger btn-sm">Delete</button>
                    </form>
                </td>
            </tr>
            <?php endforeach; ?>
        </tbody>
    </table>
</section>

<?php require 'footer.php'; ?>
