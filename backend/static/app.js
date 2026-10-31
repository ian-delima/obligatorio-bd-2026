// Llama a la API; si responde con error lo muestra y corta.
async function api(metodo, url, datos) {
    const opciones = {method: metodo, headers: {}};

    if (datos !== undefined) {
        opciones.headers['Content-Type'] = 'application/json';
        opciones.body = JSON.stringify(datos);
    }

    const respuesta = await fetch(url, opciones);
    const json = await respuesta.json().catch(() => ({}));

    if (!respuesta.ok) {
        mostrar(json.error || 'Error ' + respuesta.status, true);
        throw new Error(json.error);
    }

    if (json.mensaje) {
        mostrar(json.mensaje, false);
    }

    return json;
}

// Muestra un mensaje verde (ok) o rojo (error) arriba de la página.
function mostrar(texto, esError) {
    const caja = document.getElementById('mensaje');
    caja.textContent = texto;
    caja.className = esError ? 'error' : 'ok';
}

// Dibuja una tabla con las filas; acciones es una lista de [texto, función].
function tabla(id, filas, acciones = []) {
    const contenedor = document.getElementById(id);

    if (!filas.length) {
        contenedor.innerHTML = '<p>No hay datos.</p>';
        return;
    }

    const columnas = Object.keys(filas[0]);
    const t = document.createElement('table');
    const encabezado = t.insertRow();

    for (const c of columnas) {
        encabezado.insertCell().outerHTML = '<th>' + c + '</th>';
    }
    if (acciones.length) {
        encabezado.insertCell().outerHTML = '<th></th>';
    }

    for (const fila of filas) {
        const tr = t.insertRow();

        for (const c of columnas) {
            tr.insertCell().textContent = fila[c] ?? '';
        }

        if (acciones.length) {
            const celda = tr.insertCell();
            for (const [texto, funcion] of acciones) {
                const boton = document.createElement('button');
                boton.textContent = texto;
                boton.onclick = () => funcion(fila);
                celda.appendChild(boton);
            }
        }
    }

    contenedor.replaceChildren(t);
}
