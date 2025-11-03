<?php
require 'db.php';
$message = '';
$error = '';
$edit_supplier = null;

// --- Handle Form Submissions (Create, Update, Delete) ---
// This follows the exact same logic as products.php
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    try {
        // --- ADD NEW SUPPLIER ---
        if (isset($_POST['add_supplier'])) {
            $sql = "INSERT INTO suppliers (name, contact_person, email, phone) VALUES (?, ?, ?, ?)";
            $stmt = $pdo->prepare($sql);
            $stmt->execute([$_POST['name'], $_POST['contact_person'], $_POST['email'], $_POST['phone']]);
            $message = "Supplier added successfully!";
        }

        // --- UPDATE SUPPLIER ---
        if (isset($_POST['update_supplier'])) {
            $sql = "UPDATE suppliers SET name = ?, contact_person = ?, email = ?, phone = ? WHERE supplier_id = ?";
            $stmt = $pdo->prepare($sql);
            $stmt->execute([$_POST['name'], $_POST['contact_person'], $_POST['email'], $_POST['phone'], $_POST['supplier_id']]);
            $message = "Supplier updated successfully!";
        }

        // --- DELETE SUPPLIER ---
        if (isset($_POST['delete_supplier'])) {
            // Check for relations before deleting
            $stmt = $pdo->prepare("SELECT COUNT(*) FROM products WHERE supplier_id = ?");
            $stmt->execute([$_POST['supplier_id']]);
            if ($stmt->fetchColumn() > 0) {
                $error = "Cannot delete supplier. They are linked to products. Set supplier to 'None' on those products first.";
            } else {
                $sql = "DELETE FROM suppliers WHERE supplier_id = ?";
                $stmt = $pdo->prepare($sql);
                $stmt->execute([$_POST['supplier_id']]);
                $message = "Supplier deleted successfully!";
            }
        }
    } catch (PDOException $e) {
        // Check for unique constraint violation (e.g., duplicate email)
        if ($e->getCode() == 23000) {
            $error = "Error: An entry with this email already exists.";
        } else {
            $error = "Database error: " . $e->getMessage();
        }
    }
}

// --- Handle Edit Request ---
if (isset($_GET['action']) && $_GET['action'] == 'edit' && isset($_GET['id'])) {
    $stmt = $pdo->prepare("SELECT * FROM suppliers WHERE supplier_id = ?");
    $stmt->execute([$_GET['id']]);
    $edit_supplier = $stmt->fetch();
}

// --- Fetch All Suppliers ---
$suppliers = $pdo->query("SELECT * FROM suppliers ORDER BY name ASC")->fetchAll();

require 'header.php';
?>

<header>
    <h1>Supplier Management</h1>
</header>

<?php if ($message): ?><div class="alert alert-success"><?php echo $message; ?></div><?php endif; ?>
<?php if ($error): ?><div class="alert alert-danger"><?php echo $error; ?></div><?php endif; ?>

<!-- Add/Edit Supplier Form -->
<section class="container">
    <h2><?php echo $edit_supplier ? 'Edit Supplier' : 'Add New Supplier'; ?></h2>
    <form action="suppliers.php" method="POST">
        <?php if ($edit_supplier): ?>
            <input type="hidden" name="supplier_id" value="<?php echo $edit_supplier['supplier_id']; ?>">
        <?php endif; ?>
        
        <div class="form-grid">
            <div class="form-group">
                <label for="name">Supplier Name</label>
                <input type="text" id="name" name="name" value="<?php echo htmlspecialchars($edit_supplier['name'] ?? ''); ?>" required>
            </div>
            <div class="form-group">
                <label for="contact_person">Contact Person</label>
                <input type="text" id="contact_person" name="contact_person" value="<?php echo htmlspecialchars($edit_supplier['contact_person'] ?? ''); ?>">
            </div>
            <div class="form-group">
                <label for="email">Email</label>
                <input type="email" id="email" name="email" value="<?php echo htmlspecialchars($edit_supplier['email'] ?? ''); ?>">
            </div>
            <div class="form-group">
                <label for="phone">Phone</label>
                <input type="text" id="phone" name="phone" value="<?php echo htmlspecialchars($edit_supplier['phone'] ?? ''); ?>">
            </div>
        </div>
        <div class="form-group" style="margin-top: 20px;">
            <?php if ($edit_supplier): ?>
                <button type="submit" name="update_supplier" class="btn btn-primary">Update Supplier</button>
                <a href="suppliers.php" class="btn btn-secondary">Cancel Edit</a>
            <?php else: ?>
                <button type="submit" name="add_supplier" class="btn btn-primary">Add Supplier</button>
            <?php endif; ?>
        </div>
    </form>
</section>

<!-- Supplier List -->
<section class="container">
    <h2>All Suppliers</h2>
    <table class="data-table">
        <thead>
            <tr>
                <th>Name</th>
                <th>Contact Person</th>
                <th>Email</th>
                <th>Phone</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            <?php foreach ($suppliers as $supplier): ?>
            <tr>
                <td><?php echo htmlspecialchars($supplier['name']); ?></td>
                <td><?php echo htmlspecialchars($supplier['contact_person']); ?></td>
                <td><?php echo htmlspecialchars($supplier['email']); ?></td>
                <td><?php echo htmlspecialchars($supplier['phone']); ?></td>
                <td class="actions">
                    <a href="suppliers.php?action=edit&id=<?php echo $supplier['supplier_id']; ?>" class="btn btn-secondary btn-sm">Edit</a>
                    <form action="suppliers.php" method="POST" onsubmit="return confirm('Are you sure? This may fail if the supplier is linked to products.');" style="display:inline;">
                        <input type="hidden" name="supplier_id" value="<?php echo $supplier['supplier_id']; ?>">
                        <button type="submit" name="delete_supplier" class="btn btn-danger btn-sm">Delete</button>
                    </form>
                </td>
            </tr>
            <?php endforeach; ?>
        </tbody>
    </table>
</section>

<?php require 'footer.php'; ?>
