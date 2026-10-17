# TEG La Revancha — versión 9 (octubre de 2026)

Juego Python + Pygame para **1 humano y entre 1 y 5 bots**; compatible con Windows (doble clic en `INICIAR_JUEGO.bat`) o terminal (`pip install -r requirements.txt` y `python main.py` desde `teg_revancha`). Requiere Python 3.10+ y pantalla preferentemente 1600 × 900; Pygame escala la interfaz a pantallas más pequeñas.

## Corrección de la versión 9: compra de misiles en incorporación

- **Solucionado el cierre `KeyError: 'Oceania'`** de `logic.py` al comprar un misil durante la segunda ronda. Sucedía cuando no se disponía de un bono del continente en el país seleccionado: se intentaba modificar una clave inexistente en `refuerzos_continente`. El mismo error podía darse en cualquiera de los siete continentes.
- La compra descuenta exactamente **6 ejércitos** del saldo pendiente. Si hay bonificaciones del continente correspondiente, se consumen primero; de lo contrario, se utilizan solamente refuerzos libres. Nunca se descuentan bonificaciones reservadas para otros continentes.
- Se conserva la conversión de seis ejércitos presentes en el país a un misil, siempre que quede al menos un ejército.
- **Regresión:** `python -m unittest -q test_reglas test_pactos test_correcciones_v7 test_correcciones_v8 test_correcciones_v9` (90 pruebas). Incluye el flujo de una partida real hasta la segunda ronda, las siete regiones y compras con/sin bonificaciones.

## Novedades de la versión 8: mapa, primera situación y pactos sin cierres

- **Misiones:** quitado el renglón auxiliar de las tarjetas gráficas de objetivo.
- **Chukchi:** nombre corregido en datos del país, conexiones, tarjeta, coordenadas de desarrollo y etiqueta impresa del mapa **que usa Pygame** (`mapa_ui.jpg`). Se conserva `mapa.jpg` como copia fuente original sin alterar.
- **Primera ronda:** no se extrae ni muestra ninguna tarjeta de situación en ronda 1. Todos atacan con Combate clásico; desde la ronda 2 se extrae exactamente una tarjeta y se muestra el aviso obligatorio. El mazo conserva sus 50 cartas hasta la segunda ronda.
- **Fronteras v8:** se incorporan 11 enlaces (India–Malasia, Chile–Brasil, Oregón–Terranova, Nigeria–Sudáfrica, Egipto–Polonia, Turquía–Rusia, Turquía–Irak, Turquía–Irán, Albania–Irán, China–Chukchi, China–Siberia) y se quitan 6 (Turquía–Malasia, Bielorrusia–Rusia, Angola–Sudáfrica, Egipto–Arabia, Egipto–Croacia, China–Irán). Son bidireccionales; el grafo final tiene **72 países y 138 conexiones**, todos alcanzables. Se aplican los cambios nuevos aunque reviertan conexiones de versiones antiguas.
- **Pactos:** solucionado `KeyError: 'paises'` al abrir **PACTOS [P]** después de firmar uno mundial. El tipo de acuerdo decide qué campos leer: entre países, continental, frontera entre continentes, mundial o condominio. Las rupturas siguen visibles.

**Pruebas v8:** `python -m unittest -v test_reglas test_pactos test_correcciones_v7 test_correcciones_v8`. También se validó el orden de fases, el consumo de una sola tarjeta desde ronda 2 y la navegación por PACTOS [P] al aceptar un pacto mundial. Pygame no está instalado en el entorno de pruebas, por lo que la comprobación final de los menús en Windows sigue siendo necesaria.

## Novedades de la versión 7: diplomacia legible y objetivos de destrucción

- **La derecha es una posición de mesa fija.** Si una misión manda destruir un color ausente o el propio, el reemplazo será **el jugador que figura inmediatamente ANTES que vos en el orden inicial** (la derecha según la convención de esta edición digital); si está al principio, se toma el último. Las rotaciones del primero en cada ronda **no alteran los vecinos de asiento**. El objetivo explícito de eliminar al de la izquierda apunta al siguiente del orden inicial. La descripción de la misión muestra el nombre del objetivo reemplazante y el motivo.
- **No más cierre al aceptar la propuesta de un bot:** los resultados de **no agresión** son pactos con `tipo`, `id` y `paises`, y los de **ataque conjunto** tienen `estado` y `tiradas`. Se procesan por separado. Se añadieron pruebas de aceptación y rechazo, incluyendo el flujo de `main.py` que producía `KeyError: 'estado'`.
- **Propuestas sin tapar el mapa:** los avisos de pacto de bots ahora se muestran **solo sobre el panel derecho**, nunca como ventana oscura centrada. Los países que participan se rodean y numeran (1: territorio del bot, 2: tu territorio, 3: objetivo de una agresión conjunta), con etiquetas legibles junto a las fichas y una ficha descriptiva en el panel. En las fichas de la propuesta aparecen nombres, colores participantes, tropas y misiles.
- **Mapa consultable durante la propuesta:** mover el cursor o hacer clic sobre cualquier ficha muestra el nombre del país, dueño, ejércitos y misiles, sin activar movimientos ni ataques. El turno permanece en pausa hasta resolver el pacto. Se responde con los botones del panel derecho o con **A** para aceptar / **R** para rechazar. **Esc no oculta la negociación**, para no dejar un pacto pendiente sin resolver.

**Pruebas v7:** ejecutar `python -m unittest -v test_reglas test_pactos test_correcciones_v7`. Las nuevas pruebas incluyen el mapa inspeccionable y las propuestas con países cercanos (Polonia/Albania), además de la elección por asientos. Como no se dispone de Pygame aquí, sigue siendo necesaria una revisión visual en Windows.

## Novedades de la versión 6: clic derecho y pactos públicos

- **Menú contextual con clic derecho sobre una ficha del mapa:** en incorporación, añadir +1/+3/+10 ejércitos y crear/convertir misiles; en ataque, marcar origen o atacar/lanzar misil desde el destino seleccionado; en reagrupamiento, seleccionar origen o mover ejércitos/misil. Se conserva el panel lateral. Tras marcar origen, hacé **clic derecho en el destino** para ejecutar la acción sin desplazar el cursor a los botones de la derecha.
- **Botón de ataque simplificado:** el texto es solo **ATACAR**; se siguen tirando automáticamente todos los dados permitidos.
- **Diplomacia pública [P]:** tipos de no agresión del reglamento: entre dos países a hasta tres fronteras (incluidos países dentro del alcance misil), dentro de un continente, en una frontera de continentes o mundial. Son **vinculantes** después de aceptados: bloquean ataques y misiles entre firmantes en el alcance acordado. El historial deja registro y se ven en un tablero de pactos. La ruptura anunciada requiere esperar hasta finalizar el siguiente turno del otro firmante; ciertas conquistas de terceros terminan el pacto.
- **Zonas internacionales:** disponibles después del tercer canje, una por jugador a la vez, sobre país de un ejército fronterizo a ambos; se exige conquista alternada y ocupación con un solo ejército; prohíbe reagrupar hacia esa zona. Incumplir retira aleatoriamente una tarjeta de país, o quita el próximo derecho a obtenerla. El perjudicado puede mantener o cancelar la zona. No se entrega el premio de +3 ejércitos de su tarjeta mientras esté vigente.
- **Pactos de agresión obligatorios:** dos colores pueden pactar un ataque común contra un tercero y determinar **el turno de cuál firmante**. Las tiradas alternan entre ellos y continúan hasta ocupar el objetivo o agotar las fuerzas legales. Si conquistan, se crea un país **en condominio**, con guarniciones diferenciadas de cada color, 1–2 ejércitos de ocupación por firmante y el reagrupamiento extra del socio antes del próximo turno. Se generan los pactos automáticos de no agresión entre países agresores y en el condominio. El premio de tarjeta por esta modalidad requiere dos conquistas conjuntas. Los aliados también pueden atacar en conjunto desde un condominio, sin obligación de continuar.
- **Condominios y terceros:** se dibujan fichas compartidas mostrando los dos colores y sus ejércitos; se permite elegir qué guarnición atacar en cada tirada. Un tercero puede expulsar a uno y convertirse en nuevo copropietario, sin pacto automático de no agresión. El pacto interno entre dueños originales tiene reglas de ruptura y ataque desde adentro.
- **Bots negociadores:** pueden aceptar o rechazar los acuerdos que propone el humano y ocasionalmente ofrecer no agresión o una agresión conjunta. Los pactos firmados limitan también sus decisiones militares.

**Cómo proponer:** seleccioná con clic izquierdo un **país tuyo** como origen y otro país del mapa como destino; pulsá **P** o la opción de pactos en el menú contextual. Elegí el tipo de acuerdo. Para pactar una agresión, el destino es el país **tercero** y la ventana siguiente ofrece aliados limítrofes. Los pactos mundiales se pueden proponer desde P aun sin países seleccionados. La lista de P también permite anunciar rupturas y administrar asaltos voluntarios.

## Novedades de la versión 5

- **Símbolos de tarjetas:** los 5 PNG de `iconos_cartas/` (soldado, granada, tanque, avión y barco) fueron girados **90° en sentido horario**, conservando transparencia y calidad. El visor de tarjetas los muestra adaptados al tamaño de la carta.
- **Refuerzos desglosados en el panel:** durante INCORPORAR, arriba se ve el total pendiente; abajo, en **verde**, los refuerzos **LIBRES · EN CUALQUIER PAÍS**, y en **dorado** la cantidad que se debe colocar **obligatoriamente en cada continente controlado**. Las cifras se actualizan tras cada incorporación o compra de misil. Los libres abarcan países, canjes y situación de refuerzos extras. No se pueden gastar refuerzos continentales fuera de su continente.
- **50 tarjetas de situación reales:** 20 Clásico, 4 Nieve, 4 Crisis, 4 Viento a favor, 4 Refuerzos extras, 4 Fronteras abiertas, 4 Fronteras cerradas y 1 Descanso por cada uno de los seis colores. Cada tarjeta se **extrae y descarta sin reposición**; al agotar el mazo se baraja el descarte. Si sale un descanso de un color que no está jugando o fue eliminado, **esa tarjeta se consume y se aplica Clásico**, sin volver a extraer; esta es la variante solicitada en lugar de robar otra, como indica el manual.
- **Misiles visibles junto a las fichas:** se añadió `iconos_ui/misil.png` (sprite vertical con transparencia), que se muestra **a la izquierda de cada país con misiles**, superpuesto ligeramente al círculo de tropas. Un misil se ve sin número; si hay dos o más, se muestra la cantidad sobre el icono. El visor de información del país también informa el número de misiles.
- **Misiles al conquistar:** los misiles del país defensor **se capturan junto con el territorio**, no se retiran ni se convierten en ejércitos. El vencedor puede utilizarlos para atacar desde ese país en su misma etapa de ataque. Una línea del historial hace visible la captura. Se mantienen costo 6 ejércitos, defensa antimisiles, alcance de 1-3 fronteras, daño 3/2/1, prohibición de aniquilar hasta cero y ausencia de defensa frente a dados.

**Pruebas v5:** 41 tests automatizados correctos, 50 simulaciones adicionales (10 con cada tamaño de 2 a 6 jugadores), validación exacta de rotación de los 5 PNG, compilación correcta. No se pudo hacer una ejecución gráfica de Pygame porque el paquete no está instalado y la conexión al índice de paquetes está restringida; se debe validar la interfaz ejecutando el juego en Windows.

## Inicio y turnos

- Elegí **cantidad de participantes y color** (blanco, negro, rojo, azul, amarillo o verde), y activá o desactivá **objetivos de destrucción** desde el menú inicial. Para partidas con 2 o 3 jugadores ya están excluidos por las reglas existentes. Los bots reciben colores diferentes.
- El orden inicial de los jugadores se **sortea**. Se conserva durante la preparación (8 + 4 ejércitos, o 18 para dos participantes) y en la primera ronda de hostilidades. Al finalizar cada ronda se rota: el primero pasa al último puesto. **El panel también cambia el orden visual de los jugadores y sus fichas de color**, sin alterar la identidad de cada jugador.
- **Aviso de situación:** desde la **segunda ronda** de hostilidades se muestra un popup obligatorio con la carta de situación y su efecto. Hay que pulsar **ACEPTAR** para continuar; no se puede cerrar con Esc. Se muestra también si el primero de la ronda es un bot.
- **Rondas desde la segunda:** la incorporación es una **vuelta global**: todos colocan sus refuerzos antes de comenzar cualquier ataque. Terminada esa vuelta se vuelve al primer jugador de la ronda, que empieza ATACAR. La primera ronda de hostilidades sigue sin refuerzos.
- En **INCORPORAR**, clic izquierdo sobre un país propio para añadir una tropa. Clic derecho sobre él para desplegar +1/+3/+10 y creación/conversión de misiles.
- En **ATACAR**, seleccioná país de origen y rival y pulsá **ATACAR** o hacé clic derecho en el destino y elegí **Atacar con dados**. Se usan automáticamente todos los dados que permiten las reglas (incluido el cuarto condicional); no existe ataque de un solo dado. Tras conquistar, elegí entre 1 y 3 ejércitos para ocupar el territorio. Los misiles se disparan con el botón correspondiente.
- En **REAGRUPAR**, seleccioná dos países propios limítrofes para mover ejércitos o misiles, o usá clic derecho sobre el destino con un origen ya seleccionado. También podés pasar a la fase siguiente.
- En **TARJETAS**, si conquistaste al menos 1 país (o 2 desde tu tercer canje) podés pulsar **SOLICITAR TARJETA**: se obtiene **una sola carta de país al azar**. Nunca se entrega automáticamente. Si finalizás el turno sin solicitarla, se pierde el derecho.

## Fronteras y refuerzos revisados en esta versión

- Se aplicaron **14 conexiones nuevas** y **23 eliminaciones en v3**, seguidas de **11 altas y 6 bajas en v8**, exactamente como las enumeró el usuario (en ambas direcciones). Están escritas en las listas de `PAISES_DATA` de `data.py` y comprobadas en `test_reglas.py`.
- El grafo resultante tiene **72 países y 138 fronteras bidireccionales**, sin países aislados y con todos los territorios conectados.
- La incorporación base durante las rondas normales es **`max(4, países_controlados // 2)`**, con mínimo cuatro ejércitos incluso si se poseen 6 o 7 países. Se suman como antes los bonos continentales, situación y canjes. La primera ronda de hostilidades conserva su regla especial sin incorporar ejércitos.
- Las conexiones resaltadas por la interfaz se comprueban contra el tablero actualizado: **no se muestran enlaces eliminados**. El JPG del mapa original se conserva intacto.

## Interfaz renovada

- Ventana lógica de **1600 × 900**, con mapa de **1200 × 900** a la izquierda y dashboard de **400 px** a la derecha; `pygame.SCALED` adapta la ventana a pantallas menores.
- Mapa **`mapa_ui.jpg`** precalculado con remuestreo de alta calidad para mejorar nitidez y arranque. El `mapa.jpg` oficial de alta resolución **sigue presente** como fuente original.
- Tipografía del sistema antialias, colores más contrastados, fichas de mayor visibilidad, detalles vectoriales de globo, botones rediseñados, fases con indicadores visuales, objetivos y contadores en tarjetas, y ayuda contextual sobre el mapa.
- Los colores se ordenan según **`orden_ronda`** durante la ronda y rotan visualmente cuando rota el turno. Los participantes eliminados quedan al final.
- El panel incluye accesos siempre accesibles a **PACTOS [P]** y a: **CARTAS (T)**, **MISIÓN (O)**, **HISTORIAL (H)** y **VELOCIDAD BOT (F)**. Los objetivos completos y hasta los últimos 23 eventos se muestran en ventanas ampliadas para evitar texto recortado con 5-6 jugadores.

## Tarjetas ilustradas de objetivos

El archivo `Tarjetas objetivos.pdf` está incorporado al ZIP. Las cartas del PDF fueron recortadas y giradas **90° en sentido horario en las páginas 1 y 2** para que se lean en formato apaisado; la tercera página ya tenía la orientación correcta. Se utilizan en la ventana **MISIÓN [O]** y como miniaturas en el panel. Se omiten las cartas de DESCANSO de ese PDF (la mecánica de descanso del mazo de situación permanece).

**Excepciones del material gráfico aportado:** el PDF incluye dos veces el objetivo de Europa + 4 Asia + 4 Sudamérica, pero no trae la imagen de «Oceanía, África, 4 América Central y 4 Asia». Además, la carta de «destruir Magenta» no coincide con el color Blanco del motor. Para evitar representar misiones incorrectas se han dibujado dos tarjetas propias, una para dicha ocupación y otra para **destruir Blanco**. Todas las misiones activas tienen una imagen; la lógica de objetivos anterior se conservó. Si se desactiva el modo eliminación en 4-6 jugadores solo se reparten objetivos de ocupación.

## Bots con estrategias diferentes

Cada rival recibe al comenzar uno de cinco estilos distintos (sin repetir mientras haya hasta cinco bots): **Agresivo**, **Defensivo**, **Objetivo**, **Oportunista** o **Equilibrado**. Sus estilos afectan la colocación de refuerzos, la concentración o distribución de tropas, la selección de ataques, el uso de misiles y el reagrupamiento; la decisión sigue validándose en el motor y varía según sus objetivos. Se informa la asignación de perfiles en el historial. No se implementa búsqueda exhaustiva de jugadas ni un oponente infalible.

## Cartas y canjes

La correspondencia de las **72 cartas de país con los símbolos** se transcribió del archivo `Tarjetas países.pdf` aportado: 4 soldado, 5 granada, 21 tanque, 21 avión y 21 barco. Las cartas de soldado son comodines; **Angola, Alemania, Albania y Alaska** son las cuatro de soldado. **No se inventan supertarjetas** entre las cartas que aparecen en este PDF.

Abrí **TARJETAS [T]** desde cualquier fase. Se puede recorrer la mano del humano o de cualquiera de los bots, incluso cambiar de página si hay muchas cartas. Durante la fase de incorporación, seleccioná las cartas de país y/o continente que deseás usar y pulsá **CANJEAR** cuando la combinación sea válida. No hay selección automática para el humano. Los bots sí eligen sus propias combinaciones. El canje consume las cartas elegidas y otorga **6, 10, 15, 20, 25…** ejércitos; como máximo uno por jugador y ronda.

- Son válidos tres símbolos iguales o tres distintos, considerando el soldado como comodín.
- América del Norte, Europa y Asia permiten un canje por sí solas; América del Sur y África representan dos símbolos; América Central y Oceanía uno. Estas equivalencias se toman del *reglamento*, página 26.
- Las tarjetas de continente **no salen del mazo**: sólo se obtienen al controlar completamente el continente y se pierden si deja de controlarse antes de usarse.
- Las cartas de país dan **+3 ejércitos** una sola vez al ocupar el país correspondiente.
- El reglamento establece que la **cantidad** de tarjetas de cada rival es pública, no sus identidades. Por pedido del usuario, esta implementación usa **manos abiertas**, donde es posible ver también las figuras y países de los bots.

**Nota de fuentes:** en algunas tarjetas continentales, los símbolos dibujados en `Tarjetas países.pdf` difieren de las equivalencias descritas en la página 26 de `TEG-REVANCHA-REGLAS.pdf`. Para determinar canjes prevalece el texto del reglamento oficial, tal como se solicitó. Para las **72 tarjetas de país**, se usan exactamente los símbolos dibujados en el nuevo PDF.

## Velocidad de bots

En la parte inferior del panel derecho están **CARTAS [T]**, **MISIÓN [O]**, **LOG [H]**, **PACTOS [P]** y **BOT 1x [F]**. El de velocidad del bot cambia entre **PAUSA → 1x → 2x → 4x → 8x** (se puede pulsar `F`). En 1x, el bot realiza una decisión visible cada ~1,1 segundos; pueden verse refuerzos, ataques, dados, conquistas y reagrupaciones. En pausa, la lógica de los bots se detiene, pero podés consultar las tarjetas. Abrir las tarjetas también detiene temporalmente a los bots.

## Controles

- **Clic izquierdo:** seleccionar país / activar acción o tarjeta.
- **Clic derecho:** abrir menú contextual sobre el país bajo el cursor para incorporar, atacar, lanzar misiles, reagrupar o abrir pactos, según la fase y selección.
- **T:** abrir o cerrar visor de tarjetas.
- **O:** leer los objetivos completos del jugador humano.
- **H:** abrir el historial ampliado de la partida.
- **P:** consultar, proponer, confirmar o anunciar ruptura de pactos públicos; acceso a asaltos voluntarios.
- **F:** cambiar velocidad de bots, incluida pausa.
- **Espacio:** avanzar fase, cuando está habilitado.
- **A / R:** aceptar o rechazar propuestas pendientes de bots.
- **Esc:** cerrar tarjetas o ventanas normales (excepto situaciones y propuestas de pactos obligatorias); si no hay ninguno, salir.
- **1, 2, 3:** elegir la cantidad para ocupar una conquista, si corresponde.

## Pruebas y alcance

```bash
python -m unittest -v test_reglas test_pactos test_correcciones_v7 test_correcciones_v8
```

Se validaron 81 casos automatizados sobre el motor, los asientos y la diplomacia, además de 60 simulaciones adicionales de 2 a 6 jugadores en v7 (además de las validaciones anteriores), junto con la conectividad del grafo de fronteras y la compilación de todos los archivos Python. **No fue posible lanzar Pygame gráficamente en este entorno** por indisponibilidad del paquete y acceso a Internet: la interacción visual debe verificarse ejecutando el ZIP en Windows.

**Límites:** la diplomacia tiene aceptación voluntaria y cumplimiento automático (no permite pactos privados ni promesas verbales); los bots negocian según su perfil. El nuevo sistema de condominios y diálogos necesita validación gráfica de usuario en Windows. Siguen pendientes la coordinación colectiva previa de refuerzos extras, el guardado/carga de partidas y los sonidos. Esta implementación digital no reemplaza todas las interpretaciones y decisiones humanas posibles del reglamento.
