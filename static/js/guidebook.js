let dialogChSt;
let stoppedVideos = 0;
let intervalDiag = null;
let intervalStopAutoplay = null;
let timeoutSwap = null;

function openNotice(entry_id, notice_n) {
  let button = document.getElementById(`buttonNotice_${entry_id}_${notice_n}`);
  let div = document.getElementById(`divNotice_${entry_id}_${notice_n}`);
  let isOpened = button.getAttribute('opened');
  if (isOpened == '') {
    div.style.display = 'none';
    button.removeAttribute('opened');
    button.innerHTML = 'Развернуть';
  }
  else {
    div.style.display = 'block';
    button.setAttribute('opened', '');
    button.innerHTML = 'Свернуть';
  }
}

function openChStWindow() {
  dialogChSt.style.display = "block";
}

function closeChStWindow() {
  dialogChSt.style.display = "none";
}

function prepareDiagAudio(audioPlayers) {
    for (let audioPlayer of audioPlayers) {
        let playerID = audioPlayer.id
        let splitID = playerID.split('_');
        let entry_id = parseInt(splitID[1])
        let answer_n = parseInt(splitID[2])
        let div_answer_audio = document.getElementById(`answer_audio_${entry_id}_${answer_n}`)
        let p_answer_audio = document.getElementById(`diag_message_${entry_id}_${answer_n}`)
        if (audioPlayer.getAttribute('src') == "" && answer_n > 0) {
            if (!(document.getElementById(`audio_${entry_id}_${answer_n - 1}`).getAttribute('src') != ""
            && audioPlayer.getAttribute('u') == uid)) {
                p_answer_audio.innerHTML = 'Пожалуйста подождите, когда ваш собеседник запишет ответ.'
                div_answer_audio.style.display = 'none'
            }
            else {
                p_answer_audio.innerHTML = ''
                div_answer_audio.style.display = 'block'
            }
        }
        else if (audioPlayer.getAttribute('src') == "" && answer_n == 0 &&
        audioPlayer.getAttribute('u') != uid) {
            p_answer_audio.innerHTML = 'Пожалуйста подождите, когда ваш собеседник запишет ответ.'
            div_answer_audio.style.display = 'none'
        }
        else {
                p_answer_audio.innerHTML = ''
                div_answer_audio.style.display = 'block'
        }
    }
}

function getDiagAudio(audioPlayers) {
    let shouldStop = true;
    for (let audioPlayer of audioPlayers) {
        let playerID = audioPlayer.id
        let splitID = playerID.split('_');
        let entry_id = splitID[1]
        let answer_n = splitID[2]
        let div_answer_audio = document.getElementById(`answer_audio_${entry_id}_${answer_n}`)
        let p_answer_audio = document.getElementById(`diag_message_${entry_id}_${answer_n}`)
        if (audioPlayer.getAttribute('src') == '') {
            shouldStop = false
            let data = new FormData()
            data.append('get_audio_data', '1')
            data.append('entry_id', entry_id)
            data.append('answer_n', answer_n)
            data.append('user_id', audioPlayer.getAttribute('u'))
            fetch('/receive', {
                method: 'POST',
                body: data
            }).then(response => response.json())
                .then (data => {
                    if (data != "No file.") {
                        p_answer_audio.innerHTML = ''
                        div_answer_audio.style.display = 'block'
                        audioPlayer.src = data
                        entry_id = parseInt(splitID[1])
                        answer_n = parseInt(splitID[2])
                        let nextAudioPlayer = document.getElementById(`audio_${entry_id}_${answer_n + 1}`)
                        if(nextAudioPlayer != null && nextAudioPlayer.getAttribute('u') == uid) {
                            let divNext = document.getElementById(`answer_audio_${entry_id}_${answer_n + 1}`)
                            let pNext = document.getElementById(`diag_message_${entry_id}_${answer_n + 1}`)
                            divNext.style.display = 'block'
                            pNext.innerHTML = ''
                        }
                    }
                })
        }
    }
    if (shouldStop) {
        clearInterval(intervalDiag)
    }
}

function moveUp(entry_id, answer_n) {
    answer_n = parseInt(answer_n)
    if (answer_n > 0) {
        let curInput = document.getElementById(`answer_${entry_id}_${answer_n}`)
        let curText = document.getElementById(`ordr_value_${entry_id}_${answer_n}`)
        let prevInput = document.getElementById(`answer_${entry_id}_${answer_n - 1}`)
        let prevText = document.getElementById(`ordr_value_${entry_id}_${answer_n - 1}`)

        let curValue = curInput.getAttribute('value')
        let prevValue = prevInput.getAttribute('value')

        curInput.setAttribute('value', prevValue)
        curText.innerHTML = prevValue

        prevInput.setAttribute('value', curValue)
        prevText.innerHTML = curValue

        let prevRow = document.getElementById(`row_${entry_id}_${answer_n - 1}`)
        prevRow.setAttribute('style', 'background-color: #f1f1f1;')
        timeoutSwap = setTimeout(function(){
            prevRow.removeAttribute('style')
        }, 300);
    }
}

function moveDown(entry_id, answer_n) {
    answer_n = parseInt(answer_n)
    if (document.getElementById(`answer_${entry_id}_${answer_n + 1}`) != null) {
        let curInput = document.getElementById(`answer_${entry_id}_${answer_n}`)
        let curText = document.getElementById(`ordr_value_${entry_id}_${answer_n}`)
        let nextInput = document.getElementById(`answer_${entry_id}_${answer_n + 1}`)
        let nextText = document.getElementById(`ordr_value_${entry_id}_${answer_n + 1}`)

        let curValue = curInput.getAttribute('value')
        let nextValue = nextInput.getAttribute('value')

        curInput.setAttribute('value', nextValue)
        curText.innerHTML = nextValue

        nextInput.setAttribute('value', curValue)
        nextText.innerHTML = curValue

        let nextRow = document.getElementById(`row_${entry_id}_${answer_n + 1}`)
        nextRow.setAttribute('style', 'background-color: #f1f1f1;')
        timeoutSwap = setTimeout(function(){
            nextRow.removeAttribute('style')
        }, 300);
    }
}

function stopAutoplay() {
    let iframes = document.querySelectorAll('iframe')
    for(let i = 0; i < iframes.length; i++) {
        let videoTag = iframes[i].contentDocument.body.querySelector('video');
        if (videoTag != null && videoTag.getAttribute('autoplay') != null) {
            videoTag.removeAttribute('autoplay')
            videoTag.setAttribute('preload', 'none')
            videoTag.setAttribute('muted', '')
            videoTag.pause();
            stoppedVideos += 1;
        }
    }
    if (stoppedVideos.toString() == iframes.length.toString()) {
        clearInterval(intervalStopAutoplay)
    }
}

function ScrollToID() {
	let id = location.hash.substring(1);
	if (id == '') return null
	let targetElement = document.getElementById(id)
	if (targetElement != null) {
        targetElement.scrollIntoView();
    }
	
}

function OnLoad() {
    let diagAudioPlayers = document.getElementsByClassName('audio-player-dialog')
    prepareDiagAudio(diagAudioPlayers)
    intervalDiag = window.setInterval(function() { getDiagAudio(diagAudioPlayers); }, 5000);
    ScrollUp();
    dialogChSt = document.getElementById("windowStudent");
	ScrollToID();
}

function ScrollUp() {
  window.scrollTo(window.scrollX, window.scrollY - 60);
}

window.addEventListener("hashchange", function () {
   //ScrollUp()
});

window.onload = OnLoad;

window.onclick = function(event) {
  if (event.target == dialogChSt) {
    dialogChSt.style.display = "none";
  }
}

intervalStopAutoplay = window.setInterval(function() { stopAutoplay(); }, 100);