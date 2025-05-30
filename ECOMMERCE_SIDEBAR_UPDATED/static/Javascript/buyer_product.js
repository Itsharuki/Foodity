function toggleDetails(productId) {
    var productContainer = document.getElementById(productId + '-container');
    var productDetails = document.getElementById(productId + '-details');
    var allProducts = document.querySelectorAll('.product');

    allProducts.forEach(function(product) {
        var details = product.querySelector('.product-details');
        if (product !== productContainer) {
            product.classList.remove('zoomed');
            details.style.display = 'none';
        }
    });

    if (productContainer.classList.contains('zoomed')) {
        productContainer.classList.remove('zoomed');
        productDetails.style.display = 'none';
    } else {
        productContainer.classList.add('zoomed');
        productDetails.style.display = 'block';
    }
}

document.addEventListener('keydown', function(event) {
    const products = document.querySelectorAll('.product');
    let currentIndex = -1;

    // Find the currently focused product
    products.forEach((product, index) => {
        if (document.activeElement === product) {
            currentIndex = index;
        }
    });

    // Move focus with arrow keys
    if (event.key === 'ArrowRight' && currentIndex < products.length - 1) {
        products[currentIndex + 1].focus();
    } else if (event.key === 'ArrowLeft' && currentIndex > 0) {
        products[currentIndex - 1].focus();
    }
});