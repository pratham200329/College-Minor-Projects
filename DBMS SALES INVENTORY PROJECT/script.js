document.addEventListener("DOMContentLoaded", function () {
    // Get the current page path
    const currentPage = window.location.pathname.split("/").pop();
    
    // Set 'active' class on the correct nav link
    const navLinks = document.querySelectorAll(".sidebar nav ul li a");
    navLinks.forEach(link => {
        if (link.getAttribute("href") === currentPage) {
            link.classList.add("active");
        }
    });

    // --- Sales & Purchase Form Logic ---
    const itemListContainer = document.getElementById("item-list-container");
    const addItemBtn = document.getElementById("add-item-btn");
    const totalAmountEl = document.getElementById("total-amount");
    const itemTemplate = document.getElementById("item-template");

    if (addItemBtn && itemListContainer && itemTemplate) {
        addItemBtn.addEventListener("click", () => {
            // Clone the template row
            const newRow = itemTemplate.content.cloneNode(true);
            itemListContainer.appendChild(newRow);
            // Re-attach event listeners to all rows
            attachRowListeners();
        });

        // Function to attach listeners to all rows (including new ones)
        function attachRowListeners() {
            itemListContainer.querySelectorAll(".item-row").forEach(row => {
                const removeBtn = row.querySelector(".remove-item-btn");
                const quantityInput = row.querySelector(".quantity-input");
                const priceInput = row.querySelector(".price-input");
                const productSelect = row.querySelector(".product-select");

                // Remove button
                if (removeBtn && !removeBtn.dataset.listenerAttached) {
                    removeBtn.addEventListener("click", () => {
                        row.remove();
                        updateTotal();
                    });
                    removeBtn.dataset.listenerAttached = true;
                }

                // Update total on quantity or price change
                if (quantityInput && !quantityInput.dataset.listenerAttached) {
                    quantityInput.addEventListener("input", updateTotal);
                    quantityInput.dataset.listenerAttached = true;
                }
                
                if (priceInput && !priceInput.dataset.listenerAttached) {
                    priceInput.addEventListener("input", updateTotal);
                    priceInput.dataset.listenerAttached = true;
                }

                // Special logic for sales page: update price when product is selected
                if (productSelect && !productSelect.dataset.listenerAttached) {
                    productSelect.addEventListener("change", (e) => {
                        const selectedOption = e.target.options[e.target.selectedIndex];
                        const price = selectedOption.dataset.price || 0;
                        const rowPriceInput = row.querySelector(".price-input");
                        if(rowPriceInput) {
                            rowPriceInput.value = parseFloat(price).toFixed(2);
                            rowPriceInput.readOnly = true; // Price is set by product
                        }
                        updateTotal();
                    });
                    productSelect.dataset.listenerAttached = true;
                }
            });
        }

        // Function to calculate and update the grand total
        function updateTotal() {
            let total = 0;
            itemListContainer.querySelectorAll(".item-row").forEach(row => {
                const quantity = parseFloat(row.querySelector(".quantity-input").value) || 0;
                const price = parseFloat(row.querySelector(".price-input").value) || 0;
                const lineTotal = quantity * price;
                
                // Update line total (if element exists)
                const lineTotalEl = row.querySelector(".line-total");
                if (lineTotalEl) {
                    lineTotalEl.textContent = lineTotal.toFixed(2);
                }
                
                total += lineTotal;
            });

            if (totalAmountEl) {
                totalAmountEl.textContent = total.toFixed(2);
                
                // Also update hidden total input if it exists
                const hiddenTotalInput = document.getElementById("total_amount_hidden");
                if(hiddenTotalInput) {
                    hiddenTotalInput.value = total.toFixed(2);
                }
            }
        }

        // Initial setup
        attachRowListeners();
        updateTotal();
    }
});
