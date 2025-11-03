<?php
// Database connection settings
$host = 'localhost'; // or 'localhost'
$dbname = 'inventory_system'; // Make sure this is your database name
$user = 'root'; // Default XAMPP user
$pass = ''; // Default XAMPP password (empty)
$charset = 'utf8mb4';

$dsn = "mysql:host=$host;dbname=$dbname;charset=$charset";

// PDO options
$options = [
    PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION, // Throw exceptions on errors
    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,       // Fetch as associative array
    PDO::ATTR_EMULATE_PREPARES   => false,                  // Use "real" prepared statements
];

try {
    // This is the line that creates the $pdo variable (changed from $db)
    $pdo = new PDO($dsn, $user, $pass, $options);
} catch (\PDOException $e) {
    // If connection fails, stop everything and show the error
    throw new \PDOException($e->getMessage(), (int)$e->getCode());
}
?>

