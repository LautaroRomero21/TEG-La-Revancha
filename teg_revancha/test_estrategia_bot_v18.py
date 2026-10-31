"""IA contextual v18: decisiones de bots y frontera Chechenia-Kamchatka."""
import unittest
from unittest.mock import patch
from data import PAISES_DATA
from logic import JuegoTEG, FASE_INCORPORAR, FASE_ATACAR, FASE_REAGRUPAR


def juego_bot():
    j=JuegoTEG(3)
    j.turno_idx=1
    j.ronda=3
    j.fase=FASE_INCORPORAR
    j.etapa='hostilidades'
    j.etapa_ronda='INCORPORACION'
    j.situacion='Clásico'
    j.refuerzos_continente={}
    j.ejercitos_a_colocar=12
    j.bot_refuerzos_por_pais={}
    j.tablero['Nigeria']['propietario']=1
    j.tablero['Nigeria']['ejercitos']=12
    j.tablero['Angola']['propietario']=0
    j.tablero['Angola']['ejercitos']=3
    j.tablero['Sudafrica']['propietario']=0
    j.tablero['Sudafrica']['ejercitos']=1
    return j


class FronterasV18(unittest.TestCase):
    def test_eliminacion_reciproca(self):
        self.assertNotIn('Kamchatka',PAISES_DATA['Chechenia']['fronteras'])
        self.assertNotIn('Chechenia',PAISES_DATA['Kamchatka']['fronteras'])
        self.assertEqual(len(PAISES_DATA),72)
        for pais,info in PAISES_DATA.items():
            self.assertEqual(len(info['fronteras']),len(set(info['fronteras'])))
            for vecino in info['fronteras']:
                self.assertIn(pais,PAISES_DATA[vecino]['fronteras'])

    def test_no_adyacencia_en_partida(self):
        j=juego_bot()
        self.assertFalse(j.son_adyacentes('Chechenia','Kamchatka'))
        self.assertFalse(j.son_adyacentes('Kamchatka','Chechenia'))


class InteligenciaContextualV18(unittest.TestCase):
    def test_un_refuerzo_si_posicion_ya_es_segura(self):
        j=juego_bot()
        self.assertEqual(j._cantidad_refuerzo_bot(j.jugadores[1],'Nigeria',8),1)

    def test_refuerzo_mayor_si_hay_amenaza(self):
        j=juego_bot()
        j.tablero['Nigeria']['ejercitos']=1
        j.tablero['Angola']['ejercitos']=10
        cantidad=j._cantidad_refuerzo_bot(j.jugadores[1],'Nigeria',8)
        self.assertGreater(cantidad,1)
        self.assertLessEqual(cantidad,8)

    def test_bot_realmente_incorpora_de_a_uno(self):
        j=juego_bot()
        with patch.object(j,'_seleccionar_refuerzo_bot',return_value='Nigeria'):
            estado=j.paso_bot()
        self.assertEqual(estado['accion'],'incorporar')
        self.assertEqual(estado['cantidad'],1)
        self.assertEqual(j.tablero['Nigeria']['ejercitos'],13)
        self.assertEqual(j.ejercitos_a_colocar,11)

    def test_incorporacion_masiva_justificada(self):
        j=juego_bot()
        j.tablero['Nigeria']['ejercitos']=1
        j.tablero['Angola']['ejercitos']=11
        with patch.object(j,'_seleccionar_refuerzo_bot',return_value='Nigeria'):
            estado=j.paso_bot()
        self.assertGreater(estado['cantidad'],1)
        self.assertEqual(j.tablero['Nigeria']['ejercitos'],1+estado['cantidad'])

    def test_rival_proximo_a_45_eleva_urgencia(self):
        j=juego_bot()
        ctx=j._contexto_estrategico_bot(j.jugadores[1])
        ctx_lider={**ctx,'paises':{**ctx['paises'],0:44}}
        base=j._valor_territorio_bot('Angola',j.jugadores[1],ctx)
        peligro=j._valor_territorio_bot('Angola',j.jugadores[1],ctx_lider)
        self.assertGreater(peligro-base,16)

    def test_cerrar_continente_eleva_prioridad(self):
        j=juego_bot()
        ctx=j._contexto_estrategico_bot(j.jugadores[1])
        c='Africa'
        bajo={**ctx,'continentes':{**ctx['continentes'],c:{**ctx['continentes'][c],1:0}}}
        alto={**ctx,'continentes':{**ctx['continentes'],c:
               {**ctx['continentes'][c],1:ctx['totales'][c]-1}}}
        self.assertGreater(j._valor_territorio_bot('Angola',j.jugadores[1],alto),
                           j._valor_territorio_bot('Angola',j.jugadores[1],bajo)+13)

    def test_priorizar_frente_con_conquistas_posibles(self):
        j=juego_bot()
        j.jugadores[1].objetivos=[{'tipo':'ocupacion','cantidad':35}]
        for d in j.tablero.values():
            d['propietario']=0
            d['ejercitos']=15
        for p in ('Nigeria','Alaska'):
            j.tablero[p]['propietario']=1
            j.tablero[p]['ejercitos']=1
        for q in j.tablero['Nigeria']['fronteras']:
            j.tablero[q]['propietario']=0
            j.tablero[q]['ejercitos']=1
        for q in j.tablero['Alaska']['fronteras']:
            j.tablero[q]['propietario']=0
            j.tablero[q]['ejercitos']=20
        self.assertEqual(j._seleccionar_refuerzo_bot(j.jugadores[1],
                         ['Nigeria','Alaska']),'Nigeria')

    def test_evitar_ataque_con_desventaja_aplastante(self):
        j=juego_bot()
        j.fase=FASE_ATACAR
        j.tablero['Nigeria']['ejercitos']=2
        j.tablero['Angola']['ejercitos']=12
        j.tablero['Sudafrica']['ejercitos']=8
        ataques=[(a,b) for _,a,b in j._ataques_posibles_bot(j.jugadores[1])]
        self.assertNotIn(('Nigeria','Angola'),ataques)

    def test_tambien_usa_factores_ajenos_a_mision(self):
        j=juego_bot()
        j.jugadores[1].objetivos=[{'tipo':'ocupacion','cantidad':35}]
        self.assertGreater(j._valor_territorio_bot('Angola',j.jugadores[1]),
                           j._preferencia('Angola',j.jugadores[1]))

    def test_reagrupe_del_interior_a_la_frontera(self):
        j=juego_bot()
        j.fase=FASE_REAGRUPAR
        for p in j.tablero:
            j.tablero[p]['propietario']=0
            j.tablero[p]['ejercitos']=2
        j.tablero['Isla Victoria']['propietario']=1
        j.tablero['Isla Victoria']['ejercitos']=12
        j.tablero['Canada']['propietario']=1
        j.tablero['Canada']['ejercitos']=2
        j.tablero['Groenlandia']['propietario']=1
        j.tablero['Groenlandia']['ejercitos']=2
        j.tablero['Oregon']['ejercitos']=8
        mov=j._reagrupe_estrategico_bot(j.jugadores[1])
        self.assertIsNotNone(mov)
        origen,destino,cant=mov
        self.assertEqual(origen,'Isla Victoria')
        self.assertIn(destino,('Canada','Groenlandia'))
        self.assertGreaterEqual(cant,1)
        self.assertEqual(j.tablero[origen]['ejercitos'],12-cant)

    def test_no_reagrupar_unidades_recibidas(self):
        j=juego_bot()
        j.fase=FASE_REAGRUPAR
        j.reagrupados_recibidos={'Nigeria':11}
        mov=j._reagrupe_estrategico_bot(j.jugadores[1])
        if mov:self.assertNotEqual(mov[0],'Nigeria')

    def test_no_pactar_con_rival_que_esta_por_ganar(self):
        j=juego_bot()
        with patch.object(j,'_contexto_estrategico_bot',return_value={'paises':{0:43}}):
            self.assertFalse(j.bot_acepta_pacto(1,'pais',0))

    def test_no_pactar_con_objetivo_de_eliminacion(self):
        j=juego_bot()
        j.jugadores[1].objetivos=[{'tipo':'eliminacion','objetivo_idx':0}]
        self.assertFalse(j.bot_acepta_pacto(1,'pais',0))

    def test_alianza_de_ataque_sigue_posible(self):
        j=juego_bot()
        with patch.object(j,'_contexto_estrategico_bot',return_value={'paises':{0:44}}):
            with patch('logic.random.random',return_value=0.0):
                self.assertTrue(j.bot_acepta_pacto(1,'agresion',0))


if __name__=='__main__':
    unittest.main()
