// Dibujos de pixel art: cada letra es un color y cada fila una línea de pixeles.
const CUERPO = [
    '....hhhh....',
    '...hhhhhh...',
    '...hhssss...',
    '...hssksss..',
    '....sssss...',
    '....cccc....',
    '...cccccc...',
    '..sccwwccs..',
    '..s.cccc.s..',
    '....pppp....',
    '....pppp....',
];

const PIERNAS = [
    [
        '...ss..ss...',
        '..mm....mm..',
        '..mm....mm..',
        '.kk......kk.',
    ],
    [
        '....ssss....',
        '....mmmm....',
        '....mmmm....',
        '....kkkk....',
    ],
];

const ICONOS = {
    copa: [
        'yyyyyyyy',
        'yyyyyyyy',
        '.yyyyyy.',
        '..yyyy..',
        '...yy...',
        '...yy...',
        '..yyyy..',
        '.kkkkkk.',
    ],
    tarjetas: [
        '...kkkkk',
        '...kyyyk',
        '.kkkkkyk',
        '.krrrkyk',
        '.krrrkkk',
        '.krrrk..',
        '.krrrk..',
        '.kkkkk..',
    ],
    cancha: [
        'wwwwwwwwwww',
        'wggggwggggw',
        'wwggwwwggww',
        'wwggwgwggww',
        'wwggwwwggww',
        'wggggwggggw',
        'wwwwwwwwwww',
    ],
    planilla: [
        '..kkkk..',
        'kkkwwkkk',
        'kwwwwwwk',
        'kwkkkkwk',
        'kwwwwwwk',
        'kwkkkkwk',
        'kwwwwwwk',
        'kwkkwwwk',
        'kwwwwwwk',
        'kkkkkkkk',
    ],
    barras: [
        '......y.',
        '......y.',
        '...r..y.',
        '...r..y.',
        'w..r..y.',
        'w..r..y.',
        'w..r..y.',
        'kkkkkkkk',
    ],
    calendario: [
        '.k....k.',
        'kkkkkkkk',
        'krrrrrrk',
        'kwwwwwwk',
        'kwkwkwwk',
        'kwwwwwwk',
        'kwkwkwwk',
        'kkkkkkkk',
    ],
    pelota: [
        '.wwww.',
        'wwkwww',
        'wkkkww',
        'wwkwkw',
        'wwwwww',
        '.wwww.',
    ],
};

const EQUIPOS = {
    rojo: {c: '#ff3b30', p: '#0e1f3a', m: '#ff3b30'},
    azul: {c: '#2f6bff', p: '#ffffff', m: '#2f6bff'},
    'arquero-rojo': {c: '#ffcc00', p: '#0e1f3a', m: '#ffcc00'},
    'arquero-azul': {c: '#ff8a00', p: '#ffffff', m: '#ff8a00'},
};

const BASE = {h: '#3b2416', s: '#f2b98a', k: '#0e1f3a', w: '#ffffff', y: '#ffcc00', r: '#ff3b30', g: '#1fb04f'};

// Convierte un dibujo en rectángulos SVG.
function pixeles(filas, colores, desdeFila = 0) {
    let svg = '';
    filas.forEach((fila, y) => {
        [...fila].forEach((letra, x) => {
            if (colores[letra]) {
                svg += `<rect x="${x}" y="${y + desdeFila}" width="1" height="1" fill="${colores[letra]}"/>`;
            }
        });
    });
    return svg;
}

// Arma un jugador con dos cuadros de animación (piernas abiertas y cerradas).
function jugador(equipo) {
    const colores = {...BASE, ...EQUIPOS[equipo]};
    const cuerpo = pixeles(CUERPO, colores);
    const cuadros = PIERNAS.map((p, i) =>
        `<g class="cuadro${i + 1}">${pixeles(p, colores, CUERPO.length)}</g>`
    ).join('');
    return `<svg viewBox="0 0 12 16" shape-rendering="crispEdges" aria-hidden="true">${cuerpo}${cuadros}</svg>`;
}

// Dibuja un ícono fijo (copa, tarjetas, cancha, etc.).
function icono(nombre) {
    const filas = ICONOS[nombre];
    return `<svg viewBox="0 0 ${filas[0].length} ${filas.length}" shape-rendering="crispEdges" aria-hidden="true">${pixeles(filas, BASE)}</svg>`;
}

// Reemplaza cada <span data-pixel="..."> por su dibujo: un jugador o un ícono.
document.querySelectorAll('[data-pixel]').forEach(el => {
    const tipo = el.dataset.pixel;
    el.innerHTML = ICONOS[tipo] ? icono(tipo) : jugador(tipo);
});
