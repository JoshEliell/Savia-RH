document.addEventListener("DOMContentLoaded", (e) => {
    /**Debes reemplazar o cambiar los valores de los bonos asignados por el ID que se encuentran en la subcategoria del bono */
    const bonoViajePEP = 0//0
    const bonoViajePrivado = 19//13
    const bonoCurso = 23//14
    const url = listarBonosVarillerosUrl
    
     /**Buscar el soporte para el bono seleccionado */
     /*async function solicitarSoporteBono(bono){
        try {
            var response = await fetch('/esquema/solicitar_soporte_bono/',{
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    'Content-Type': 'application/json',
                },
                body:JSON.stringify({
                    'bono':bono,
                }),
            });

            const datos = await response.json();
            //console.log(datos)
            //console.log(datos.soporte)

            document.getElementById("soporte").textContent = datos.soporte
            //cantidad = datos[0].fields.importe
            //cantidad === null ? mensajeBonoNa() : document.getElementById('cantidad').setAttribute('value',cantidad) 

        } catch (error) {
            console.log(error)
            Swal.fire({
                title: "Error",
                text: "No se pudo procesar la solicitud",
                icon: "warning",
            })

        }
    }*/

    /**Para verificar si existe un valor en el select de bono - bono de viaje al iniciar el DOM en js despues de agregar un bono - es para bono viaje */
    /*var viajeSelect = document.getElementById("bono");
    if (viajeSelect.selectedIndex > 0) {
        
        selectBonoCurso = parseInt(document.getElementById('bono').value)
        
        if (selectBonoCurso == bonoViajePEP || selectBonoCurso == bonoViajePrivado) {
            document.getElementById('km').classList.remove("d-none")
        }else{
            document.getElementById('km').classList.add("d-none")
        }
        
    }*/

    /**Para verificar si existe un valor en el select de bono al iniciar el DOM en js - despues de agregar un bono - es para el soporte*/
    /*var soporteSelect = document.getElementById("id_bono");
    if (soporteSelect.selectedIndex > 0) {
        //console.log("seleccionado")
        valor = soporteSelect.value
        solicitarSoporteBono(valor)
    }*/


    /**Seleccionar esquema bono */
    /*async function solicitarEsquemaBono(bono,puesto){
        try {
            var response = await fetch("{% url 'solicitar-esquema-bonos' %}",{
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    'Content-Type': 'application/json',
                },
                body:JSON.stringify({
                    'bono':bono,
                    'puesto':puesto
                }),
            });

            var datos = await response.json();
            cantidad = datos[0].fields.importe

            //Aqui debes de reemplazar/cambiar el id del bono ahorro 
           
            selectBonoCurso = parseInt(document.getElementById('id_bono').value)
            
            if(selectBonoCurso == bonoCurso){
                if(cantidad == 0.00){
                    document.getElementById('cantidad').removeAttribute("readonly")
                }else{
                    document.getElementById('cantidad').setAttribute("readonly")
                    document.getElementById('cantidad').value = '' 
                }
            }

            //document.getElementById('cantidad').setAttribute("readonly", "readonly");
            //cantidad === null ? mensajeBonoNa() : document.getElementById('cantidad').setAttribute('value',cantidad)
            cantidad === null ? mensajeBonoNa() : document.getElementById('cantidad').value = cantidad

        } catch (error) {
            //console.log(error)
            //document.getElementById('cantidad').setAttribute('value','') 
            document.getElementById('cantidad').value = '' 
            document.getElementById('cantidad').setAttribute("readonly", "readonly");
            Swal.fire({
                title: "Error",
                text: "No se pudo procesar la solicitud",
                icon: "warning",
            })

        }
    }*/

   
    //para cargar el soporte del bono
    /*var bonoSoporteSelect = document.getElementById("id_bono")

    bonoSoporteSelect.addEventListener("change",function(e){
        //console.log('solicitar soporte - requerimientos')
        const bono = document.getElementById("id_bono").value;
        //console.log("bono id: ",bono)
        solicitarSoporteBono(bono)
    });*/

    /**funcion para calcular los km - $1 x km a partir del km 501 se paga .50 */
    //para detectar cuando se pulsan los km ingresados
    var ingresarKM = document.getElementById('cantidad-km');
    var cantidadInput = document.getElementById('cantidad');
    
    ingresarKM.addEventListener("input", function(e) {
        var totalKM = parseFloat(ingresarKM.value);
    
        if (totalKM >= 501) {
            var restar = totalKM - 500;
            var calcular = restar * 0.50;
            var totalFinal = 500 + calcular;
            cantidadInput.value = totalFinal.toFixed(2); // Redondear el resultado a dos decimales
        } else {
            cantidadInput.value = totalKM;
        }
    });
    

    //para cargar la cantidad del bono cuando se seleccione alguno puesto o bono
    /*var puestoSelect = document.getElementById("id_puesto");
    var bonoSelect = document.getElementById("id_bono");

    puestoSelect.addEventListener("change",function (e) {
        const bono = document.getElementById("id_bono").value;
        const puesto = document.getElementById("id_puesto").value;

        if(bono.length != 0 && puesto.length != 0){
            solicitarEsquemaBono(bono,puesto)
        }
    });

    bonoSelect.addEventListener("change",function (e) {
        const bono = document.getElementById("id_bono").value;
        const puesto = document.getElementById("id_puesto").value;

        if(bono.length != 0 && puesto.length != 0){
            solicitarEsquemaBono(bono,puesto)

        }

    });*/

    /**Remover bono de la solicitud- good*/
    async function removerBono(bonoId){
        const url = `/esquema/remover_bono/${bonoId}/`
        console.log(url)
        try {
            var respuesta= await fetch(url,{
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    'Content-Type': 'application/json',
                },
                body:JSON.stringify({
                    'bonoId':bonoId,
                }),
            });

            const datos = await respuesta.json();
            console.log(datos)
            
            if (respuesta.status === 200) {
                //console.log(datos)
                //eliminar la fila
                const renderizar = document.querySelectorAll(`[data-id="${datos.bono_id}"]`)
                renderizar[0].remove()
                //renderizar el total en html
                total = document.getElementById('total').textContent = datos.total
                //se elimina la tabla cuando re remueven los bonos y no hay
                //if (datos.total == 0)
                //    document.getElementById('tabla').remove()
                



                /**se verifica la respuesta y depende si es un el puesto la cantidad sera divida o no */
                /** 
                if (!datos.reparto){
                    console.log(datos)
                    console.log(datos.reparto)
                    console.log(typeof(datos.reparto))
    
                    //eliminar la file
                    const renderizar = document.querySelectorAll(`[data-id="${datos.bono_id}"]`)
                    renderizar[0].remove()
                    //renderizar el total en html
                    total = document.getElementById('total').textContent = datos.total
                    //se elimina la tabla cuando re remueven los bonos y no hay
                    if (datos.total == 0)
                        document.getElementById('tabla').remove()
                }else{
                    console.log(datos.participantes)
                    console.log("Datos participanes: ",datos.participantes)
                    console.log("datos bandera: ", bandera)
                    //se elimina la fila que contiene el bono
                    const renderizar = document.querySelectorAll(`[data-id="${datos.bono_id}"]`)
                    renderizar[0].remove()
                    //se detecta la tabla y la clase cantidad para que sea sustituida esta cantidad
                    const celdasCantidad = document.querySelectorAll('#tabla .cantidad');
                    //cada celda se le pasa el monto 
                    celdasCantidad.forEach(celda => {
                        celda.textContent = '$' + datos.monto;
                    });
                    
                    if (datos.bandera == 1)
                        document.getElementById('tabla').remove()
                }
                */
               


                

            } else if (respuesta.status === 403) {
                Swal.fire({
                    title: "Acceso Denegado",
                    text: "No tienes permiso para realizar esta acción.",
                    icon: "error",
                });

            } else if (respuesta.status === 404) {
                Swal.fire({
                    title: "Error",
                    text: "No existe este bono en nuestros registros.",
                    icon: "warning",
                });
            }else{
                Swal.fire({
                    title: "Error",
                    text: "Intentelo más tarde",
                    icon: "warning",
                })
            }

        } catch (error) {
            //Manejo de errores
            console.log(error)
            Swal.fire({
                title: "Error",
                text: "No se pudo procesar la solicitud ",
                icon: "warning",

                
            })

        }
    }

    tabla = document.getElementById("tabla")
    if (tabla) {
        addEventListener("click", async function(e){
            //hacer click en el boton eliminar
            if(e.target.classList.contains("btn-danger") || e.target.classList.contains("fa-minus")){
                
                //verficar la clase que contiene para obtener el id del bono
                if (e.target.classList.contains("btn-danger")){
                    elemento = e.target.parentNode.parentNode
                    bonoId = elemento.getAttribute('data-id');
                }else{
                    elemento = e.target.parentNode.parentNode.parentNode
                    bonoId = elemento.getAttribute('data-id');
                }

                //mensaje de confirmacion para eliminar
                if (bonoId > 0){
                    Swal.fire({
                    title: "¿Desea quitar este bono?",
                    text: "No se puede deshacer esta acción",
                    icon: "warning",
                    showCancelButton: true,
                    confirmButtonColor: "#3085d6",
                    cancelButtonColor: "#696969",
                    confirmButtonText: "Aceptar",
                    cancelButtonText: "Cancelar"
                  }).then((result) => {
                    if (result.isConfirmed) {
                        removerBono(bonoId)
                    }
                });
                }

            }
        });
    }


    /**Para eliminar un archivo -good */
    async function removerArchivo(archivo){
        try {
            var response = await fetch(`/esquema/remover_archivo/${archivo}/`,{
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    'Content-Type': 'application/json',
                },
                body:JSON.stringify({
                    'archivo_id':archivo,
                }),
            });
            const datos = await response.json();
            if (response.status === 200){
                console.log(datos)
                var renderizar = document.querySelectorAll(`[data-archivo="${datos.archivo_id}"]`)
                renderizar[0].remove()
            }else{
                Swal.fire({
                    title: "Error",
                    text: "No se encontro el recurso solicitado",
                    icon: "warning",
                })
            }
        } catch (error) {
            console.log(error)
            Swal.fire({
                title: "Error",
                text: "No se pudo procesar la solicitud",
                icon: "warning",
            })
        }
    }

    files = document.getElementById("archivos")
    

    
    if (files) {
        addEventListener("click", async function(e){
            if(e.target.classList.contains('small')){
                archivo_id = e.target.getAttribute("data-archivo")
                console.log("el ID del archivo es: ",archivo_id)
                removerArchivo(archivo_id)    
            }
        });
    }

    /**Enviar la solicitud - autorizacion */
    /*async function enviarSolicitud(solicitud){
        try {
            var response = await fetch("{% url 'enviar_solicitud' %}",{
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    'Content-Type': 'application/json',
                },
                body:JSON.stringify({
                    'solicitud':solicitud
                }),
            });

            const datos = await response.json();
            console.log(datos)
            console.log(datos.status)

            if (datos.mensaje === 1){
                Swal.fire({
                    title: "Exitoso",
                    text: "Su solicitud será revisada por el superintendente",
                    icon: "success",
                }).then((result) => {
                    // Este código se ejecuta después de que el usuario hace clic en OK
                    if (result.isConfirmed) {
                      console.log('El usuario hizo clic en OK');
                      window.location.href = url;
                    }
                });
               
                //desactivar los botones
                var botonEnviar = document.getElementById('enviar_solicitud');
                var botonSubir = document.getElementById('subirArchivos');
                var botonAgragarBono = document.getElementById('btnAgregar')
                var botonRemoverBono = document.getElementById('removerBono')
                botonEnviar.setAttribute('disabled',true);
                botonSubir.setAttribute('disabled',true);
                botonAgragarBono.setAttribute('disabled',true);
                botonRemoverBono.setAttribute('disabled',true);
                var boton = document.getElementsByClassName('subirArchivos')
                var primerElemento = boton[0];
                primerElemento.disabled = true;
                primerElemento.disabled = true;

            }else{
                Swal.fire({
                    title: "Error",
                    text: "Falta subir el soporte",
                    icon: "warning",
                })
            }

           

        } catch (error) {
            Swal.fire({
                title: "Error",
                text: "No se pudo procesar la solicitud",
                icon: "warning",
            })
        }
    }
    
    var botonEnviar = document.getElementById('enviar_solicitud');
    
    if (botonEnviar){
        botonEnviar.addEventListener("click",async function(e){
            
            var folio = document.getElementsByName('folio')[0].value;
            enviarSolicitud(folio)
        })
    }*/

});