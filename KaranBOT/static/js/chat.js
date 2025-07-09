document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const chatMessageInput = document.getElementById('chat-message');
    const chatLog = document.getElementById('chat-log');

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const userMessage = chatMessageInput.value.trim();
        if (!userMessage) return;

        // Display user message
        appendMessage('You', userMessage);
        chatMessageInput.value = '';

        // Send message to the server and get response
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: userMessage }),
            });

            const data = await response.json();
            const botMessage = data.response;

            // Display bot response
            appendMessage('KaranBOT', botMessage);

        } catch (error) {
            console.error('Error:', error);
            appendMessage('Error', 'Sorry, something went wrong.');
        }
    });

    function appendMessage(sender, message) {
        const messageContainer = document.createElement('div');
        messageContainer.classList.add('chat-message', sender === 'You' ? 'user-message' : 'bot-message');

        const senderElement = document.createElement('div');
        senderElement.classList.add('message-sender');
        senderElement.textContent = sender;

        const bubbleElement = document.createElement('div');
        bubbleElement.classList.add('message-bubble');
        bubbleElement.textContent = message;

        messageContainer.appendChild(senderElement);
        messageContainer.appendChild(bubbleElement);
        chatLog.appendChild(messageContainer);

        chatLog.scrollTop = chatLog.scrollHeight; // Auto-scroll to the bottom
    }
});
