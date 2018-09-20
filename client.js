import PyFiClient from 'pyfi-client'

const py = PyFiClient()

let imgSize = {}

let baseChair = {}
let derivedChairs = {}

const button = document.getElementById('button')
const button_family = document.getElementById('button_family')
const result = document.getElementById('result')
const input = document.getElementById('input')
button.disabled = true

const loadImage = function(file_name, index){
  let elem = document.createElement('img')
  elem.setAttribute('src', `imgs/${file_name}`)
  elem.setAttribute('data-vector-index', index)
  document.getElementById('imageFrame').appendChild(elem)
}

const loadFamily = function(file_name, index){
  let elem = document.createElement('img')
  // document.getElementById('imageFrame').removeChild('img')
  elem.setAttribute('src', `imgs/${file_name}`)
  elem.setAttribute('familyImg', 'null')
  elem.setAttribute('data-vector-index', index)
  document.getElementById('familyFrame').appendChild(elem)
}

function removeImages() {
  var images = [].slice.call(document.getElementsByTagName('img'), 0)
  images.forEach(function(img) { // iterate the images array
    img.parentNode.removeChild(img) // remove the child node via the parent node
  });
}

function removeFamily() {

  if (document.querySelectorAll('familyImg') == null) {
    return "null";
  } else {
    var images = [].slice.call(document.querySelectorAll('familyImg'), 0)
    console.log(images)
    images.forEach(function(img) { // iterate the images array
      img.parentNode.removeChild(img) // remove the child node via the parent node
    })
    return "Removed";
  }
}

py._.onReady(()=>{
  // wait until PyFi is ready to allow clicks
  button.disabled = false
  console.log('PyFi Ready!')
  py.get_size([])
  .then(size => {
    console.log(size)
    imgSize = size
  })
})


button.addEventListener("click", function(event){
  console.log('clicked initial generator!')
  event.preventDefault()
  event.stopPropagation()

  button.disabled = true
  removeImages()
  py.generate_random_chair([])
  .then(res => {
    baseChair = res
    loadImage(baseChair.file_name)
    console.log('baseChair Set:',res)
    button.disabled = false
  })
  .catch(error => {
    console.log(error)
  })
})

button_family.addEventListener("click", function(event){
  event.preventDefault()
  event.stopPropagation()
  // button_family.disabled = true

  let generationVector = baseChair.latent_vector
  // look to see if the element has a data-vector-index attr,
  // if so generate chairs based on that vector,
  // otherwise assume it is the base vector
  console.log('GENERATING FROM : baseChair.latent_vector', [baseChair.latent_vector])

  // py.generate_random_chair([])
  // .then(res => {
  //   console.log(res)
  //   loadImage(res.file_name)
    py.generate_similar_chairs([baseChair.latent_vector])
      .then(derivations => {
        derivedChairs = derivations
        removeFamily()

        console.log('derivedChairs Set:',derivedChairs)
        derivedChairs.file_names.forEach(function(file_name, index) {
          loadFamily(file_name, index)
        })
        button_family.disabled = false
      })
  // })
    .catch(error => {
      console.log(error)
    })
})
