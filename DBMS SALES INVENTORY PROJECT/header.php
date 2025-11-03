<?php
// Function to check if a page is active
function is_active($page_name) {
    if (basename($_SERVER['PHP_SELF']) == $page_name) {
        return 'active';
    }
    return '';
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo isset($page_title) ? $page_title : 'Inventory System'; ?></title>
    <!-- 
      FIX: Added a version number (v=1.7) to the CSS link. 
      This forces the browser to re-download the file and fixes style caching issues.
    -->
    <link rel="stylesheet" href="style.css?v=1.7">
    <script src="https://unpkg.com/feather-icons"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <aside class="sidebar">
        <div class="sidebar-header">
            Inventory
        </div>
        <ul>
            <li class="<?php echo is_active('index.php'); ?>">
                <a href="index.php"><i data-feather="grid"></i> Dashboard</a>
            </li>
            <li class="<?php echo is_active('products.php'); ?>">
                <a href="products.php"><i data-feather="package"></i> Products</a>
            </li>
            <li class="<?php echo is_active('suppliers.php'); ?>">
                <a href="suppliers.php"><i data-feather="truck"></i> Suppliers</a>
            </li>
            <li class="<?php echo is_active('customers.php'); ?>">
                <a href="customers.php"><i data-feather="users"></i> Customers</a>
            </li>
            <li class="<?php echo is_active('sales.php'); ?>">
                <a href="sales.php"><i data-feather="shopping-cart"></i> Record Sale</a>
            </li>
            <li class="<?php echo is_active('purchases.php'); ?>">
                <a href="purchases.php"><i data-feather="archive"></i> Record Purchase</a>
            </li>
            <li class="<?php echo is_active('reports.php'); ?>">
                <a href="reports.php"><i data-feather="bar-chart-2"></i> Reports</a>
            </li>
        </ul>
    </aside>
    <main class="main-content">

