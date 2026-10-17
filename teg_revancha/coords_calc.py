"""
Script auxiliar para calcular coordenadas de paises
en el espacio 1280x960 a partir de posiciones en el mapa original (9933x7016).
"""

# Posiciones en imagen original 9933x7016 (estimadas visualmente)
# Estas posiciones se calcularon inspeccionando el mapa original
paises_orig = {
    # AMERICA DEL NORTE
    "Alaska":        ( 980,  650),
    "Canada":        (1550, 1230),
    "Isla Victoria": (2100,  620),
    "Groenlandia":   (3100,  590),
    "Labrador":      (2950, 1100),
    "Oregon":        ( 840, 1740),
    "Terranova":     (3200, 1520),
    "Nueva York":    (2500, 1860),
    "Las Vegas":     (1150, 2180),
    "Chicago":       (1960, 2050),
    "California":    ( 790, 2530),
    "Florida":       (2100, 2640),
    "Mexico":        (1300, 2980),
    # AMERICA CENTRAL
    "Cuba":          (2290, 3020),
    "Honduras":      (1640, 3270),
    "Jamaica":       (2350, 3280),
    "El Salvador":   (1530, 3490),
    "Nicaragua":     (1740, 3700),
    # AMERICA DEL SUR
    "Colombia":      (1580, 4100),
    "Venezuela":     (2130, 4130),
    "Brasil":        (2600, 4480),
    "Bolivia":       (1850, 4650),
    "Paraguay":      (2280, 4760),
    "Chile":         (1680, 5130),
    "Uruguay":       (2390, 5080),
    "Argentina":     (1950, 5520),
    # EUROPA
    "Islandia":      (4300,  970),
    "Gran Bretana":  (4520, 1510),
    "Irlanda":       (4100, 1850),
    "Noruega":       (5120, 1060),
    "Finlandia":     (5610, 1150),
    "Bielorrusia":   (6020, 1380),
    "Portugal":      (4020, 2490),
    "Espana":        (4450, 2590),
    "Francia":       (4780, 2140),
    "Alemania":      (5140, 1860),
    "Polonia":       (5620, 1710),
    "Ucrania":       (6180, 1800),
    "Italia":        (5010, 2510),
    "Serbia":        (5440, 2200),
    "Croacia":       (5370, 2510),
    "Albania":       (5980, 2370),
    # ASIA
    "Chukchi":       (8240,  590),
    "Siberia":       (7620,  840),
    "Kamchatka":     (8820, 1200),
    "Chechenia":     (7400, 1340),
    "Rusia":         (6870, 1700),
    "Japon":         (9380, 1600),
    "Corea":         (8940, 1940),
    "Iran":          (7260, 2420),
    "Turquia":       (6670, 2680),
    "China":         (8230, 2210),
    "Israel":        (6620, 3050),
    "Irak":          (7130, 3040),
    "Arabia":        (6870, 3560),
    "India":         (7790, 3100),
    "Malasia":       (8620, 2940),
    "Vietnam":      (8840, 2620),
    # AFRICA
    "Sahara":        (4770, 3610),
    "Egipto":        (5680, 3560),
    "Nigeria":       (5130, 4200),
    "Etiopia":       (5870, 4070),
    "Angola":        (5620, 4570),
    "Mauritania":    (6100, 4620),
    "Sudafrica":     (5870, 5130),
    "Madagascar":    (6680, 4840),
    # OCEANIA
    "Filipinas":     (9040, 3390),
    "Sumatra":       (8360, 3900),
    "Tonga":         (9260, 3940),
    "Australia":     (8700, 4560),
    "Tasmania":      (8630, 5250),
    "Nueva Zelanda": (9350, 5190),
}

W_ORIG = 9933
H_ORIG = 7016
W_DATA = 1280
H_DATA = 960

print("Coordenadas convertidas al espacio 1280x960:")
for nombre, (xo, yo) in paises_orig.items():
    xd = round(xo * W_DATA / W_ORIG)
    yd = round(yo * H_DATA / H_ORIG)
    print(f'    "{nombre}": ({xd}, {yd}),')
