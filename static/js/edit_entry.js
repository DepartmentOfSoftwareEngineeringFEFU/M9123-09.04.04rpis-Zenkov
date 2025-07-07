const BlockEmbed = Quill.import('blots/block/embed');
class AudioBlot extends BlockEmbed {
  static create(url) {
    let node = super.create();
    node.setAttribute('src', url);
    node.setAttribute('controls', '');
    return node;
  }
  
  static value(node) {
    return node.getAttribute('src');
  }
}
AudioBlot.blotName = 'audio';
AudioBlot.tagName = 'audio';
Quill.register(AudioBlot);

let toolbarOptions = [
    ['bold', 'italic', 'underline'],
    [{ 'align': [] }]
]

const editor = new Quill('#editor', {
    bounds: '#editor',
    modules: {
        toolbar: toolbarOptions,
        table: true
    },
    placeholder: 'Сочините эпос...',
    theme: 'snow'
    });

function insertToEditor(book_id, type) {
    const range = editor.getSelection();
    if (type == 'video') {
        let selectVideo = document.getElementById("select-video");
        let valueVideo = selectVideo.value;
        if (valueVideo != null && valueVideo != '') {
            let url = '/static/guidebooks/' + book_id + '/files/' + valueVideo;
            editor.insertEmbed(range.index, 'video', `${url}`);
        }
    }
    else if (type == 'image') {
       let selectImage = document.getElementById("select-image");
       let valueImage = selectImage.value;
       if (valueImage != null && valueImage != '') {
           let url = '/static/guidebooks/' + book_id + '/files/' + valueImage;
           editor.insertEmbed(range.index, 'image', `${url}`);
       }
    }
	else if (type == 'audio') {
       let selectAudio = document.getElementById("select-audio");
       let valueAudio = selectAudio.value;
       if (valueAudio != null && valueAudio != '') {
		   console.log(valueAudio)
           let url = '/static/guidebooks/' + book_id + '/files/' + valueAudio;
		   console.log(url)
           editor.insertEmbed(range.index, 'audio', `${url}`);
       }
    }
}

function insertAnswer() {
    let selection = editor.getSelection(true);
    editor.insertText(selection.index, '{answer_field}');
}

function insertNotice() {
    let selection = editor.getSelection(true);
    editor.insertText(selection.index, '{notice_button}{notice_body}Текст справки{/notice_body}');
}

function setHTML() {
    let html = editor.root.innerHTML;
    document.getElementById('entry_contents').setAttribute('value', html);
    document.getElementById('form_save').submit();
}

function saveEmptyContents() {
    document.getElementById('entry_contents').setAttribute('value', "");
    document.getElementById('form_save').submit();
}

const table = editor.getModule('table');

document.querySelector('#insert-table').addEventListener('click', function() {
  table.insertTable(2, 2);
});
document.querySelector('#insert-row-above').addEventListener('click', function() {
  table.insertRowAbove();
});
document.querySelector('#insert-row-below').addEventListener('click', function() {
  table.insertRowBelow();
});
document.querySelector('#insert-column-left').addEventListener('click', function() {
  table.insertColumnLeft();
});
document.querySelector('#insert-column-right').addEventListener('click', function() {
  table.insertColumnRight();
});
document.querySelector('#delete-row').addEventListener('click', function() {
  table.deleteRow();
});
document.querySelector('#delete-column').addEventListener('click', function() {
  table.deleteColumn();
});
document.querySelector('#delete-table').addEventListener('click', function() {
  table.deleteTable();
});