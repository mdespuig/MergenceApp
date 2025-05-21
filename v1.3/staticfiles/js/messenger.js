const senderUsername = "{{ current_user.username|escapejs }}";
const receiverUsername = "{{ chat_partner.username|escapejs }}";

const roomName = [senderUsername, receiverUsername].sort().join('_');

const chatSocket = new WebSocket(
    (window.location.protocol === 'https:' ? 'wss://' : 'ws://') + window.location.host + '/ws/chat/' + roomName + '/'
);

chatSocket.onopen = function () {
    console.log('WebSocket connection established.');
};

chatSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    const chatLog = document.getElementById('chat-log');
    const messageElement = document.createElement('div');
    messageElement.innerHTML = `<b>${data.sender}:</b> ${data.message} <span class="timestamp">${data.timestamp}</span>`;
    chatLog.appendChild(messageElement);
    chatLog.scrollTop = chatLog.scrollHeight;
};

chatSocket.onclose = function (e) {
    console.error('Chat socket closed unexpectedly.');
};

document.getElementById('chat-message-send').onclick = function () {
    const input = document.getElementById('chat-message-input');
    const message = input.value.trim();
    if (message) {
        chatSocket.send(JSON.stringify({
            'message': message,
            'sender': senderUsername,
            'receiver': receiverUsername
        }));
        input.value = '';
    }
};

document.getElementById('chat-message-input').addEventListener('keyup', function (e) {
    if (e.key === 'Enter') {
        document.getElementById('chat-message-send').click();
    }
});