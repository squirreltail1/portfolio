const tracks = document.querySelectorAll('.image_main[data-audio]');
const player = document.getElementById('player');
const currentTrack = document.getElementById('current-track');

tracks.forEach(track => {
  track.addEventListener('click', (e) => {
    const audioSrc = track.dataset.audio;
    const trackName = track.querySelector('.image_main_info').innerText;

    // Set audio and play
    player.src = audioSrc;
    player.play().catch(err => {
      console.log("Autoplay prevented:", err);
    });

    currentTrack.textContent = "Now Playing: " + trackName;

    // No e.preventDefault() here, so the link still works
  });
});
