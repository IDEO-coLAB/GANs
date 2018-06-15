import PyFiClient from 'pyfi-client'

const py = PyFiClient()

let imgSize = {}

let canvas = document.createElement('canvas')
let ctx = canvas.getContext('2d')

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

    canvas.width = imgSize.width
    canvas.height = imgSize.height
  })
})


button.addEventListener("click", function(){
  button.disabled = true
  py.generate_image([])
  .then(res => {
    console.log(res)
    renderimage(res)
    result.innerHTML = `logged console`
    button.disabled = false
  })
  .catch(error => {
    console.log(error)
  })
})

const renderimage = function(image_message){
  ctx.putImageData(image_message, 0, 0)
}
