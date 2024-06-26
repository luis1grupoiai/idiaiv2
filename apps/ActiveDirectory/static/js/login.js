function mostrarSpinnerMax() 
    {
        document.getElementById('spinner-overlay-max').style.display = 'block';
    }

    function ocultarSpinnerMax() 
    {
        document.getElementById('spinner-overlay-max').style.display = 'none';
    }


$("#btnSession").on("click", function(event){
    mostrarSpinnerMax();
    event.preventDefault();
    console.log("Dio clic en iniciar sesion ...")
    
    var usuario = $("#username").val();
    var password = $("#password").val();
    // var csrfToken = '{{ csrf_token }}';
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    bValido = true;
    sTexto = "";
    // var csrfToken = getCookie('csrftoken');
    // bPwd = btoa(password);
    // console.log(usuario);
    // console.log(bPwd);

    if(usuario.trim().length == 0)
    {
        sTexto = "El campo usuario viene vacío, por favor de ingresar un usuario válido.";
        bValido = false;
    }

    if(password.trim().length == 0)
    {
        sTexto += " El campo contraseña viene vacío, por favor de ingresar este dato.";
        bValido = false;
    }

    // setTimeout(function() {
    //     // Agrega el código para recargar la página aquí
    //     // window.location.href = 'soldadores.php';
        
    //     // location.href=urlRedireccion
    //     ocultarSpinnerMax();
    //   }, 2500);

    if(!bValido)
    {
       setTimeout(function() {
       
        
      }, 2500);
       

      ocultarSpinnerMax();

        Swal.fire({
            icon: 'error',
            title: sTexto,
            showConfirmButton: false,
            timer: 2500
            });
            $('#inlineForm').modal('hide');

    }else
    {
        // setTimeout(function() {
        //     // Agrega el código para recargar la página aquí
        //     // window.location.href = 'soldadores.php';
            
        //     // location.href=urlRedireccion
        //     ocultarSpinnerMax();
        //   }, 1500);

        $.ajax({
            type: 'POST',       
            url: obtenerDatosUsuario,
            headers: { 'X-CSRFToken': csrftoken },
            data: {            
                'username' : usuario,
                'password' : password
            },
            success: function(response) {
                console.log(response)
    
                // if(response)
                // {
                //     location.href="/"
                // }
    
                if(response.message == "Success")
                {
                    ocultarSpinnerMax();
                    // alert("Inicio de sesión valido :) ")
                    // var urlRedireccion = response.url_direccion;
                    
                    var urlRedireccion = response.url_direccion;
                    Swal.fire({
                        icon: 'success',
                        title: '¡BIENVENIDO(A) '+response.empleado+'!',
                        showConfirmButton: false,
                        timer: 2500
                        });
                        //  $('#inlineForm').modal('hide');
                    

                    // Swal.fire({
                    //     toast: true,
                    //     icon: 'success',
                    //     title: 'Inicio de sesión correcto',
                    //     position: 'top',
                    //     showConfirmButton: false,
                    //     timer: 2500,
                    //     timerProgressBar: true,
                    //     didOpen: (toast) => {
                    //       toast.addEventListener('mouseenter', Swal.stopTimer)
                    //       toast.addEventListener('mouseleave', Swal.resumeTimer)
                    //     }
                    //   });

                      setTimeout(function() {
                        // Agrega el código para recargar la página aquí
                        // window.location.href = 'soldadores.php';
                        
                        // location.href=urlRedireccion
                        window.location.href = urlRedireccion;
                      }, 2500);

                    
                    // window.location.href = urlRedireccion;
                    
                }else
                {
                    ocultarSpinnerMax();
                    // alert(response.message)
                    // alert(response.descripcion)
    
                    Swal.fire({
                    icon: 'error',
                    title: response.descripcion,
                    showConfirmButton: false,
                    timer: 2500
                    });
                    // $('#inlineForm').modal('hide');
                    
                    setTimeout(function() {
                        location.reload();
                    }, 2500);
                }
               
                // location.href ="inicio.html";
    
                
                // Swal.fire({
                //     icon: 'success',
                //     title: 'Solicitud enviada con éxito',
                //     showConfirmButton: false,
                //     timer: 2500
                // });
                // $('#inlineForm').modal('hide');
            },
            error: function(error) {
                console.log(error);
                ocultarSpinnerMax();
                Swal.fire({
                    icon: 'error',
                    title: 'Ocurrió un error al iniciar sesión, por favor contacte al area de desarrollo.',
                    showConfirmButton: false,
                    timer: 2500
                    });

                    setTimeout(function() {
                        location.reload();
                    }, 2500);
                    // $('#inlineForm').modal('hide');

                
            }
        });
    }


   
});


function checkMonthAndRun() {
    var currentDate = new Date();
    var currentMonth = currentDate.getMonth(); // en JavaScript, Enero es 0, Diciembre es 11

    if (currentMonth === 11) { // Diciembre
        iniNevada(100, 80);
       

    } else if (currentMonth === 1 && currentDay === 2) { // 14 de Febrero
        iniCorazones(14, 80);
    }
}
// COPO DE NIEVE 
class oCopo{
  constructor(tam, id){
     this.x = 0;
     this.y = 0;
     this.size = tam;
     this.nombre = id
     this.obj = document.createElement("div");
     this.obj.setAttribute('id',id);
     this.obj.innerText="*";
     this.obj.style.position = "absolute";
     this.obj.style.fontSize = tam+"px";
     this.obj.style.color = "white";
     document.body.appendChild(this.obj)
}
dibujar(x,y){
     this.x = x;
     this.y = y;
     this.obj.style.top = this.y+"px";
     this.obj.style.left = this.x+"px";
     }
}
function iniCopos(num, anc, alto){
   var copos = new Array(num);
   var tam, x, y;
   for (let i = 0; i<num; i++)
     {
     tam = Math.round(Math.random()*10)+ 8;
     copos[i] = new oCopo(tam, "c"+i);
     x = parseInt(Math.random()*anc);
     y = parseInt(Math.random()*alto);
     copos[i].dibujar(x,y);
     }
return copos;
}
function iniNevada(num, vel)
{
var ancho = document.body.offsetWidth-10;
var alto = window.innerHeight-10;
var losCopos = iniCopos(num, ancho, alto)
nevar(losCopos, ancho,alto, vel);


} 
function nevar(copos, coposAncho, coposAlto, vel)
{
var x, y;
for (let i = 0; i < copos.length; i++)
    {
    y = copos[i].y;
x = copos[i].x;
    if (Math.random() > 0.5)
        y += parseInt(Math.random()+1);
    y += parseInt(Math.random()+2);
    if (y >= (coposAlto - copos[i].size))
        {
        y = Math.round(Math.random()*10);
        x  =parseInt(Math.random()*coposAncho-1); 
        }
copos[i].dibujar(x,y); 
    }
setTimeout(nevar, vel, copos,  coposAncho, coposAlto, vel);
}

//CORAZONES 
function oCorazon(tam, id) {
    this.x = 0;
    this.y = 0;
    this.size = tam;
    this.nombre = id;
    this.obj = document.createElement("div");
    this.obj.setAttribute('id', id);
    this.obj.innerText = "❤️";
    this.obj.style.position = "absolute";
    this.obj.style.fontSize = tam + "px";
    this.obj.style.color = "red";
    document.body.appendChild(this.obj);
}

function iniCorazones(num, vel) {
    var ancho = document.body.offsetWidth - 10;
    var alto = window.innerHeight - 10;
    var losCorazones = iniObjetos(num, ancho, alto, oCorazon);
    caer(losCorazones, ancho, alto, vel);
}

function iniObjetos(num, anc, alto, tipoObjeto) {
    var objetos = new Array(num);
    var tam, x, y;
    for (let i = 0; i < num; i++) {
        tam = Math.round(Math.random() * 20) + 15;
        objetos[i] = new tipoObjeto(tam, "o" + i);
        x = parseInt(Math.random() * anc);
        y = parseInt(Math.random() * alto);
        objetos[i].dibujar(x, y);
    }
    return objetos;
}

function caer(objetos, objetosAncho, objetosAlto, vel) {
    var x, y;
    for (let i = 0; i < objetos.length; i++) {
        y = objetos[i].y;
        x = objetos[i].x;
        y += parseInt(Math.random() * 2) + 1;
        if (y >= (objetosAlto - objetos[i].size)) {
            y = Math.round(Math.random() * 10);
            x = parseInt(Math.random() * objetosAncho - 1);
        }
        objetos[i].dibujar(x, y);
    }
    setTimeout(caer, vel, objetos, objetosAncho, objetosAlto, vel);
}

oCorazon.prototype.dibujar = function (x, y) {
    this.x = x;
    this.y = y;
    this.obj.style.top = this.y + "px";
    this.obj.style.left = this.x + "px";
};



