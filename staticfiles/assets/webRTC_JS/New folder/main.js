
/////////////////////////////////////////////
/////////////////////////////////////////////
var usernameInput = document.querySelector("#username22");
var joinBtn = document.querySelector("#join_btn");


var localVideo = document.querySelector("#gum");
var btnToggleAudio = document.querySelector("#btn-toggle-audio");
var btnToggleVideo = document.querySelector("#btn-toggle-Video");

var username2;
var webSocket;

var mapPeers ={};
const constraints2  ={
  'video': true,
  'audio': true
}
var userMedia = navigator.mediaDevices.getUserMedia(constraints2).then(stream =>{
  localSream= stream;
  localVideo.srcObject = localSream;
  localVideo.muted =true;

  var audioTracks = stream.getAudioTracks();
  var videoTracks = stream.getVideoTracks();

  audioTracks[0].enabled=true;
  videoTracks[0].enabled=true;
  btnToggleAudio.addEventListener("click", () =>{
    audioTracks[0].enabled= !audioTracks[0].enabled;
    if (audioTracks[0].enabled){
      btnToggleAudio.innerHTML ="Audio Mute";
    }

    btnToggleAudio.innerHTML ="Audio Unmute";

  });


  btnToggleVideo.addEventListener("click", () =>{
    videoTracks[0].enabled= !videoTracks[0].enabled;
    if (videoTracks[0].enabled){
      btnToggleVideo.innerHTML ="Video off";
    }

    btnToggleVideo.innerHTML ="Video On";

  });
})
function webSocketOnMessage(event){
	var parseData = JSON.parse(event.data);
	var peerUsername =parseData["peer"];
	var action =parseData["action"];
  if ( username2 = peerUsername){
    return;

  }
  var ceiver_channel_name = parseData['message']['receiver_channel_name'];
  if (action =='new-peer'){
    createofferer(peerUsername, ceiver_channel_name);
    return;
  }  
  if (action =='new-offer'){
    var offer = parseData['message']['sdp']
    createAnswerer(offer, peerUsername, ceiver_channel_name);
    return;
  }  
  if (action =='new-answer'){
    var answer = parseData['message']['sdp']
    var peer = mapPeers[peerUsername][0];
    peer.setLocalDescription(answer)
    return;
  }
}
joinBtn.addEventListener('click',()=>{
	
	username2 =usernameInput.value;
	console.log('username: ', username2)
	if (username2 ==""){
		return;
		
	}
	usernameInput.value ="";
	usernameInput.disabled =true;
	usernameInput.style.visibility ="Hidden";
	
	joinBtn.disabled =true;
	joinBtn.style.visibility ="Hidden";
	
	
    var labelUsername = document.querySelector("#label_username");
	labelUsername.innerHTML =username2;
	
	var loc =window.location;
	var wsstart = "ws://";
	if (loc.protocol == "https:"){
	   var wsstart = "wss://";
	}
	var endPoint = wsstart + loc.host + loc.pathname;
	
	console.log('endPoint: ', endPoint)
	
  webSocket = new WebSocket(endPoint);
	
	
	webSocket.addEventListener('open', ()=>{
		console.log('connection open')
    
    //sendSignal('new-peer', {});
	});

	webSocket.addEventListener('message', webSocketOnMessage);
  
	webSocket.addEventListener('close', ()=>{
		console.log('connection closed ')
		
	});
	webSocket.addEventListener('error', ()=>{
		console.log('error occurred ')
		
	});
})

var localSream = new MediaStream();

const constraints  ={
  'video': true,
  'audio': true
}




function sendSignal(action, message){


  var jsonStr =JSON.stringify({
    'peer': username2,
    'action': action,
    'message': message,
  });
  webSocket.send(jsonStr);

}

function createofferer(peerUsername, receiver_channel_name){

  var peer = RTCPeerConnection(null);
  addLocalTrack(peer);
  var dc = peer.createDataChannel('channel');
  dc.addEventListener('open', ()=>{

    console.log('connection open');
  })
  dc.addEventListener('open', dcOnMessage);
  var remoteVideo = createVideo(peerUsername);
  setOnTrack(peer, remoteVideo)
  mapPeers[peerUsername]= [peer, dc];
  peer.addEventListener('iceconnectionstatechange', () =>{
    var iceconnectionState = peer.iceconnectionState;

    if (iceconnectionState === 'failed' || iceconnectionState === 'disconnected' || iceconnectionState === 'closed'){
      delete mapPeers[peerUsername];
      if (iceconnectionState != 'closed'){
        peer.close();
      }
      removeVideo(remoteVideo);

    }
  });
function  createAnswerer(offer, peerUsername, receiver_channel_name){

    var peer = RTCPeerConnection(null);
    addLocalTrack(peer);
    var remoteVideo = createVideo(peerUsername);
    setOnTrack(peer, remoteVideo)

    peer.addEventListener('datachannel', () =>{
      peer.dc = e.channel;
      
      peer.dc.addEventListener('open', ()=>{

        console.log('connection open');
      })
      peer.dc.addEventListener('open', dcOnMessage);
      
      mapPeers[peerUsername]= [peer, peer.dc];
    
    });
    peer.addEventListener('iceconnectionstatechange', () =>{
      var iceconnectionState = peer.iceconnectionState;
  
      if (iceconnectionState === 'failed' || iceconnectionState === 'disconnected' || iceconnectionState === 'closed'){
        delete mapPeers[peerUsername];
        if (iceconnectionState != 'closed'){
          peer.close();
        }
        removeVideo(remoteVideo);
  
      }
    });
  }
  peer.addEventListener('icecandidate', (event) =>{

    if (event.candidate){
      console.log("new ice candidate", JSON.stringify(peer.localDescription));
      return;
      
    }
      sendSignal('new-answer',{
          'sdp': peer.localDescription,
          'receiver_channel_name': receiver_channel_name
      });
  });
  peer.setRemoteDescription(offer).then(() =>{
     console.log("remote description set succefully for %s.", peerUsername)

     return peer.createAnswerer();
  }).then(a =>{
    console.log("Answer created")

    peer.setLocalDescription(a);
 })

}

function addLocalTrack(peer){

localSream.addTrack().forEach(track =>{
  peer.addTrack(track, localSream);
});
   return;
} 

var messageList = document.querySelector('#message-list');
function dcOnMessage(event){
  var message = event.data;

  var li = document.createElement('li');
  li.appendChild(document.createTextNode(message));
  messageList.appendChild(li);

}

function createVideo(peerUsername){
  var videoContainer = document.querySelector('#video-container');
  var remoteVideo = document.createElement('video');
  remoteVideo.id = peerUsername + '-video';
  remoteVideo.autoplay =true;
  remoteVideo.playsInline =true;

  
  var videoWrapper = document.createElement('div');
  videoContainer.appendChild(videoWrapper);
  videoWrapper.appendChild(remoteVideo);

  return remoteVideo;

}

function setOnTrack(peer, remoteVideo){
   var remoteStream = new MediaStream();
   remoteVideo.srcObject =remoteStream;

   peer.addEventListener('track', async(event) =>{
     remoteStream.addTrack(event.track, remoteStream);
   })

}

function  removeVideo(video){
  var videoWrapper = video.parentNode;
  videoWrapper.parentNode.removeChild(videoWrapper);

}


