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

// Dibuja una tabla. columnas: lista de [título, función que saca el valor de la fila].
// acciones: lista de [texto, función, clase] que se agregan como botones en cada fila.
function tabla(id, filas, {columnas = null, acciones = []} = {}) {
    const contenedor = document.getElementById(id);

    if (!filas.length) {
        contenedor.innerHTML = '<p class="vacio">Todavía no hay nada cargado acá.</p>';
        return;
    }

    columnas = columnas || Object.keys(filas[0]).map(c => [c, f => f[c]]);

    const t = document.createElement('table');
    const encabezado = t.createTHead().insertRow();

    for (const [titulo] of columnas) {
        const th = document.createElement('th');
        th.textContent = titulo;
        encabezado.appendChild(th);
    }
    if (acciones.length) {
        encabezado.appendChild(document.createElement('th'));
    }

    const cuerpo = t.createTBody();

    for (const fila of filas) {
        const tr = cuerpo.insertRow();

        for (const [, valor] of columnas) {
            const v = valor(fila);
            const celda = tr.insertCell();
            if (v instanceof Node) celda.appendChild(v);
            else celda.textContent = v ?? '';
        }

        if (acciones.length) {
            const celda = tr.insertCell();
            celda.className = 'acciones';
            for (const [texto, funcion, clase] of acciones) {
                const boton = document.createElement('button');
                boton.type = 'button';
                boton.textContent = texto;
                if (clase) boton.className = clase;
                boton.onclick = () => funcion(fila);
                celda.appendChild(boton);
            }
        }
    }

    contenedor.replaceChildren(t);
}

// Convierte la fecha que manda Flask ("Fri, 12 Mar 2004 00:00:00 GMT") a "2004-03-12".
function fechaISO(texto) {
    return texto ? new Date(texto).toISOString().slice(0, 10) : '';
}

// Igual que fechaISO pero para mostrar: "12/03/2004".
function fechaLinda(texto) {
    return texto ? fechaISO(texto).split('-').reverse().join('/') : '';
}

const MESES = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio',
               'Agosto', 'Setiembre', 'Octubre', 'Noviembre', 'Diciembre'];

// Reemplaza el calendario del navegador de un input de fecha por uno con el estilo del sitio.
function armarCalendario(input) {
    const caja = document.createElement('span');
    caja.className = 'campo-fecha';
    input.replaceWith(caja);

    const boton = document.createElement('button');
    boton.type = 'button';
    boton.className = 'boton-fecha';
    boton.setAttribute('aria-label', 'Abrir calendario');
    boton.innerHTML = '<span class="pixel" data-pixel="calendario"></span>';

    const panel = document.createElement('div');
    panel.className = 'calendario';
    panel.hidden = true;

    caja.append(input, boton, panel);

    let vista;
    const iso = (a, m, d) => `${a}-${String(m + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
    const hoy = new Date();

    function dibujar() {
        const anio = vista.getFullYear();
        const mes = vista.getMonth();
        const desde = input.min ? Number(input.min.slice(0, 4)) : 1940;
        const hasta = input.max ? Number(input.max.slice(0, 4)) : hoy.getFullYear() + 2;

        let html = `<div class="cal-cabeza">
            <button type="button" data-mover="-1" aria-label="Mes anterior">◀</button>
            <select data-campo="mes">${MESES.map((m, i) => `<option value="${i}" ${i === mes ? 'selected' : ''}>${m}</option>`).join('')}</select>
            <select data-campo="anio">${Array.from({length: hasta - desde + 1}, (_, i) => hasta - i)
                .map(a => `<option ${a === anio ? 'selected' : ''}>${a}</option>`).join('')}</select>
            <button type="button" data-mover="1" aria-label="Mes siguiente">▶</button>
        </div><div class="cal-dias">`;

        for (const d of ['Lu', 'Ma', 'Mi', 'Ju', 'Vi', 'Sá', 'Do']) {
            html += `<span class="cal-semana">${d}</span>`;
        }

        const vacios = (new Date(anio, mes, 1).getDay() + 6) % 7;
        html += '<span></span>'.repeat(vacios);

        const diasDelMes = new Date(anio, mes + 1, 0).getDate();
        for (let d = 1; d <= diasDelMes; d++) {
            const fecha = iso(anio, mes, d);
            const clases = [
                fecha === input.value ? 'elegido' : '',
                fecha === iso(hoy.getFullYear(), hoy.getMonth(), hoy.getDate()) ? 'hoy' : '',
            ].join(' ');
            const fuera = (input.min && fecha < input.min) || (input.max && fecha > input.max);
            html += `<button type="button" class="${clases}" data-fecha="${fecha}" ${fuera ? 'disabled' : ''}>${d}</button>`;
        }

        panel.innerHTML = html + '</div>';
    }

    function abrir() {
        const base = input.value ? new Date(input.value + 'T00:00')
                   : input.max ? new Date(input.max + 'T00:00') : hoy;
        vista = new Date(base.getFullYear(), base.getMonth(), 1);
        dibujar();
        panel.hidden = false;
    }

    boton.onclick = () => panel.hidden ? abrir() : (panel.hidden = true);

    panel.onclick = (e) => {
        const b = e.target.closest('button');
        if (!b) return;
        if (b.dataset.mover) {
            vista.setMonth(vista.getMonth() + Number(b.dataset.mover));
            dibujar();
        } else if (b.dataset.fecha) {
            input.value = b.dataset.fecha;
            input.dispatchEvent(new Event('input', {bubbles: true}));
            panel.hidden = true;
            input.focus();
        }
    };

    panel.onchange = (e) => {
        const campo = e.target.dataset.campo;
        if (campo === 'mes') vista.setMonth(Number(e.target.value));
        if (campo === 'anio') vista.setFullYear(Number(e.target.value));
        dibujar();
    };

    document.addEventListener('click', (e) => {
        if (!caja.contains(e.target)) panel.hidden = true;
    });
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') panel.hidden = true;
    });
}

document.querySelectorAll('input[type=date]').forEach(armarCalendario);

// Los errores de api() ya se muestran en pantalla, así que no los repetimos en la consola.
window.addEventListener('unhandledrejection', e => e.preventDefault());

// Escribe un título mezclando texto y datos: titulo('id', 'Editar ', [nombre]).
// Los datos (entre corchetes) se muestran con la letra de datos.
function titulo(id, ...partes) {
    const el = document.getElementById(id);
    el.replaceChildren(...partes.map(p => {
        if (!Array.isArray(p)) return p;
        const span = document.createElement('span');
        span.className = 'dato';
        span.textContent = p[0];
        return span;
    }));
}
