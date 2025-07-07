function GetActiveTrack(video) {
	let textTracks = video.textTracks; 
	let targetTrack = null;
    for (let i = 0; i < textTracks.length; i++) {
      if (textTracks[i].kind === 'subtitles' && textTracks[i].mode == 'showing') {
        targetTrack = textTracks[i];
        break;
      }
    }
	return targetTrack
}

function HideSubtitles(subtitles) {
	subtitles.innerHTML = '';
	subtitles.style.visibility = 'hidden';
}

function ShowSubtitles(subtitles, subtitlesText) {
	subtitles.innerHTML = subtitlesText;
	subtitles.style.visibility = 'visible';
}

function PrepareVideos() {
	let videoplayers = document.getElementsByClassName('videoplayer');
	for (let i = 0; i < videoplayers.length; i++) {
		let video = videoplayers[i].getElementsByTagName('video')[0];
		let subtitles = videoplayers[i].getElementsByClassName('subtitles')[0];
		video.textTracks.addEventListener('change', (event) => {
			if (GetActiveTrack(video) == null) HideSubtitles(subtitles)
		});
		for (let j = 0; j < video.textTracks.length; j++) {
			video.textTracks[j].oncuechange = () => {
				let activeCues = video.textTracks[j].activeCues;
				if (activeCues && activeCues.length > 0) {
					let currentCue = activeCues[0];
					ShowSubtitles(subtitles, currentCue.text)
					currentCue.addEventListener('exit', (event) => {
						HideSubtitles(subtitles)
					});
				}
			};
		}
	}
}