<?php
// api/fetch_product.php
require_once('db.php');

if (!isset($_GET['id']) || empty($_GET['id'])) {
    echo json_encode(['error' => 'No product ID provided.']);
    exit;
}

$product_id = $_GET['id'];

try {
    // This query MUST fetch cost_price and sale_price
    $stmt = $pdo->prepare("SELECT product_id, name, sale_price, cost_price, quantity_in_stock FROM products WHERE product_id = ?");
    $stmt->execute([$product_id]);
    $product = $stmt->fetch(PDO::FETCH_ASSOC);

    if ($product) {
        echo json_encode($product);
    } else {
        echo json_encode(['error' => 'Product not found.']);
    }

} catch (PDOException $e) {
    echo json_encode(['error' => 'Database error: ' . $e->getMessage()]);
}
?>

