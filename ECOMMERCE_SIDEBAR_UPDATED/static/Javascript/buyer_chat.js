// Toggle Chat Window
function toggleChat() {
    var chatWindow = document.getElementById('chatWindow');
    if (chatWindow.style.display === 'none' || chatWindow.style.display === '') {
        chatWindow.style.display = 'block';
    } else {
        chatWindow.style.display = 'none';
    }
}

// Minimize Chat Window
function minimizeChat() {
    var chatWindow = document.getElementById('chatWindow');
    chatWindow.style.display = 'none';
}

// Toggle Read/Unread
function toggleReadUnread(element) {
    var user = element.closest('.user');
    if (user.classList.contains('unread')) {
        user.classList.remove('unread');
    } else {
        user.classList.add('unread');
    }
}

// Toggle Pin/Unpin
function togglePinUnpin(element) {
    var user = element.closest('.user');
    if (user.classList.contains('pinned')) {
        user.classList.remove('pinned');
    } else {
        user.classList.add('pinned');
    }
}

// Toggle Mute/Unmute
function toggleMuteUnmute(element) {
    var user = element.closest('.user');
    if (user.classList.contains('muted')) {
        user.classList.remove('muted');
    } else {
        user.classList.add('muted');
    }
}

// Delete Chat
function deleteChat(element) {
    var user = element.closest('.user');
    var chatMessageList = document.querySelector('.chat-message-list');

    // Clear all messages related to the user
    chatMessageList.innerHTML = ''; // Remove all messages from the chat message list
    user.remove(); // Remove the user from the user list

    // Optionally, reset states of user
    user.classList.remove('unread', 'pinned', 'muted'); // Reset states
}

// Send Message
function sendMessage() {
    var messageInput = document.getElementById('messageInput');
    var imageUpload = document.getElementById('imageUpload');
    var messageList = document.querySelector('.chat-message-list');
    var messageText = messageInput.value.trim();
    var imageSrc = imageUpload.files.length > 0 ? URL.createObjectURL(imageUpload.files[0]) : null;

    if (messageText !== '' || imageSrc) {
        var newMessage = document.createElement('div');
        newMessage.className = 'chat-message';

        // If there's an image, include it in the message
        newMessage.innerHTML = `
            <p><strong>You:</strong> ${messageText}</p>
            ${imageSrc ? `<img src="${imageSrc}" alt="Uploaded Image" style="max-width: 100%; border-radius: 10px; margin-top: 5px;" />` : ''}
            <span class="message-time">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
        `;

        messageList.appendChild(newMessage);
        messageInput.value = ''; // Clear the text input
        imageUpload.value = ''; // Clear the image upload input
        document.getElementById('imagePreview').style.display = 'none'; // Hide image preview
        messageList.scrollTop = messageList.scrollHeight; // Scroll to the bottom
    }
}

// Preview Image
function previewImage(event) {
    var imagePreview = document.getElementById('imagePreview');
    var previewImg = document.getElementById('previewImg');
    var file = event.target.files[0];
    var reader = new FileReader();

    reader.onload = function(e) {
        previewImg.src = e.target.result;
        imagePreview.style.display = 'block';
    }

    reader.readAsDataURL(file);
}

// Event listener for sending message on Enter key
document.getElementById('messageInput').addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        event.preventDefault(); // Prevent default behavior (new line)
        sendMessage(); // Call sendMessage function
    }
});

// Search and filter functionality for user list
document.getElementById('searchUsers').addEventListener('input', function() {
    var searchQuery = this.value.toLowerCase();
    var users = document.querySelectorAll('.user');
    users.forEach(function(user) {
        var userName = user.textContent.toLowerCase();
        if (userName.includes(searchQuery)) {
            user.style.display = 'flex';
        } else {
            user.style.display = 'none';
        }
    });
});

document.getElementById('filterUsers').addEventListener('change', function() {
    var filter = this.value;
    var users = document.querySelectorAll('.user');
    users.forEach(function(user) {
        if (filter === 'unread' && !user.classList.contains('unread')) {
            user.style.display = 'none';
        } else if (filter === 'pinned' && !user.classList.contains('pinned')) {
            user.style.display = 'none';
        } else {
            user.style.display = 'flex';
        }
    });
});
    