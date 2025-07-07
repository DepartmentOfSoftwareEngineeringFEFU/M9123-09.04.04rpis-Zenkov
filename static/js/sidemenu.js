let timeoutLinks = null;

/* Set the width of the side navigation to 250px and the left margin of the page content to 250px */
function openNav() {
  if (closeAllWindows != null) closeAllWindows();
  let openbtn = document.getElementById("openbtn")
  if (openbtn.getAttribute("opened") != null) {
    clearTimeout(timeoutLinks)
    document.getElementById("sidemenuContents").style.width = "0";
    //document.getElementById("main").style.marginLeft = "0";
    openbtn.removeAttribute("opened")
    openbtn.innerText = "☰";
    openbtn.style.fontSize = "15px";
    document.querySelectorAll('#sidemenuContents ul ul li a').forEach(function(link) {hideLists()})
  }
  else {
    clearTimeout(timeoutLinks)
    document.getElementById("sidemenuContents").style.width = "300px";
    //document.getElementById("main").style.marginLeft = "500px";
    openbtn.setAttribute("opened", "")
    openbtn.innerText = "×";
    openbtn.style.fontSize = "25px";
    timeoutLinks = setTimeout(function(){
      document.querySelectorAll('#sidemenuContents ul ul li a').forEach(function(link) {revertLists()})
    }, 400);
  }
}

/* Set the width of the side navigation to 0 and the left margin of the page content to 0 */
function closeNav() {
  document.getElementById("sidemenuContents").style.width = "0";
  document.getElementById("main").style.marginLeft = "0";
}

function hideLists() {
  let listBook = document.getElementById('listBook')
  listBook.style.display = "none";
}

function revertLists() {
  let listBook = document.getElementById('listBook')
  if (listBook.getAttribute("opened") != null) {
    listBook.style.display = "block";
  }
}

function openList(listName) {
  let list = document.getElementById(listName)
  if (list.getAttribute("opened") != null) {
    list.style.display = "none";
    list.removeAttribute("opened")
  }
  else {
    list.style.display = "block";
    list.setAttribute("opened", "")
  }
}

setTimeout(function(){
	openList('listBook');
	hideLists();
}, 100);
