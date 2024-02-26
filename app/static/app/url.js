let header = document.querySelector("header");
let main = document.querySelector("main");
main.style.paddingTop = header.offsetHeight + "px";
let link = document.querySelector(".links");

var thresholdWidth = 900;

function widthChange(){
  let windowWidth = window.innerWidth;
  let linkElement = document.getElementById('links')
  if (windowWidth<=thresholdWidth){
    if(linkElement.classList.value.indexOf('transition')<0){
      linkElement.classList.toggle('transition')
    }
  } else {
    if(linkElement.classList.value.indexOf('transition')>=0){
      linkElement.classList.toggle('transition')
    }
  }
}
widthChange()
window.addEventListener('resize', function(){
  widthChange()
})

function menu() {
  link.classList.toggle("active");

  // add hide function to posts link
  let postsElement = document.getElementById('posts-tag')
  postsElement.setAttribute('onclick', "hideLink(event=event)")

  console.log(postsElement.classList.value)

  if(postsElement.classList.value.includes('hide')){
    console.log('here')
    hideLink()
  }

}

function hideLink(event = null){
  if(event){
    event.preventDefault()
  }
  console.log("running")
  // add hide to the classes for 3 main tags in the menu
  let homeElement = document.getElementById('home-tag')
  // homeElement.setAttribute('class', 'hide')
  hide(homeElement)
  let aboutElement = document.getElementById('about-tag')
  // aboutElement.setAttribute('class', 'hide')
  hide(aboutElement)
  let postsElement = document.getElementById('posts-tag')
  // postsElement.setAttribute('class', 'hide')
  hide(postsElement)

  let dropdownElement = document.getElementById('dropdown')
  // dropdownElement.classList.add('show')
  show(dropdownElement)
  
}

function hide(element){
  element.classList.toggle("hide")
}
function show(element){
  element.classList.toggle('show')
}

function toggleDiv(a) {
  a = a.parentNode.parentNode.parentNode
  replybox = a.querySelector('.comment-box')
  if (replybox.style.display === "none") {
    replybox.style.display = "block";
  } else {
    replybox.style.display = "none";
  }
}

// const dropdown = document.querySelector('header .links .dropdown');
// console.log(header)

// dropdown.addEventListener('mouseover', function() {
//   header.style.height = '150px'; // Set the increased height when the dropdown is hovered over
// });

// dropdown.addEventListener('mouseout', function() {
//   header.style.height = '100px'; // Set the original height when the mouse moves out of the dropdown
// });