function activateTab(element) {
    var tabs = document.getElementsByClassName("tab");
    for (var i = 0; i < tabs.length; i++) {
        tabs[i].classList.remove("active");
    }
    element.classList.add("active");
}


document.addEventListener("DOMContentLoaded", function() {
    // Sidebar toggle functionality
    const toggleButton = document.getElementById('toggleButton');
    const sidebar = document.getElementById('sidebar');

    toggleButton.addEventListener('click', function() {
        sidebar.classList.toggle('collapsed');
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
});






// Function to activate the tab and filter history entries
function activateTab(tab) {
    const tabs = document.querySelectorAll('#tab'); // Get all tab buttons
    const entries = document.querySelectorAll('.history-entry'); // Get all history entries (orders, refunds)

    // Remove active class from all tabs
    tabs.forEach(t => t.classList.remove('active'));

    // Add active class to the clicked tab
    tab.classList.add('active');

    // Get the category from the clicked tab
    let category = tab.getAttribute('data-category'); // Get the category like 'all', 'orders', 'refunds'

    // Show/hide entries based on the selected tab
    entries.forEach(entry => {
        if (category === 'all') {
            entry.style.display = 'block'; // Show all entries
        } else if (entry.getAttribute('data-category') === category) {
            entry.style.display = 'block'; // Show entries matching the category (orders or refunds)
        } else {
            entry.style.display = 'none'; // Hide non-matching entries
        }
    });
}
