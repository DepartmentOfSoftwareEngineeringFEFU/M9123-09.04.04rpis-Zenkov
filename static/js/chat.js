const chatContent = document.getElementById('messagesList');
const chatInput = document.getElementById('chatInput');
const chatTextarea = document.getElementById('chatTextarea');
const chatWindow = document.getElementById('chatWindow');
let chatOpened = false;
let currentRoom = -1;
let intervalChat = null;

function UpdateMessages() {
	if (currentRoom < 0 || !chatOpened) return null;
	let times = chatContent.getElementsByClassName('messageTime')
	if (times == null || times.length < 1 || !times[times.length-1].hasAttribute('time')) return null
	let lastTime = times[times.length-1].getAttribute('time')
	console.log(lastTime)
	let data = new FormData()
		data.append('get_messages', '1');
		data.append('group_id', currentRoom);
		data.append('get_type', 'after');
		data.append('time', lastTime)
		fetch('/chat', {
			method: 'POST',
			body: data
		}).then(response => response.json())
				.then (data => {
					if (data != "") {
						InsertMessage(data);
						UpdateChatDates();
						chatContent.scrollTop = chatContent.scrollHeight;
					}
				})
}

function UpdateChatDates() {
	let times = chatContent.getElementsByClassName('messageTime')
	for (let i = 0; i < times.length; i++) {
		if (!times[i].hasAttribute('prepared')) {
			let time = Number(times[i].getAttribute('time'))
			if (time != NaN) {
				time *= 1000;
				let date = new Date(time);
				times[i].innerHTML = date.toLocaleString();
				times[i].setAttribute('prepared', '')
			}
		}
	}
}

function InsertMessageBefore(message) {
	let txt = chatContent.innerHTML
	if (txt == '<p>Нет сообщений.</p>') txt = message
	else txt = message + txt
	chatContent.innerHTML = txt;
}

function InsertMessage(message) {
	let txt = chatContent.innerHTML
	if (txt == '<p>Нет сообщений.</p>') txt = message
	else txt += message
	chatContent.innerHTML = txt;
}

function SendMessage() {
	if (chatTextarea.value == '') return null;
	let message = chatTextarea.value;
	chatTextarea.value = "";
	let data = new FormData()
			data.append('send_message', '1');
			data.append('message', message);
			data.append('group_id', currentRoom);
			fetch('/chat', {
				method: 'POST',
				body: data
			}).then(response => response.json())
					.then (data => {
						if (data != "") {
							//InsertMessage(data);
							//UpdateChatDates();
						}
					})
}

function OpenChat() {
	if (chatWindow.style.display == "none") {
		chatWindow.setAttribute('style', 'display:auto;');
		chatOpened = true;
	} 
	else {
		chatWindow.setAttribute('style', 'display:none;');
		chatOpened = false;
	}
}

function HideChatInput() {
	chatInput.setAttribute('style', 'display:none;');
}

function ShowChatInput() {
	chatInput.setAttribute('style', 'display:auto;');
}

function DeselectAllChatRooms() {
	let listRooms = chatWindow.getElementsByClassName('listWord')
	for (let i = 0; i < listRooms.length; i++) {
		listRooms[i].removeAttribute('selected')
	}
}

function LoadOlderMessages() {
	if (currentRoom < 0 || !chatOpened) return null;
	let times = chatContent.getElementsByClassName('messageTime')
	if (times == null || times.length < 1 || !times[0].hasAttribute('time')) return null
	let firstTime = times[0].getAttribute('time')
	let lastHeight = chatContent.scrollHeight
	let data = new FormData()
		data.append('get_messages', '1');
		data.append('group_id', currentRoom);
		data.append('get_type', 'before');
		data.append('time', firstTime)
		fetch('/chat', {
			method: 'POST',
			body: data
		}).then(response => response.json())
				.then (data => {
					if (data != "") {
						InsertMessageBefore(data);
						UpdateChatDates();
						chatContent.scrollTop = chatContent.scrollHeight - lastHeight
					}
				})
}

function UpdateChatWindow(group_id) {
	let listItem = document.getElementById('chat_' + group_id);
	if (listItem == null) return null;
	currentRoom = group_id
	HideChatInput();
	DeselectAllChatRooms();
	chatContent.innerHTML = '<p>Загрузка...</p>'
	listItem.setAttribute('selected', '')
	let data = new FormData()
			data.append('get_messages', '1');
			data.append('group_id', group_id);
			data.append('get_type', 'last')
			fetch('/chat', {
				method: 'POST',
				body: data
			}).then(response => response.json())
					.then (data => {
						if (data != "err") {
							chatContent.innerHTML = data;
							UpdateChatDates();
							ShowChatInput();
							chatContent.scrollTop = chatContent.scrollHeight;
						}
						else {
							chatContent.innerHTML = '<p>Произошла ошибка при загрузке сообщений!</p>'
						}
					})
}


intervalChat = window.setInterval(function() { 
	if (chatContent != null && chatContent.scrollTop === 0) {
		LoadOlderMessages()
	}
	if (chatContent != null) UpdateMessages();
}, 500);