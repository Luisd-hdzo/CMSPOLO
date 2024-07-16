document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('rsvp-form');

    form.addEventListener('submit', (event) => {
        event.preventDefault();

        const fullName = document.getElementById('fullName').value;
        const attendance = document.getElementById('attendance').value;
        const contact = document.getElementById('contact').value;
        const specialMenu = document.getElementById('specialMenu').value;

        const newEntry = [fullName, attendance, contact, specialMenu];

        // Verificar si ya existe un archivo Excel guardado en localStorage
        let existingData = localStorage.getItem('invitados_confirmados');
        let workbook;

        if (existingData) {
            const workbookBinary = atob(existingData);
            workbook = XLSX.read(workbookBinary, {type: 'binary'});
        } else {
            // Crear un nuevo libro de trabajo
            workbook = XLSX.utils.book_new();
            // Crear una hoja de cálculo
            workbook.SheetNames.push("Invitados");
            const worksheetData = [["Nombre Completo", "Asistirás al evento?", "Contacto", "¿Necesitas menú especial?"]];
            const worksheet = XLSX.utils.aoa_to_sheet(worksheetData);
            workbook.Sheets["Invitados"] = worksheet;
        }

        // Añadir los nuevos datos
        const worksheet = workbook.Sheets["Invitados"];
        const sheetData = XLSX.utils.sheet_to_json(worksheet, {header: 1});
        sheetData.push(newEntry);
        const updatedWorksheet = XLSX.utils.aoa_to_sheet(sheetData);
        workbook.Sheets["Invitados"] = updatedWorksheet;

        // Guardar el libro de trabajo en localStorage
        const workbookBinary = XLSX.write(workbook, {bookType: 'xlsx', type: 'binary'});
        const workbookBase64 = btoa(workbookBinary);
        localStorage.setItem('invitados_confirmados', workbookBase64);

        // Confirmación
        alert('Datos guardados exitosamente.');
        form.reset();
    });
});
