const commentSections = document.getElementsByClassName('commentSection')
let intervalComments = null;

function InsertComment(commentMessages, message, replace) {
	let txt = commentMessages.innerHTML
	if (replace) txt = message
	else txt += message
	commentMessages.innerHTML = txt;
}

function isElementInViewport(el) {
	if (el == null) return false;
	let rect = el.getBoundingClientRect();
	let windowHeight = (window.innerHeight || document.documentElement.clientHeight);
	let windowWidth = (window.innerWidth || document.documentElement.clientWidth);
	let vertInView = (rect.top <= windowHeight) && ((rect.top + rect.height) >= 0);
	let horInView = (rect.left <= windowWidth) && ((rect.left + rect.width) >= 0);
	return (vertInView && horInView);
}

function UpdateCommentDates() {
	if (commentSections == null || commentSections.length < 1) return null
	for (let i=0; i < commentSections.length; i++) {
		let commentSection = commentSections[i]
		let times = commentSection.getElementsByClassName('messageTime')
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
}

function UpdateComments() {
	if (commentSections == null || commentSections.length < 1) return null
	for (let i=0; i < commentSections.length; i++) {
		let commentSection = commentSections[i]
		if (isElementInViewport(commentSection) && commentSection.hasAttribute('entry_id') && commentSection.hasAttribute('student_id')) {
			let commentMessages = commentSection.getElementsByClassName('messagesList')
			if (commentMessages == null || commentMessages.length < 1) continue;
			commentMessages = commentMessages[0]
			let times = commentSection.getElementsByClassName('messageTime')
			// no messages
			if (times == null || times.length < 1 || !times[times.length-1].hasAttribute('time')) {
				let data = new FormData()
					data.append('get_comments', '1');
					data.append('entry_id', commentSection.getAttribute('entry_id'));
					data.append('student_id', commentSection.getAttribute('student_id'));
					data.append('get_type', 'all');
					fetch('/chat', {
						method: 'POST',
						body: data
					}).then(response => response.json())
							.then (data => {
								if (data != "err" && data != "") {
									InsertComment(commentMessages, data, true);
									UpdateCommentDates();
									commentMessages.scrollTop = commentMessages.scrollHeight;
								}
							})
					
			}
			else if (times != null && times.length > 0 && times[times.length-1].hasAttribute('time')) {
				let lastTime = times[times.length-1].getAttribute('time')
				let data = new FormData()
						data.append('get_comments', '1');
						data.append('entry_id', commentSection.getAttribute('entry_id'));
						data.append('student_id', commentSection.getAttribute('student_id'));
						data.append('time', lastTime);
						data.append('get_type', 'after');
						fetch('/chat', {
							method: 'POST',
							body: data
						}).then(response => response.json())
								.then (data => {
									console.log("DATA")
									console.log(data)
									if (data != "err" && data != "") {
										InsertComment(commentMessages, data, false);
										UpdateCommentDates();
										commentMessages.scrollTop = commentMessages.scrollHeight;
									}
								})
			}
		}
	}
}

function SendComment(entry_id, student_id) {
	let section = document.getElementById('section_' + entry_id + '_' + student_id)
	if (section == null) return null;
	textArea = section.getElementsByClassName('messageTextarea')
	if (textArea == null || textArea.length < 1) return null
	textArea = textArea[0]
	let comment = textArea.value;
	textArea.value = "";
	let data = new FormData()
			data.append('send_comment', '1');
			data.append('comment', comment);
			data.append('entry_id', entry_id);
			data.append('student_id', student_id);
			fetch('/chat', {
				method: 'POST',
				body: data
			}).then(response => response.json())
					.then (data => {
						if (data != "") {
						}
					})
}


intervalComments = window.setInterval(function() { 
	UpdateComments();
}, 500);