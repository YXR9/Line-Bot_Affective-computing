const video = document.getElementById('video');
flag = 0;
e_id = 0;
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
  console.log("Start detecting...");
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
        v_time = get_video_time();
        update_study_emotion(m_id, userID, v_time, OutputToString);
        
      } 
      
    } 

    // canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height)
    // faceapi.draw.drawDetections(canvas, resizedDetections);

  }, 5000);
});

// 利用ajax去更新

function update_study_emotion(m_id, userID, video_time, emotion) {
  
  if(emotion == "sad" && flag == 0){
    pauseVideo();
    $.ajax({
      type: 'POST',
      url:".././update_study_emotion",
      data:"m_id=" + m_id + "&userID="+ userID + "&video_time=" + video_time + "&study_emotion="+ emotion + "&flag=0",
      timeout: 360 * 1000,
      success: function(data) {
          console.log("return data is ");
          console.log(data);
          e_id = data;
      },
      error: function(jqXHR, textStatus, errorThrown) {
      }
    });
    var v_status = setInterval(check_video_status, 1000);

    flag = 1;
  }else if(flag == 0){
    $.ajax({
      type: 'POST',
      url:".././update_study_emotion",
      data:"m_id=" + m_id + "&userID="+ userID + "&video_time=" + video_time + "&study_emotion="+ emotion + "&flag=1",
      timeout: 360 * 1000,
      success: function(data) {
        console.log("return data is ");
        console.log(data);
        e_id = data;

      },
      error: function(jqXHR, textStatus, errorThrown) {
      }
    });
  }
  console.log(e_id);
  
}

function check_video_status(){
  console.log("e_id is");
  console.log(e_id);
  $.ajax({
    type: 'POST',
    url:".././check_study_video_status",
    data:"e_id=" + e_id ,
    timeout: 360 * 1000,
    success: function(data) {
      if(data == "true"){
        console.log("restart ...");
      }
    },
    error: function(jqXHR, textStatus, errorThrown) {
    }
  });
}