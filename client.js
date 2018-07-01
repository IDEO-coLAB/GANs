import PyFiClient from 'pyfi-client'

const py = PyFiClient()

let imgSize = {}


const button = document.getElementById('button')
const result = document.getElementById('result')
const input = document.getElementById('input')
button.disabled = true

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


button.addEventListener("click", function(){
  button.disabled = true
  py.generate_image([])
  .then(res => {
    console.log(res)
    loadImage(res)
    result.innerHTML = `success!`
    button.disabled = false
  })
  .catch(error => {
    console.log(error)
  })
})

const loadImage = function(file_name){
  let elem = document.createElement('img')
  elem.setAttribute('src', `imgs/${file_name}`)
  document.getElementById('imageFrame').appendChild(elem)
}
