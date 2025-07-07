let audioPlayer = document.querySelector('#audio_default')

function updateAudioTag(entry_id, answer_n) {
    let audioInput = document.getElementById(`fileAnswer_${entry_id}_${answer_n}`);
    let audioFile = audioInput.files[0];
    let url = URL.createObjectURL(audioFile);
    let audioPlayer = document.getElementById(`audio_${entry_id}_${answer_n}`);
    audioPlayer.src = url;
}

async function saveAudio(book_id, entry_id, answer_n) {
    let audioInput = document.getElementById(`fileAnswer_${entry_id}_${answer_n}`);
    let audioFile = audioInput.files[0];
    let buttonSave = document.getElementById(`buttonSave_${entry_id}_${answer_n}`);
    if (audioFile != null) {
        let data = new FormData()
        data.append('file', audioFile)
        data.append('entry_id', entry_id)
        data.append('book_id', book_id)
		data.append('answer_n', answer_n)

        fetch('/receive', {
            method: 'POST',
            body: data
        }).then(response => response.json())
            .then (data => {
            if (data == "File received and saved.") {
            audioInput.style.display = "none"
            buttonSave.style.display = "none"
            }
            else if (data == "File not allowed.") {
                alert("Расширение не поддерживается. Загрузите другой файл.")
            }
            else {
                alert("Произошла ошибка при загрузке файла. Пожалуйста, повторите попытку или загрузите другой файл.")
            }
        })
        .catch(err => {
            alert("Произошла ошибка при загрузке файла. Возможно, файл слишком большой.")
        });
    }
    else {
        alert('Аудио для сохранения отсутствует!')
    }
}