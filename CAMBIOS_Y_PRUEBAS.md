# IA contextual de bots y frontera Chechenia–Kamchatka (octubre de 2026)

- Eliminada la conexión **Chechenia ↔ Kamchatka** de ambos lados de `PAISES_DATA`. Se conservan los otros territorios y las fronteras recíprocas.
- La IA consulta en cada decisión un estado resumido del tablero: territorios exclusivos por jugador (para la victoria general), control continental, concentración de tropas enemigas, oportunidades de misiones, amenazas y tropas incorporadas en el turno.
- Los bots **ya no usan lotes fijos de 2/3/4 ejércitos**: pueden incorporar 1 en un frente seguro o concentrar varios para defenderse o abrir una ofensiva. Siempre respetan los fondos continentales y libres, el bloqueo y las restricciones del motor.
- Ataques puntuados por oportunidad, ventaja militar, riesgo de contraataque, posible premio de tarjeta, objetivo personal, interrupción de continentes rivales y urgencia de frenar líderes cercanos a 45 países. Continúan calculándose tras cada tirada y mantienen las reglas de los condominios.
- Reagrupamiento estratégico desde la retaguardia hacia el frente mediante distancias en territorios propios; se reserva defensa en zonas amenazadas y nunca se vuelven a mover unidades recibidas durante el turno.
- Misiles reservados para amenazas o bloqueos reales; la diplomacia evita pactos de no agresión con rivales próximos a ganar o que se deban eliminar por misión. Se mantienen los perfiles existentes y el juego offline, sin dependencias externas de IA.
- **Pruebas locales**: 141 `unittest` aprobados (126 del ZIP base más 15 de `test_estrategia_bot_v18.py`); 125 simulaciones de 2 a 6 jugadores hasta cinco rondas (8.900 ataques y 4.989 conquistas registradas), sin excepciones. Las pruebas locales se ejecutaron sobre el código base empaquetado con estas modificaciones; los archivos se publicaron y se verificaron en GitHub. Validación visual manual pendiente.

---

# Mejora — Pantalla de victoria con objetivo alcanzado (octubre de 2026)

- Al concluir una partida, la pantalla de victoria identifica al jugador ganador (humano o bot), indica si alcanzó el objetivo general o sus misiones personales y muestra literalmente las descripciones de las tarjetas de misión correspondientes.
- Si gana por objetivo general, se detalla que ocupó **al menos 45 países** y la cantidad de territorios exclusivos controlados.
- Si gana por misión personal, se muestra el objetivo exacto; en partidas de dos jugadores se muestran las **dos misiones** exigidas por el motor.
- El motor guarda la causa de la victoria en `detalle_victoria`, que también utiliza la pantalla final; conserva la condición ya existente de prioridad del objetivo de 45 países.
- Se agregaron **8 pruebas nuevas** en `teg_revancha/test_correcciones_victoria.py`, incluyendo misiones de ocupación y eliminación, bots ganadores, visualización del mensaje y ausencia de triunfos prematuros. Se ejecutaron en el código base local (134 tests incluyendo estas 8) y se publicaron los cambios en GitHub. La apariencia gráfica final en Windows queda por validar.

---

# Versión 16 — Ajustes visuales y documentación (octubre de 2026)

- Se retiró la etiqueta flotante «REAGRUPE +N» (y «REAGRUPE MISIL») del mapa. Se conservan la línea de movimiento, la animación y la información de reagrupamiento en la columna izquierda.
- Se actualizó el README de la raíz basándose en el archivo entregado por el usuario para documentar las mejoras realizadas desde la versión 9 hasta la 16.
- No se modificaron las reglas de juego.

---

# Versión 14 — Cambio de color de una conquista después de visualizar el ataque (octubre 2026)

1. El resultado de `JuegoTEG.atacar` y los ataques contra condominios incluyen datos de los propietarios y ejércitos defensores anteriores a la tirada. Esto no cambia la mecánica de combate.
2. `Renderer` guarda instantáneas visuales temporales de países conquistados: 950 ms con el color y tropas previas, después cambia al dueño real. Es solo una presentación, no un retraso en la conquista lógica.
3. En la columna izquierda aparece el color atacante y el color defensor, junto a las bajas y la ruta. Si un país se utiliza inmediatamente como origen de un nuevo ataque, su transición se cierra para que no parezca que ataca el defensor derrotado.
4. La opción prepartida para desactivar animaciones sigue funcionando: sin efectos, el cambio de dueño es inmediato. Los ataques no conquistadores y los misiles no generan transiciones de propiedad.
5. Se añadieron 6 tests específicos (`test_correcciones_v14.py`) y se mantienen las 120 pruebas anteriores (**126/126**). Validación gráfica final pendiente de ejecutar con Pygame en Windows.

---

# Versión 12 — Tarjetas, combates animados y frontera Nigeria–Angola (octubre 2026)

1. **Máximo cinco tarjetas de país:** comprobado el control existente en `puede_solicitar_tarjeta()` y `solicitar_tarjeta()`; el botón se deshabilita al alcanzar cinco y los bots pasan el turno sin robar. Las tarjetas de continente son independientes del límite. Siete casos de regresión comprueban el límite, una quinta carta válida y la separación de continentes.
2. **Ataques más visibles:** línea luminosa animada entre país de origen y destino, aros pulsantes de ataque/defensa, proyectil desplazándose, etiquetas con los nombres y franja de identificación del jugador y las pérdidas. Se aplica a ataques propios, bots, enfrentamientos con condominios y lanzamientos de misil. La animación no modifica dados, turnos ni tropas.
3. **Conquistas:** indicador destacado en destino y aviso `PAÍS CONQUISTADO` que persiste aproximadamente cuatro segundos; el aviso anterior no desaparece al comenzar el siguiente ataque del bot. Se mantienen los popups de transferencia de tropas.
4. **Dados sin bloquear la batalla:** ventana de dados compacta desplazada a la esquina superior derecha del mapa, sin oscurecer el centro; conserva el motivo del cuarto dado y los resultados. La franja superior izquierda muestra las ubicaciones y el progreso del ataque.
5. **Frontera nueva:** Nigeria ↔ Angola, incorporada en ambos sentidos, sin modificar ninguna otra frontera. Tablero con 72 países y 137 conexiones bidireccionales.
6. **Pruebas:** siete tests nuevos en `test_correcciones_v12.py`; total **120 unittest**. 40 simulaciones de 2 a 6 jugadores y 8.929 pasos, 3.544 ataques y 2.047 conquistas sin errores. Compilación Python y paquete ZIP validados.

**Pendiente:** revisión visual sobre Windows con Pygame (no instalado en este entorno), especialmente dimensiones y duración de los indicadores cuando el bot está a 4x u 8x.

---

# Versión 11 — Dados, bloqueos, continentales y fronteras (octubre 2026)

1. **Aclaración de dados (pág. 12):** se respeta el cuarto dado reglamentario con defensores >=3 y fuerzas atacantes >=2x, incluso en Combate clásico. Se centralizó el cálculo entre batallas normales y condominios y se muestra la razón en la animación de dados y en el historial. Caso reproducido de tres tiradas sucesivas **3→4→3** sin viento.
2. **Bloqueos (págs. 18–19):** se validan tres o más vecinos, todos del mismo adversario con al menos dos tropas, se prohíben refuerzos/premios pero se permiten ataques, con las excepciones de preparación y último país. Los condominios no cuentan como un bloqueador unicolor.
3. **Tarjetas continentales (pág. 21):** la revocación de tarjeta no usada es inmediata al perder dominio, sea por conquista de un rival o creación/cambio de condominio. `opcion_canje()` y `canje_valido()` verifican la propiedad actual en cada consulta; no se permite gastar tarjetas obsoletas. Se recuperan al reconquistar, siempre que ese jugador nunca haya canjeado esa carta.
4. **Conexiones:** bajas de Nueva York–Terranova y Noruega–Bielorrusia (ambos sentidos), total 136 fronteras del grafo no dirigido.
5. **Pruebas de regresión:** nuevo `test_correcciones_v11.py` (15 casos); actualizado `test_reglas.py` con rutas de misiles y canjes con propiedad legítima conforme a las nuevas conexiones/reglas. **113/113 unittest**, 50 simulaciones de bots entre 2 y 6 jugadores hasta ronda 5/victoria, sin excepciones ni estados negativos.

La interfaz de Pygame debe verificarse visualmente en Windows (paquete no instalado en el entorno de pruebas).

---

# Versión 10 — Premios de tarjetas y canjes personales (octubre 2026)

1. **Canjes independientes:** la serie 6, 10, 15, 20, 25… es por jugador. Antes se usaba `canje_numero` global y el humano podía recibir 10 en su primer canje si un bot había hecho el primero de la partida. Ahora `valor_canje(jugador=None)` usa `jugador.canjes_realizados`; `canje_numero` continúa contando el total de canjes de la partida sin alterar los valores personales. Aplica también a canjes de bots y tarjetas continentales. El historial identifica el ordinal del canje del jugador.
2. **Premios +3 verificados:** la carta de un país que el jugador controla acredita automáticamente tres ejércitos al robarla. Si la carta ya se posee pero el país se conquista más tarde, el premio se concede al entrar en la etapa TARJETA de ese turno. Se concede una vez por carta durante su posesión, sin consumirla. Se mantienen las excepciones oficiales: bloqueo y zona internacional vigente, con acreditación pendiente si cesa la restricción.
3. **Tarjetas heredadas:** se corrigió un caso de premio omitido: al eliminar a otro jugador, sus tarjetas pasaban al vencedor, pero el motor las marcaba todas como si ya hubieran dado +3. Ahora las tarjetas transferidas pueden dar premio al nuevo titular al finalizar su turno si controla el país.
4. **Interfaz:** el popup de tarjeta obtenida muestra si acaba de acreditarse +3, si está pendiente por bloqueo/zona, o si el premio podrá ganarse conquistando el país mientras se conserve la carta.
5. **Regresión:** ocho pruebas nuevas en `test_correcciones_v10.py`, desde canjes cruzados con bots hasta premios por posesión, conquista, bloqueo y herencia; 98 pruebas totales.

**Verificación:** `python -m unittest -q test_reglas test_pactos test_correcciones_v7 test_correcciones_v8 test_correcciones_v9 test_correcciones_v10`, compilación de todos los módulos y paquete ZIP íntegro. La interfaz Pygame requiere prueba visual en Windows.

---

# Versión 9 — Compra de misiles sin bonos continentales (octubre 2026)

1. **Cierre corregido:** `incorporar_misil()` en `logic.py` lanzaba `KeyError` al comprar un misil en un país de un continente que no figuraba como clave en `refuerzos_continente`. Se verificó que ocurría también fuera de Oceanía. Ahora solo se descuenta el fondo continental si efectivamente financia parte del costo.
2. **Saldos correctos:** se sigue exigiendo el costo de 6 refuerzos, consumiendo primero los disponibles de ese mismo continente y luego los libres. Bonos de otros continentes quedan intactos. La conversión de 6 ejércitos existentes funciona sin cambiar el saldo de refuerzos.
3. **Pruebas:** `test_correcciones_v9.py` agrega 9 casos: reproducción del error de Oceanía, todos los continentes, bonos de otro continente, insuficiencia de refuerzos libres, bono propio, bono agotado, conversión, compras inválidas y recorrido de una partida real desde la preparación a la ronda 2. Se vuelven a ejecutar todos los tests anteriores.

**Verificación:** `python -m unittest -q test_reglas test_pactos test_correcciones_v7 test_correcciones_v8 test_correcciones_v9`; `python -m py_compile *.py`; ZIP íntegro. Pygame gráfico: pendiente de ejecutar en Windows.

---

# Versión 8 — Correcciones de fronteras, Chukchi, situaciones y pantalla de pactos (octubre 2026)

1. Se eliminó el texto «Las imágenes corresponden a tus tarjetas de misión.» del popup de objetivos.
2. Se corrigió `Chokchi` a **`Chukchi`** en `PAISES_DATA`, mazo y símbolos de tarjetas, así como `coords_calc.py` y `mapa_ui.jpg`; el mapa original fuente se mantiene.
3. No se extraen ni se muestran situaciones en ronda 1; el estado es Clásico y el mazo sigue con 50 tarjetas. Desde la segunda ronda se roba una carta y se muestra el popup.
4. Se sumaron **11 fronteras bidireccionales** y se retiraron **6**, según la lista de esta versión. Se mantienen **72 países y 138 conexiones**, todos conectados. El código de fronteras está ordenado un país por línea para permitir revisiones.
5. `descripcion_pacto` dejó de construir anticipadamente referencias específicas de todas las variantes. El error **`KeyError: 'paises'`** al abrir Pactos después de firmar un acuerdo mundial queda corregido y probado con el mismo flujo `Renderer.mostrar_pactos`. Se verifican también continente, frontera, país, condominio y ruptura pendiente.

**Validación:** tests `python -m unittest -q test_reglas test_pactos test_correcciones_v7 test_correcciones_v8`; compilar módulos; comprobar ZIP. Pygame gráfico pendiente de comprobación en Windows.

---

# Versión 7 — Asientos de objetivos, propuestas visibles y corrección de KeyError (octubre 2026)

1. **Objetivos de destrucción:** se usa `orden_base` como referencia de asientos fija, no `orden_ronda`, que solo rota al primer jugador. Si el objetivo es un color ausente o el color propio, ahora apunta a la **derecha = jugador anterior** en el orden inicial (antes se apuntaba erróneamente al siguiente). El objetivo explícito **izquierda** se ajusta al siguiente. La misión muestra claramente la alternativa y el rival real.
2. **Error de propuesta de bot:** al aceptar no agresión, el objeto es un pacto sin `estado` ni `tiradas`; se eliminaron los accesos incorrectos. `respuestas_pactos.py` distingue los resultados de no agresión y ofensiva conjunta, rechazo e imposibilidad. Incluye prueba que recorre `manejar_pactos` del `main.py` con Polonia–Albania y verifica que ya no lanza `KeyError: 'estado'`.
3. **Propuesta en panel derecho:** el mapa NO se oscurece ni se cubre. Se resaltan con anillos y etiquetas los países implicados, con índice 1/2 (o 1/2/3 en agresión conjunta); el panel lateral muestra nombres completos, participantes, ejércitos y misiles para valorar la conveniencia.
4. **Inspección libre:** durante la decisión se permite pasar el cursor y hacer clic para inspeccionar cualquier país sin mover ejércitos. A/R y botones a la derecha para responder; Esc no cierra la negociación en curso.

**Validación:** 65/65 tests (`test_reglas`, `test_pactos`, `test_correcciones_v7`); 60 simulaciones adicionales (2–6 jugadores) que aceptaron 61 propuestas sin excepciones ni valores negativos; `py_compile` correcto. Falta ejecutar Pygame gráficamente en Windows: no instalado en este entorno.

---

# Versión 6 — Clic derecho, diplomacia, pactos y condominios (octubre 2026)

1. **Menú contextual en fichas del tablero:** selección de origen y destino y acciones según fase. Con clic derecho en destino se puede atacar sin volver a la barra lateral; también refuerzos, misiles, reagrupes y ventana diplomática.
2. **Botón ATACAR:** se retiró el texto «Máx. dados» sin modificar el cálculo automático de dados.
3. **Motor de pactos:** módulo nuevo `pactos.py` con las cuatro formas de no agresión (dos países, continente, frontera de continentes, mundial), efectos obligatorios para ataques y misiles, registros públicos y ruptura diferida.
4. **Zonas internacionales:** alternancia obligatoria sobre país de una ficha, disponibles a partir del tercer canje; penalización según cartas en mano, decisión del perjudicado, restricción de ocupación y reagrupamiento, suspensión del premio de tarjeta.
5. **Agresiones conjuntas y condominios:** posibilidad de acordar turno del líder, tiradas alternadas y asalto obligatorio; guarniciones separadas y fichas bicolores en países compartidos, reglas de conquista, pausa voluntaria del asalto desde condominio, ataques internos tras ruptura, ataques de terceros y desplazamientos especiales de ambos socios.
6. **Bots:** decisiones voluntarias de firma, rechazo u ofrecimiento de pactos, con aplicación de las mismas prohibiciones militares a todos los jugadores.
7. **Interfaz diplomática:** tecla P, visor de pactos vigentes, propuestas y rupturas, decisiones sobre sanciones de zonas, aceptación del humano ante propuestas de bots y opciones de reagrupe extraordinario tras conquista conjunta.

**Pruebas:** 55 pruebas unitarias (`test_reglas` + `test_pactos`), 55 simulaciones de 2–6 jugadores con controles de propiedad y guarniciones, sintaxis Python y ZIP verificado. No se realizó prueba gráfica real porque Pygame no está disponible en el entorno: verificar en Windows.

---

# Versión 5 — Símbolos rotados, desglose de refuerzos, mazo y misiles (octubre 2026)

1. Rotación exacta de los cinco iconos de tarjetas de país (`iconos_cartas/*.png`) **90° en sentido horario**, sin pérdida de píxeles; escala proporcional en el visor.
2. Incorporación desglosada visualmente. `JuegoTEG.desglose_incorporacion()` devuelve el saldo libre y los pendientes de cada continente. El panel muestra cada cuenta y actualiza sus números con las colocaciones y conversiones en misil. Las bonificaciones de continente sólo se pueden colocar allí.
3. Mazo físico de 50 situaciones. 20 Clásico, 4 × cada uno de los seis eventos comunes, y un Descanso por color. Extracción sin reposición hasta agotar, entonces barajado del descarte. Si la carta fue Descanso de un color **que no participa o fue eliminado**, no se repone: se descarta y aplica Clásico, respetando la variante indicada por el usuario (el reglamento original propone sacar otra).
4. Misiles visibles. Sprite nuevo de misil negro metalizado, renderizado sobre el borde izquierdo de cada token; para dos o más, marcador numérico encima. Se muestra la cantidad en el HUD del país.
5. Misiles capturados. Se confirma y documenta que **al conquistar un país se conservan sus misiles y pasan al conquistador**. El motor ya mantenía ese estado; se añadió línea de historial explícita y una prueba que captura dos misiles y dispara uno desde el territorio conquistado.

**Pruebas:** 41/41 `unittest` correctos; 50 simulaciones adicionales de 2 a 6 jugadores y hasta 250 pasos cada una, sin ejércitos/misiles negativos; comparación pixel a pixel de iconos rotados, sintaxis Python OK. Verificación gráfica real pendiente por imposibilidad de instalar Pygame en este entorno.

---

# Versión 4 — Situaciones, objetivos ilustrados, turnos conjuntos e IA (octubre 2026)

1. **Popup de situación por ronda.** Se muestra al empezar cada ronda de hostilidades, antes del primer paso humano o del bot; para continuar se requiere ACEPTAR. Esc no lo descarta. Incluye una explicación del efecto y los afectados por Crisis.
2. **Objetivos de destrucción opcionales.** Checkbox en menú, habilitado por defecto; en 4-6 jugadores se excluyen los objetivos de destrucción al desmarcarlo. Para 2 y 3 sigue la restricción anterior (sin eliminación).
3. **Corrección estructural de los turnos desde la ronda 2.** Etapa de INCORPORACIÓN para todos los jugadores activos, en el orden rotativo; solo después se habilita ATACAR para el primero, y continúan ATACAR → REAGRUPAR → TARJETA para cada uno. Preparación y ronda 1 se conservan. Se introdujeron `etapa_ronda` e `incorporaciones_completadas`.
4. **Imágenes reales de objetivos.** 17 tarjetas recortadas del PDF original y 2 creadas para misiones presentes en código pero sin imagen equivalente. Se giran 90° en sentido horario las de páginas 1-2; las de página 3 están verticalmente legibles sin girar. El PDF tiene un duplicado de la misión Europa+4 Asia+4 Sudamérica y no contiene la imagen de Oceanía+África+4 América Central+4 Asia; tampoco contiene «destruir Blanco» (contiene «destruir Magenta»). Las cartas «Descanso» no se utilizan como objetivos. Imágenes guardadas en `teg_revancha/objetivos_imagenes/` con índices `00` a `18`. Ver carta a tamaño completo con O.
5. **Bots más variados.** Cinco estilos asignados sin repetir (Agresivo / Defensivo / Objetivo / Oportunista / Equilibrado), ponderación de países conforme a la misión, amenazas vecinas, debilidades, equilibrio ofensivo/defensivo, penalización por refuerzos repetidos y reagrupes de apoyo. Todos los movimientos pasan por las funciones de reglas.

**Validación:** 35 pruebas `unittest`, compilación sintáctica, 25 simulaciones adicionales hasta ronda 5 o victoria (2-6 jugadores), verificando que no se crean ejércitos negativos ni se pierden territorios sin dueño. Pygame no está instalado en el entorno y no se pudo descargar, por lo que la verificación gráfica real queda pendiente de ejecutar en Windows. El ZIP sigue incluyendo archivos originales y el reglamento.

---

# Actualización — Conexiones, interfaz y refuerzos (octubre de 2026)

## Lo solicitado en esta revisión

1. **Tablero:** se agregaron las 14 fronteras indicadas y se quitaron las 23 sobrantes, siempre en ambos sentidos. Los nombres de `data.py` se conservan sin tildes por compatibilidad. Hay 133 conexiones únicas entre 72 países. El grafo es conexo y ningún país queda aislado.
2. **Refuerzos:** ahora se aplica `max(4, cantidad_paises // 2)` durante las rondas regulares, incluyendo 6 y 7 países, donde antes se otorgaban erróneamente tres ejércitos. Se mantienen los bonos por continente, situación, canjes y la primera ronda especial.
3. **Interfaz:** panel oscuro rediseñado con fuente nítida, contraste, tarjetas informativas, pistas de acciones, marcadores de fase, fichas visibles, nuevas ventanas de objetivos e historial y portada visual. El mapa de alta resolución se mantiene y se añadió la versión optimizada `mapa_ui.jpg` para acelerar el inicio.
4. **Orden visual rotativo:** se usa el orden real de la ronda (`orden_visual_jugadores` basado en `orden_ronda`), no la lista fija de jugadores. Los eliminados quedan al final.
5. **Mapas:** se dejó de dibujar la antigua lista rígida de líneas marítimas, porque incluía conexiones ahora descartadas; sólo se resalta un par seleccionado que el motor confirma como adyacente.

## Pruebas de esta entrega

- 31 pruebas de `python -m unittest -v test_reglas`: **OK**, incluyendo 37 modificaciones de fronteras, mínimo 4, y rotación visual.
- Prueba del grafo: 72 países, 133 fronteras, 1 componente conexa, 0 países aislados.
- 100 simulaciones parciales de juego (20 semillas por 2 a 6 jugadores, 11.480 pasos): **sin excepciones ni ejércitos negativos**.
- `python -m py_compile *.py`: **OK**.
- **Pendiente de verificación visual en Windows:** no fue posible instalar ni ejecutar Pygame en el entorno de validación por falta de acceso al paquete. Los cambios de interfaz se revisaron por código, no mediante ejecución gráfica real.

---

# Historial de cambios de la versión anterior (v2) — Octubre de 2026

## Nuevos respecto de la versión ZIP anterior

1. Se elimina el ataque voluntario con 1 dado. El motor siempre calcula el máximo permitido; el panel tiene un único botón de ataque.
2. Se sortea el orden inicial de jugadores. Cada nueva ronda rota el orden: primer jugador al último puesto. La preparación y la primera ronda mantienen el orden sorteado.
3. El menú permite elegir los seis colores oficiales; se ajustan nombres, fichas, situaciones de descanso y misiones de eliminación al color asignado.
4. Se divide la IA en pasos (`paso_bot`): cada decisión se anima en el loop de Pygame sin bloquear eventos. Velocidades PAUSA/1x/2x/4x/8x, con tecla F y control visual. Se resaltan país origen y destino y se muestran dados en ataques.
5. Los 72 símbolos de tarjetas ya **no son aleatorios**. `FIGURAS_POR_PAIS` en `data.py` contiene la asignación real de las cartas del PDF: cuatro soldados, cinco granadas y veintiuna cartas de cada uno de los otros tres símbolos.
6. Se incorporó una fase TARJETA después de reagrupar: el jugador solicita explícitamente una sola carta, sujeto al mínimo de 1 o 2 conquistas y el límite de cinco cartas. La carta no se roba sin pulsar el botón.
7. Visor completo de cartas propias y rivales con pestañas, paginación, figuras recortadas del PDF y selección manual de país/continente para canjes.
8. El motor ofrece `canje_valido` para validar combinaciones elegidas. Los bots conservan elección automática de canje.
9. Se añadieron pruebas de las correspondencias del PDF, orden y rotación, colores, dados máximos, solicitud explícita, límite de cartas y canjes seleccionados.

## Resultados

- 28 pruebas automáticas del motor: **OK**.
- 100 simulaciones adicionales con 2, 3, 4, 5 y 6 jugadores (20 semillas por configuración): **sin excepciones ni ejércitos negativos**.
- Compilación sintáctica del código: **OK**.
- Interfaz gráfica: **no ejecutada aquí**, porque Pygame no está instalado y no se pudo descargar debido a restricciones de red.

## Limitaciones

Pactos especiales, condominios, reparto colectivo de refuerzos extras y guardado de partidas todavía no están implementados. Ver README para detalles y aclaración sobre discrepancias en figuras de las tarjetas continentales.
