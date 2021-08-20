// setCookie and getCookie taken from https://www.w3schools.com/js/js_cookies.asp

bundeslaender={
  "BR":"Gesamt",
  "01":"Schleswig-Holstein",
  "02":"Hamburg",
  "03":"Niedersachsen",
  "04":"Bremen",
  "05":"Nordrhein-Westfalen",
  "06":"Hessen",
  "07":"Rheinland-Pfalz",
  "08":"Baden-Württemberg",
  "09":"Bayern",
  "10":"Saarland",
  "11":"Berlin",
  "12":"Brandenburg",
  "13":"Mecklenburg-Vorpommern",
  "14":"Sachsen",
  "15":"Sachsen-Anhalt",
  "16":"Thüringen"
}

function setCookie(cname, cvalue, exdays = 365) {
  var d = new Date();
  d.setTime(d.getTime() + (exdays*24*60*60*1000));
  var expires = "expires="+ d.toUTCString();
  document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/covid19/;SameSite=Strict";
  console.log("set " + cname + " to " + cvalue);
}

function getCookie(cname) {
  var name = cname + "=";
  var decodedCookie = decodeURIComponent(document.cookie);
  var ca = decodedCookie.split(';');
  for(var i = 0; i <ca.length; i++) {
    var c = ca[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}

function setHiddenOnCookie(item, index) {
  hidden = getCookie(item.label);
  console.log(item.label +"/"+ hidden);
  if (hidden == "true") {
    cc.data.datasets[index].hidden = true;
  }
}

function showDataInGraph() {
  for (var i = 0; i < datasets.length; i++) {
    if (datasets[i].label == this.id) {
      var found = false;
      for (var j=0; j<cc.data.datasets.length;j++) {
        if (cc.data.datasets[j].label == this.id) {
          found = j;
          break;
        }
      }
      if (found !== false) {
        cc.data.datasets.splice(found,1);
        setCookie(this.id+"inGraph", false);
        this.classList.remove('s');
      } else {
        cc.data.datasets.push(datasets[i]);
        setCookie(this.id+"inGraph", true);
        this.classList.add('s');
      }
      cc.update();
    }
  }
}

function showLandkreisInList(item, index) {
  blid = item.kreisid.substring(0,2);
  bldiv = document.getElementById(blid);
  if (!bldiv) {
    bldiv = document.createElement('div');
    bldiv.id = blid;
    bldiv.classList.add("bl");
    bldiv.innerHTML = "<h2>" + bundeslaender[blid] + "</h2>";
    document.getElementById('lk').appendChild(bldiv);
  }
  bldiv.innerHTML = bldiv.innerHTML + " <div class=b><em id=\"" + item.label + "\">" + item.label + "</em></div>";
}


