document.addEventListener("DOMContentLoaded", function() {
    // Sidebar toggle functionality
    const toggleButton = document.getElementById('toggleButton');
    const sidebar = document.getElementById('sidebar');

    toggleButton.addEventListener('click', function() {
        sidebar.classList.toggle('collapsed');

        document.addEventListener('DOMContentLoaded', function() {
            // Select all home button elements
            const homeButtons = document.querySelectorAll('.Home_button');
            
            // Loop through each button and add the click event
            homeButtons.forEach(button => {
                button.addEventListener('click', function() {
                    // Toggle the 'active' class for the clicked button
                    this.classList.toggle('active');
                });
            });
        });
    });

    // Slider functionality
    let currentSlide = 0;

    function showSlide(index) {
        const slides = document.querySelectorAll('.slide');
        const totalSlides = slides.length;

        // Wrap around if index is out of range
        if (index >= totalSlides) currentSlide = 0;
        if (index < 0) currentSlide = totalSlides - 1;
        else currentSlide = index;

        // Update the slide position
        const slideWidth = slides[0].clientWidth;
        document.querySelector('.slides').style.transform = `translateX(-${currentSlide * slideWidth}px)`;

        // Update active button
        updateActiveButton(currentSlide);
    }

    function nextSlide() {
        currentSlide++;
        showSlide(currentSlide);
    }

    function prevSlide() {
        currentSlide--;
        showSlide(currentSlide);
    }

    function goToSlide(index) {
        showSlide(index);
    }

    function updateActiveButton(index) {
        const buttons = document.querySelectorAll('.button-holder .button');
        buttons.forEach((button, i) => {
            button.classList.toggle('active', i === index);
        });
    }

    // Initialize slider
    showSlide(currentSlide);

    // Attach event listeners for the slider controls
    document.querySelector('.next').addEventListener('click', nextSlide);
    document.querySelector('.prev').addEventListener('click', prevSlide);

    // Dropdown menu toggle for settings
    const settingsButton = document.querySelector('.settings-button');
    const settingsDropdown = document.querySelector('.settings .dropdown');

    settingsButton.addEventListener('click', function(event) {
        event.preventDefault();
        settingsDropdown.classList.toggle('show');
    });

    // Dropdown menu toggle for search filter
    const filterIconButton = document.querySelector('.icon-button');
    const filterDropdownContent = document.querySelector('.dropdown-content');

    filterIconButton.addEventListener('click', function(event) {
        event.preventDefault();
        filterDropdownContent.classList.toggle('show');
    });

    // Hide dropdowns when clicking outside
    document.addEventListener('click', function(event) {
        if (!settingsButton.contains(event.target) && !settingsDropdown.contains(event.target)) {
            settingsDropdown.classList.remove('show');
        }
        if (!filterIconButton.contains(event.target) && !filterDropdownContent.contains(event.target)) {
            filterDropdownContent.classList.remove('show');
        }
    });

    // Filter button selection
    const buttons = document.querySelectorAll('.filter-buttons button');

    buttons.forEach(button => {
        button.addEventListener('click', function() {
            buttons.forEach(btn => btn.classList.remove('selected')); // Remove the selected class from all buttons
            this.classList.add('selected'); // Add the selected class to the clicked button
            
            
            

        });
    });
});










// FOR FILTER BUTTONS (Nearby, Promotion, Best Seller, Top Rated, etc.)
document.addEventListener('DOMContentLoaded', () => {
    // Get all buttons in the filter section
    const buttons = document.querySelectorAll('.filter-buttons button');
    const products = document.querySelectorAll('.fnv_box, .confectionery_box, .cereals_box, .edible_box, .dairy_box, .bakery_box, .np_box, .sweet_box'); // Include all product boxes

    // Function to handle button click and toggle active state
    buttons.forEach(button => {
        button.addEventListener('click', function () {
            const category = this.getAttribute('data-category').toLowerCase(); // Get the selected category

            // Remove the active class from all buttons
            buttons.forEach(btn => btn.classList.remove('active'));

            // Add the active class to the clicked button
            this.classList.add('active');

            // Loop through all product boxes
            products.forEach(product => {
                // Show the products based on the selected category
                if (category === 'all') {
                    product.style.display = 'block'; // Show all products
                } else if (product.getAttribute('data-category') === category) {
                    product.style.display = 'block'; // Show the selected category
                } else {
                    product.style.display = 'none'; // Hide non-selected products
                }
            });
        });
    });
});






let selectedCategory = 'all';  // Default to showing all categories
let selectedType = 'all';      // Default to showing all types (food & beverages)

// Function to filter products based on both category and type
function filterProducts() {
    const products = document.querySelectorAll('.fnv_box, .confectionery_box, .cereals_box, .edible_box, .dairy_box, .bakery_box, .np_box, .sweet_box');
    
    products.forEach(product => {
        const productCategory = product.getAttribute('data-category');
        const productType = product.getAttribute('data-type');

        // Show the product only if it matches both selected category and type
        if ((selectedCategory === 'all' || productCategory === selectedCategory) &&
            (selectedType === 'all' || productType === selectedType)) {
            product.style.display = 'block';  // Show the product
        } else {
            product.style.display = 'none';   // Hide the product
        }
    });
}


document.querySelectorAll('.filter-buttons button[data-category]').forEach(button => {
    button.addEventListener('click', function () {
        console.log('Category button clicked:', this.getAttribute('data-category'));
        selectedCategory = this.getAttribute('data-category');
        filterProducts();
    });
});

function filterType(type) {
    console.log('Type filter clicked:', type);
    selectedType = type;
    filterProducts();
}




document.addEventListener('DOMContentLoaded', () => {
    const searchBar = document.getElementById('searchBar'); // Input element
    const productBoxes = document.querySelectorAll('.product_frame div[data-category]'); // All product boxes with a category

    if (!searchBar) {
        console.error("Search bar element (#searchBar) not found!");
        return;
    }

    if (productBoxes.length === 0) {
        console.error("No product boxes with 'data-category' found!");
        return;
    }

    // Event listener for search input
    searchBar.addEventListener('input', () => {
        const searchValue = searchBar.value.toLowerCase().trim();
        console.log("Search value:", searchValue);

        productBoxes.forEach((box) => {
            const category = box.getAttribute('data-category')?.toLowerCase();
            const type = box.getAttribute('data-type')?.toLowerCase();

            if (!category) {
                console.warn("Missing 'data-category' attribute on a product box.");
                return;
            }

            // Show/hide based on match
            if (category.includes(searchValue) || (type && type.includes(searchValue))) {
                box.style.display = 'block'; // Show matching products
            } else {
                box.style.display = 'none'; // Hide non-matching products
            }
        });
    });
});





