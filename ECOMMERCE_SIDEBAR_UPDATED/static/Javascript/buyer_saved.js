function deleteItem(itemId) {
        const item = document.getElementById(itemId);
        if (item) {
            item.remove();
        }
    }