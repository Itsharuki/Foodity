

//########################################################################
//#####################  C O N T E N T  L O A D E R  #####################
//########################################################################

document.addEventListener('DOMContentLoaded', function() {
    const selectAllCheckbox = document.getElementById('select-all');
    const itemCheckboxes = document.querySelectorAll('input[name="select-item"]');
    const quantityMinusButtons = document.querySelectorAll('.quantity-button-minus');
    const quantityPlusButtons = document.querySelectorAll('.quantity-button-plus');
    const cartItemRemoveButtons = document.querySelectorAll('.cart-item-remove');
    const cartTotal = document.querySelector('.cart-total');
    
    function updateTotal() {
        let total = 0;
        document.querySelectorAll('.cart-item').forEach(item => {
            const price = parseFloat(item.querySelector('.cart-item-price').textContent.replace('₱', ''));
            const quantity = parseInt(item.querySelector('.quantity-input').value);
            total += price * quantity;
        });
        cartTotal.textContent = 'Total: ₱' + total;
    }

//#######################################################
//#####################  I T E M S  #####################
//#######################################################

    // Function to check/uncheck all items when "Select All" is clicked
    selectAllCheckbox.addEventListener('click', function() {
        itemCheckboxes.forEach((checkbox) => {
            checkbox.checked = selectAllCheckbox.checked;
        });
    });

    // Function to uncheck "Select All" when any item is unchecked
    itemCheckboxes.forEach((checkbox) => {
        checkbox.addEventListener('click', function() {
            if (!checkbox.checked) {
                selectAllCheckbox.checked = false;
            }
        });
    });

    // Function to check "Select All" if all items are checked
    itemCheckboxes.forEach((checkbox) => {
        checkbox.addEventListener('click', function() {
            if (Array.from(itemCheckboxes).every((checkbox) => checkbox.checked)) {
                selectAllCheckbox.checked = true;
            }
        });
    });

    // Function to increase quantity
    quantityPlusButtons.forEach((button) => {
        button.addEventListener('click', function() {
            const quantityInput = this.previousElementSibling;
            let quantity = parseInt(quantityInput.value);
            quantityInput.value = quantity + 1;
            updateTotal();
        });
    });

    // Function to decrease quantity
    quantityMinusButtons.forEach((button) => {
        button.addEventListener('click', function() {
            const quantityInput = this.nextElementSibling;
            let quantity = parseInt(quantityInput.value);
            if (quantity > 1) {
                quantityInput.value = quantity - 1;
                updateTotal();
            }
        });
    });

    // Function to remove cart item
    cartItemRemoveButtons.forEach((button) => {
        button.addEventListener('click', function() {
            const cartItem = this.closest('.cart-item');
            const checkbox = cartItem.querySelector('input[name="select-item"]');
            if (checkbox.checked) {
                cartItem.remove();
                updateTotal();
            } else {
                alert('Please select items to remove.');
            }
        });
    });

    // Initial total calculation
    updateTotal();
});

