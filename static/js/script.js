let $ = jQuery;
let socket;

function initializeWebSocket() {
  socket = new WebSocket('ws://localhost:8000/message');

  socket.onopen = function (event) {
    console.log('WebSocket connection established.');
  };

  socket.onmessage = function (event) {
    const data = JSON.parse(event.data);
    const msgClass = data.isMe ? 'user-message float-right text-right' : 'other-message float-left text-left';
    const sender = data.isMe ? 'You' : data.username;
    const message = data.data;

    // Nếu là thông báo hệ thống (ví dụ Welcome back!)
    if (sender === 'You' && (message === 'Welcome back!' || message === 'Have joined!!')) {
      const sysMsg = $('<li>').addClass('clearfix text-center text-info').text(message);
      $('#messages').append(sysMsg);
    } else {
      const messageElement = $('<li>').addClass('clearfix');
      messageElement.append($('<div>').addClass(msgClass).text(sender + ': ' + message));
      $('#messages').append(messageElement);
    }
    $('#chat').scrollTop($('#chat')[ 0 ].scrollHeight);
  };


  socket.onmessage = function (event) {
    const data = JSON.parse(event.data);
    console.log('Received message:', data);
    
    const msgClass = data.isMe ? 'user-message float-right text-right' : 'other-message float-left text-left';
    const sender = data.isMe ? 'You' : data.username;
    const message = data.data;

    // Nếu là thông báo hệ thống (ví dụ Welcome back!)
    if (sender === 'You' && (message === 'Welcome back!' || message === 'Have joined!!')) {
      const sysMsg = $('<li>').addClass('clearfix text-center text-info').text(message);
      $('#messages').append(sysMsg);
    } else {
      const messageElement = $('<li>').addClass('clearfix');
      messageElement.append($('<div>').addClass(msgClass).text(sender + ': ' + message));
      $('#messages').append(messageElement);
    }
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
