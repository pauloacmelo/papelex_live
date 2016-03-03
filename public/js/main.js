function toggleFullScreen() {
  if (!document.fullscreenElement &&    // alternative standard method
      !document.mozFullScreenElement && !document.webkitFullscreenElement && !document.msFullscreenElement ) {  // current working methods
    // Check if there's a FullScreenWrapper Element
    if(!document.getElementById('FullScreeenWrapper')){
      var wrapperDiv = document.createElement("div");
      wrapperDiv.id = "FullScreeenWrapper";
      wrapperDiv.style.boxShadow = '0px 0px 0px';
      wrapperDiv.style.mozBoxShadow = '0px 0px 0px';
      wrapperDiv.style.webkitBoxShadow = '0px 0px 0px';
      wrapperDiv.style.width = '100%';
      wrapperDiv.style.height = '100%';
      wrapperDiv.style.padding = '0px';
      while (document.body.firstChild)
          wrapperDiv.appendChild(document.body.firstChild);
      document.body.appendChild(wrapperDiv);
    }

    elem = document.getElementById('FullScreeenWrapper') || document.body;
    if (elem.requestFullscreen) {
      elem.requestFullscreen();
    } else if (elem.msRequestFullscreen) {
      elem.msRequestFullscreen();
    } else if (elem.mozRequestFullScreen) {
      elem.mozRequestFullScreen();
    } else if (elem.webkitRequestFullscreen) {
      elem.webkitRequestFullscreen(Element.ALLOW_KEYBOARD_INPUT);
    }
  } else {
    if (document.exitFullscreen) {
      document.exitFullscreen();
    } else if (document.msExitFullscreen) {
      document.msExitFullscreen();
    } else if (document.mozCancelFullScreen) {
      document.mozCancelFullScreen();
    } else if (document.webkitExitFullscreen) {
      document.webkitExitFullscreen();
    }
  }
}

function getWeekday() {
  switch(Date().slice(0, 3)){
    case 'Mon': return 'Segunda-feira';
    case 'Tue': return 'Terça-feira';
    case 'Wed': return 'Quarta-feira';
    case 'Thu': return 'Quinta-feira';
    case 'Fri': return 'Sexta-feira';
    case 'Sat': return 'Sábado';
    case 'Sun': return 'Domingo';
    default: return ''
  }
}

function getMonthDay() {
  return new Date().toJSON().slice(0,10);
}