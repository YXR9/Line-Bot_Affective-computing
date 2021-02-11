// var tag = document.createElement('script');
// tag.id = 'nFPuGm0kihs';
// tag.src = 'https://www.youtube.com/iframe_api';
// var firstScriptTag = document.getElementsByTagName('script')[0];
// firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

// var player;
// function onYouTubeIframeAPIReady() {
//     player = new YT.Player('course_video');
// }
var player;
function onYouTubeIframeAPIReady() {
  player = new YT.Player('course_video', {
    height: '390',
    width: '640',
    videoId: 'nFPuGm0kihs',
    events: {
      'onReady': get_video_time
    }
  });
}

// var myVar = setInterval(get_video_time, 5000);

function get_video_time() {
    var time = player.getCurrentTime();
    return time.toFixed(1);
    console.log(time.toFixed(1));
}

function pauseVideo(){
    player.pauseVideo();
    console.log("pause");
}

function stopVideo() {
    player.stopVideo();
}