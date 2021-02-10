const video = document.getElementById('video');
console.log(video);

var tempemotion = 'non';

Promise.all([
  faceapi.nets.tinyFaceDetector.loadFromUri('https://project-emotion.herokuapp.com/static/models'),
  faceapi.nets.faceLandmark68Net.loadFromUri('https://project-emotion.herokuapp.com/static/models'),
  faceapi.nets.faceRecognitionNet.loadFromUri('https://project-emotion.herokuapp.com/static/models'),
  faceapi.nets.faceExpressionNet.loadFromUri('https://project-emotion.herokuapp.com/static/models')
]).then(startVideo)

function startVideo() {
  navigator.getUserMedia(
    { video: {} },
    stream => video.srcObject = stream,
    err => console.error(err)
  )
}

video.addEventListener('play', () => {

  // const canvas = faceapi.createCanvasFromMedia(video)
  // document.body.append(canvas)

  const displaySize = { width: video.width, height: video.height }
  // faceapi.matchDimensions(canvas, displaySize)

  setInterval(async () => {
    
    const detections = await faceapi.detectAllFaces(video, new faceapi.TinyFaceDetectorOptions()).withFaceLandmarks().withFaceExpressions()
    const resizedDetections = faceapi.resizeResults(detections, displaySize)

    if (detections[detections.length-1] != undefined) {

      let Datalist = detections[detections.length-1];
      var Emotion = Datalist.expressions;
      var Outputemotion = Object.entries(Emotion).sort((a,b) => b[1]-a[1]).map(el=>el[0]).slice(0,1);
      var OutputToString = Outputemotion.toString();
      
      if(OutputToString != tempemotion) {
      
        tempemotion = OutputToString;
        console.log(OutputToString);  //OutputToString為紀錄的情緒，情緒有改變才會更換成下一個情緒狀態

      } 
      
    } 

    // canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height)
    // faceapi.draw.drawDetections(canvas, resizedDetections);

  }, 1000);
});

