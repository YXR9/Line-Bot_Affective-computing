// var tag = document.createElement('script');
// tag.src = 'https://www.youtube.com/iframe_api';
// var firstScriptTag = document.getElementsByTagName('script')[0];
// firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

var player;
function onYouTubeIframeAPIReady() {
    player = new YT.Player('course_video');
    console.log("reday");
}

var myVar = setInterval(get_time, 5000);

function get_time() {
    var time = player.getCurrentTime();
    console.log(time);s
}