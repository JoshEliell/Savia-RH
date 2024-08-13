document.addEventListener("DOMContentLoaded", function() {
    /* Permite poner los días de la semana al lado del formulario */
    const filas = document.querySelectorAll('#tabla_incidencias tbody tr');
    const dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];

    filas.forEach((fila, index) => {
        const primeraCelda = fila.querySelector('td:first-child');
        const dia = dias_semana[index % dias_semana.length]; // Cicla a través de los días de la semana
        primeraCelda.textContent = dia;
    });
});