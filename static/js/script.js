let $ = jQuery;
let socket;

function initializeWebSocket() {
  let ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
  socket = new WebSocket(ws_scheme + '://' + window.location.host + '/message');

  socket.onopen = function (event) {
    console.log('WebSocket connection established.');
  };

  socket.onmessage = function (event) {
    const data = JSON.parse(event.data);
    // So sánh username nhận được với username hiện tại
    const isMe = data.username === username;
    const sender = isMe ? 'You' : data.username;
    const message = data.message || data.data; // phòng trường hợp server gửi khác key

    const msgClass = isMe ? 'user-message float-right text-right' : 'other-message float-left text-left';
    const messageElement = $('<li>').addClass('clearfix');
    messageElement.append($('<div>').addClass(msgClass).text(sender + ': ' + message));
    $('#messages').append(messageElement);
    const chat = document.getElementById('chat');
    chat.scrollTop = chat.scrollHeight;
    $('#chat').scrollTop($('#chat')[ 0 ].scrollHeight);
  };

  socket.onerror = function (event) {
    console.error('WebSocket error. Please rejoin the chat.');
    showJoinModal();
  };

  socket.onclose = function (event) {
    if (event.code === 1000) {
      console.log('WebSocket closed normally.');
    } else {
      console.error('WebSocket closed with error code: ' + event.code + '. Please rejoin the chat.');
      showJoinModal();
    }
  };
}

function showJoinModal() {
  $('#username-form').show();
  $('#chat').hide();
  $('#message-input').hide();
  $('#usernameModal').modal('show');
}

$('#open-modal').click(function () {
  showJoinModal();
});

function joinChat() {
  $('#username-form').hide();
  $('#chat').show();
  $('#message-input').show();
  $('#usernameModal').modal('hide');
}

$('#join').click(function () {
  initializeWebSocket();
  joinChat()
});

$('#send').click(function () {
  sendMessage();
});

$('#message').keydown(function (event) {
  if (event.key === "Enter") {
    sendMessage();
  }
});

function sendMessage() {
  const message = $('#message').val();
  if (message) {
    socket.send(JSON.stringify({ "message": message, "username": $('#usernameInput').val() }));
    $('#message').val('');
  }
}
$('#messages').append(messageElement);
const chat = document.getElementById('chat');
chat.scrollTop = chat.scrollHeight;
