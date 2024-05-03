document.addEventListener("DOMContentLoaded", function() {

    /**función async await para verificar las incidencias*/
    async function verificarIncidencias(id){
        var formData = new FormData(document.getElementById("incidencias-form"));

        try {
            var response = await fetch(`/prenomina/programar_incidencias/${id}/`,{
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                },
                body: formData
            });

            var data = await response.json();
            console.log ("esta es la data: ",data)
            console.log ("este es el response: ",response)

            if (response.ok) {
                
                Swal.fire({
                    title: "Mensaje",
                    text: "Se ha agregado la incidencia correctamente",
                    icon: "success",
                    confirmButtonText: "Pulsa aquí para continuar"
                }).then((result) => {
                    if (result.isConfirmed) {
                        window.location.reload();
                    }
                });

                if (data.success) {
                    console.log(data.message); // Mensaje de éxito
                } else {
                    console.error('Error de validación:', data.errors);
                    mostrarErrores(data.errors); // Mostrar errores de validación
                }
            } else {
                switch (response.status) {
                    case 405:
                        Swal.fire({
                            title: "Error",
                            text: "No se pudo procesar la solicitud",
                            icon: "warning",
                        })
                        break;
                    case 422:
                        if (data.poscondicion){
                            //console.log(data.poscondicion)
                            Swal.fire({
                                title: "Error",
                                text: data.poscondicion,
                                icon: "warning",
                            })
                        }else{
                            Swal.fire({
                                title: "Error",
                                text: "Errores de validación",
                                icon: "warning",
                            })
                        }
                        break;
                    default:
                        console.log('Mensaje no reconocido');
                }
                console.log(response)
                console.error('Error en la respuesta del servidor:', response.status);
            }
        } catch (error) {
            console.error('Error en la solicitud:', error);
        }
    }

    function mostrarErrores(errors) {
        // Mostrar los errores al usuario, por ejemplo, en el DOM
        //var errorContainer = document.getElementById('error-container');
        //errorContainer.innerHTML = ''; // Limpiar mensajes de error anteriores

        for (var fieldName in errors) {
            var errorMessage = errors[fieldName].join(', '); // Concatenar mensajes de error
            //var errorElement = document.createElement('div');
            //errorElement.textContent = fieldName + ': ' + errorMessage;
            console.log(fieldName + errorMessage)
            //errorContainer.appendChild(errorElement);
        }
    }

    //Clic al botón de guardar la incidencia
    var boton_programar = document.getElementById("btn-programar")
    boton_programar.addEventListener("click", function(e) {
        e.preventDefault();
        //se obtiene el valor del id del input hidden costo  
        var costo = document.getElementById('costo').value 
        //console.log(costo)
        verificarIncidencias(costo)
    });

    


});