const popup = document.getElementById('dictPopup');
const dictionaryContent = document.getElementById('dictionaryContent');
const userbookContent = document.getElementById('userbookContent');
const dictionaryWindow = document.getElementById('windowDictionary')
const userbookWindow = document.getElementById('windowUserbook')
let showingDict = false;

function closeAllWindows() {
	dictionaryWindow.setAttribute('style', 'display:none;');
	if (userbookWindow != null) userbookWindow.setAttribute('style', 'display:none;');
}

function openDictionary() {
	if (dictionaryWindow.style.display == "none") {
		closeAllWindows();
		dictionaryWindow.setAttribute('style', 'display:auto;');
	} 
	else dictionaryWindow.setAttribute('style', 'display:none;');
}

function closeDictionary() {
	dictionaryWindow.setAttribute('style', 'display:none;');
}

function openUserbook() {
	if (userbookWindow.style.display == "none") {
		closeAllWindows();
		userbookWindow.setAttribute('style', 'display:auto;');
	} 
	else userbookWindow.setAttribute('style', 'display:none;');
}

function closeUserbook() {
	userbookWindow.setAttribute('style', 'display:none;');
}


function RemoveUserbookEntry(type, element_id) {
	// rule
	if (type == '0') {
		console.log('deleting rule...')
		let userbookItem = document.getElementById('ubook_entry_' + element_id)
		if (userbookItem != null) {
			if (userbookItem.hasAttribute('selected')) {
				userbookContent.innerHTML = '<p>Выберите элемент картотеки.</p>'
			}
			userbookItem.remove();
		}
	}
	// word
	else {
		let userbookItem = document.getElementById('ubook_word_' + element_id)
		if (userbookItem != null) {
			if (userbookItem.hasAttribute('selected')) {
				userbookContent.innerHTML = '<p>Выберите элемент картотеки.</p>'
			}
			userbookItem.remove();
		}
	}
}

function AddUserbookEntry(type, element_id, title) {
	let list = userbookWindow.getElementsByClassName('row')[0]
	let listItem = document.createElement('div');
	listItem.setAttribute('class', 'listWord');
	listItem.setAttribute('onclick', 'UpdateUserbookWindow(' + element_id + ', ' + type + ')');
	// rule
	if (type == 0) {
		listItem.setAttribute('id', 'ubook_entry_' + element_id);
		listItem.setAttribute('entry_id', element_id);
	}
	// word
	else {
		listItem.setAttribute('id', 'ubook_word_' + element_id);
		listItem.setAttribute('word_id', element_id);
	}
	listItem.innerHTML = '<p>' + title + '</p>'
	list.appendChild(listItem)
}

function UpdateUserbook(type, element_id) {
	// rule
	if (type == 0) {
		let btn = document.getElementsByClassName('rule_button_' + element_id)
		if (btn != null && btn.length > 0) {
			let btn_type = btn[0].getAttribute('button_type')
			let data = new FormData()
				data.append('update_userbook_' + btn_type, type);
				data.append('element_id', element_id);
				fetch('/userbook', {
					method: 'POST',
					body: data
				}).then(response => response.json())
						.then (data => {
							if (data != "") {
								if (btn_type == "add") {
									AddUserbookEntry(type, element_id, data)
									for (let i = 0; i < btn.length; i++) {
										btn[i].setAttribute('value', 'Удалить из картотеки')
										btn[i].setAttribute('button_type', 'remove')
									}
								}
								else {
									RemoveUserbookEntry(type, element_id)
									for (let i = 0; i < btn.length; i++) {
										btn[i].setAttribute('value', 'Добавить в картотеку')
										btn[i].setAttribute('button_type', 'add')
									}
								}
							}
							else {
								console.error('Error updating userbook!');
							}
						})
		}
	}
	// word
	else {
		let btn = document.getElementsByClassName('word_button_' + element_id)
		if (btn != null && btn.length > 0) {
			let btn_type = btn[0].getAttribute('button_type')
			let data = new FormData()
				data.append('update_userbook_' + btn_type, type);
				data.append('element_id', element_id);
				fetch('/userbook', {
					method: 'POST',
					body: data
				}).then(response => response.json())
						.then (data => {
							if (data != "") {
								if (btn_type == "add") {
									AddUserbookEntry(type, element_id, data)
									for (let i = 0; i < btn.length; i++) {
										btn[i].setAttribute('value', 'Удалить из картотеки')
										btn[i].setAttribute('button_type', 'remove')
									}
								}
								else {
									RemoveUserbookEntry(type, element_id)
									for (let i = 0; i < btn.length; i++) {
										btn[i].setAttribute('value', 'Добавить в картотеку')
										btn[i].setAttribute('button_type', 'add')
									}
								}
							}
							else {
								console.error('Error updating userbook!');
							}
						})
		}
	}
}

function elementContainsSelection(el) {
	if (el == null) return null;
    var sel = window.getSelection();
    if (sel.rangeCount > 0) {
        for (var i = 0; i < sel.rangeCount; ++i) {
            if (!el.contains(sel.getRangeAt(i).commonAncestorContainer)) {
                return false;
            }
        }
        return true;
    }
    return false;
}

function GetSelectedText() {
  return window.getSelection().toString().trim();
}

function ShowPopup(content, selectionRect) {
	if (selectionRect != null) {
		console.log("Show popup!")
		popup.style.left = selectionRect.left + 'px';
		popup.style.top = selectionRect.bottom + 'px';
		popup.style.display = 'block';
		popup.innerHTML = content;
		showingDict = true;
	}
}

function HidePopup() {
	console.log("Hide popup!")
	popup.style.display = 'none';
	popup.innerHTML = "";
	showingDict = false;
}

function DeselectAllDictionaryItems() {
	let listWords = dictionaryWindow.getElementsByClassName('listWord')
	for (let i = 0; i < listWords.length; i++) {
		listWords[i].removeAttribute('selected')
	}
}

function UpdateDictionaryWindow(word_id) {
	let listItem = document.getElementById('list_' + word_id);
	if (listItem == null) return null;
	DeselectAllDictionaryItems();
	dictionaryContent.innerHTML = '<p>Загрузка...</p>'
	listItem.setAttribute('selected', '')
	let data = new FormData()
			data.append('get_word_def_id', '1');
			data.append('word_id', word_id);
			data.append('lesson_id', lesson_id);
			fetch('/dict', {
				method: 'POST',
				body: data
			}).then(response => response.json())
					.then (data => {
						if (data != "") {
							dictionaryContent.innerHTML = data
						}
						else {
							dictionaryContent.innerHTML = '<p>Произошла ошибка при загрузке определения!</p>'
						}
					})
}

function DeselectAllUserbookItems() {
	let listWords = userbookWindow.getElementsByClassName('listWord')
	for (let i = 0; i < listWords.length; i++) {
		listWords[i].removeAttribute('selected')
	}
}

function UpdateUserbookWindow(ubook_entry_id, type) {
	// rule
	if (type == 0) {
		let listItem = document.getElementById('ubook_entry_' + ubook_entry_id);
		if (listItem == null) return null;
		DeselectAllUserbookItems();
		userbookContent.innerHTML = '<p>Загрузка...</p>'
		listItem.setAttribute('selected', '')
		let data = new FormData()
				data.append('get_entry_contents', '1');
				data.append('entry_id', ubook_entry_id);
				data.append('lesson_id', lesson_id);
				fetch('/userbook', {
					method: 'POST',
					body: data
				}).then(response => response.json())
						.then (data => {
							if (data != "") {
								userbookContent.innerHTML = data
							}
							else {
								userbookContent.innerHTML = '<p>Произошла ошибка при загрузке элемента!</p>'
							}
						})
	}
	// word
	else {
		let listItem = document.getElementById('ubook_word_' + ubook_entry_id);
		if (listItem == null) return null;
		DeselectAllUserbookItems();
		userbookContent.innerHTML = '<p>Загрузка...</p>'
		listItem.setAttribute('selected', '')
		let data = new FormData()
				data.append('get_word_def_id', '1');
				data.append('word_id', ubook_entry_id);
				data.append('lesson_id', lesson_id);
				fetch('/dict', {
					method: 'POST',
					body: data
				}).then(response => response.json())
						.then (data => {
							if (data != "") {
								userbookContent.innerHTML = data
							}
							else {
								userbookContent.innerHTML = '<p>Произошла ошибка при загрузке элемента!</p>'
							}
						})
	}
}

function ShowDefinition() {
	let selectedText = GetSelectedText()
    if (selectedText != "") {
		if (elementContainsSelection(popup) || elementContainsSelection(dictionaryWindow) || elementContainsSelection(userbookWindow)) return null;
		let selection = window.getSelection()
		let selectionRect = null;
		if (selection.rangeCount > 0) {
			let range = selection.getRangeAt(0);
			selectionRect = range.getBoundingClientRect();
		}
	    let data = new FormData()
        data.append('get_word_def', '1');
		data.append('selected', selectedText);
        data.append('lesson_id', lesson_id);
        fetch('/dict', {
			method: 'POST',
            body: data
        }).then(response => response.json())
                .then (data => {
                    if (data != "") {
						ShowPopup(data, selectionRect);
                    }
					else {
						HidePopup();
					}
                })
   }
   else {
	   HidePopup();
   }
}

function main() {
	dictionaryWindow.addEventListener("mouseleave", function(e) {
		closeDictionary();
	});
	if (userbookWindow != null) {
		userbookWindow.addEventListener("mouseleave", function(e) {
			closeUserbook();
		});
	}
	window.addEventListener("mouseup", function(e) {
	ShowDefinition();
});
}

main();

