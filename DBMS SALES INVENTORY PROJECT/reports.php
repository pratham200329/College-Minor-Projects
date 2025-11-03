<?php
require 'db.php';

// --- Fetch Profit/Loss Data ---
// This query now calculates ACTUAL profit based on historical cost
$sql = "
    SELECT 
        p.name,
        SUM(si.quantity) as total_sold,
        SUM(si.quantity * si.price_per_unit) as total_revenue,
        SUM(si.quantity * (si.price_per_unit - si.cost_per_unit)) as actual_profit
    FROM 
        sale_items si
    JOIN 
        products p ON si.product_id = p.product_id
    GROUP BY 
        p.product_id, p.name
    ORDER BY 
        actual_profit DESC
";
$profit_data = $pdo->query($sql)->fetchAll(PDO::FETCH_ASSOC);

$total_revenue = 0;
$total_profit = 0;

// --- Fetch Low Stock Data ---
$sql_low_stock = "
    SELECT name, sku, quantity_in_stock, low_stock_threshold 
    FROM products 
    WHERE quantity_in_stock <= low_stock_threshold
    ORDER BY quantity_in_stock ASC
";
$low_stock_items = $pdo->query($sql_low_stock)->fetchAll(PDO::FETCH_ASSOC);


require 'header.php';
?>

<header>
    <h1>Reports</h1>
</header>

<!-- Profit/Loss Report -->
<section class="container">
    <h2>Profit/Loss Report (by Product)</h2>
    <div class="table-responsive">
        <table class="data-table">
            <thead>
                <tr>
                    <th>Product</th>
                    <th>Total Units Sold</th>
                    <th>Total Revenue</th>
                    <th>Actual Profit</th>
                </tr>
            </thead>
            <tbody>
                <?php if (empty($profit_data)): ?>
                    <tr>
                        <td colspan="4">No sales data found to generate a profit report.</td>
                    </tr>
                <?php else: ?>
                    <?php foreach ($profit_data as $row): ?>
                        <?php 
                            $total_revenue += $row['total_revenue'];
                            $total_profit += $row['actual_profit'];
                        ?>
                        <tr>
                            <td><?php echo htmlspecialchars($row['name']); ?></td>
                            <td><?php echo $row['total_sold']; ?></td>
                            <td>$<?php echo number_format($row['total_revenue'], 2); ?></td>
                            <td class="<?php echo $row['actual_profit'] >= 0 ? 'text-success' : 'text-danger'; ?>">
                                $<?php echo number_format($row['actual_profit'], 2); ?>
                            </td>
                        </tr>
                    <?php endforeach; ?>
                <?php endif; ?>
            </tbody>
            <tfoot>
                <tr>
                    <th colspan="2" style="text-align:right;">Total:</th>
                    <th>$<?php echo number_format($total_revenue, 2); ?></th>
                    <th>$<?php echo number_format($total_profit, 2); ?></th>
                </tr>
            </tfoot>
        </table>
    </div>
</section>

<!-- Profit/Revenue Chart -->
<section class="container">
    <h2>Revenue vs. Profit Chart</h2>
    <div class="chart-container">
        <canvas id="profitChart"></canvas>
    </div>
</section>

<!-- Low Stock Alerts -->
<section class="container">
    <h2>Low Stock Alerts</h2>
    <div class="table-responsive">
        <?php if (empty($low_stock_items)): ?>
            <p>No items are currently low on stock. Well done!</p>
        <?php else: ?>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Product</th>
                        <th>SKU</th>
                        <th>Quantity in Stock</th>
                        <th>Low Stock Threshold</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($low_stock_items as $item): ?>
                    <tr class="low-stock-alert">
                        <td><?php echo htmlspecialchars($item['name']); ?></td>
                        <td><?php echo htmlspecialchars($item['sku']); ?></td>
                        <td><?php echo $item['quantity_in_stock']; ?></td>
                        <td><?php echo $item['low_stock_threshold']; ?></td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        <?php endif; ?>
    </div>
</section>

<!-- Chart.js Library -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
document.addEventListener('DOMContentLoaded', function() {
    // --- Profit Chart ---
    const ctx = document.getElementById('profitChart').getContext('2d');
    
    const labels = [];
    const revenueData = [];
    const profitData = [];

    <?php
    foreach ($profit_data as $row) {
        echo "labels.push(" . json_encode($row['name']) . ");\n";
        echo "revenueData.push(" . $row['total_revenue'] . ");\n";
        echo "profitData.push(" . $row['actual_profit'] . ");\n"; // Use actual_profit
    }
    ?>

    const profitChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Total Revenue',
                    data: revenueData,
                    backgroundColor: 'rgba(54, 162, 235, 0.6)', // Blue
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Actual Profit', // Changed from 'Estimated'
                    data: profitData,
                    backgroundColor: 'rgba(75, 192, 192, 0.6)', // Green
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + value;
                        }
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(context.parsed.y);
                            }
                            return label;
                        }
                    }
                }
            }
        }
    });
});
</script>

<?php require 'footer.php'; ?>

