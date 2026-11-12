"""Regresiones v28: prioridad de cerrar Oceanía y cálculo de dados con 75 tropas."""
import unittest
from unittest.mock import patch

from data import CONTINENTES, PAISES_DATA
from logic import JuegoTEG, FASE_ATACAR
from ia_dificil import probabilidad_conquista


def oceania_verde():
    """Reproduce la captura: Filipinas 75 verdes vs Tonga 13 azules.

    Hay además tropas rojas en California, que podrían contraatacar Tonga.
    Los demás territorios verdes de Oceanía tienen un ejército cada uno.
    """
    j=JuegoTEG(4,orden_inicial=[1,0,2,3],dificultad='Dificil')
    j.etapa='hostilidades'
    j.etapa_ronda='ATAQUE'
    j.fase=FASE_ATACAR
    j.turno_idx=1
    j.ronda=9
    j.situacion='Clásico'
    j.conquistas_turno=0
    j.conquistas_colectivas=0
    j.bot_ataques_turno=0
    for k,p in enumerate(j.tablero):
        j.tablero[p]['propietario']=[0,2,3][k%3]
        j.tablero[p]['ejercitos']=10
        j.tablero[p]['misiles']=0
    for pais,d in PAISES_DATA.items():
        if d['continente']=='Oceania':
            j.tablero[pais]['propietario']=1
            j.tablero[pais]['ejercitos']=1
    j.tablero['Filipinas']['ejercitos']=75
    j.tablero['Vietnam']['propietario']=1
    j.tablero['Vietnam']['ejercitos']=1
    j.tablero['Tonga']['propietario']=2
    j.tablero['Tonga']['ejercitos']=13
    j.tablero['California']['propietario']=0
    j.tablero['California']['ejercitos']=21
    return j


class CierreOceania(unittest.TestCase):
    def test_filipinas_y_tonga_son_vecinos(self):
        self.assertIn('Tonga',PAISES_DATA['Filipinas']['fronteras'])
        self.assertIn('Filipinas',PAISES_DATA['Tonga']['fronteras'])

    def test_calcula_los_75_ejercitos_no_solo_36(self):
        p36,_=probabilidad_conquista(36,13)
        p75,bajas=probabilidad_conquista(75,13)
        self.assertGreater(p75,.999999)
        self.assertGreater(p75,p36)
        self.assertLess(bajas,14)

    def test_cierre_de_oceania_incentivado_por_bono_real(self):
        j=oceania_verde()
        bot=j.jugadores[1]
        ctx=j.ia_dificil.contexto(bot)
        self.assertEqual(ctx['continentes']['Oceania'][1],5)
        self.assertEqual(ctx['totales']['Oceania'],6)
        self.assertEqual(CONTINENTES['Oceania']['bonus'],3)
        self.assertGreater(j.ia_dificil._incentivo_cierre_continente('Tonga',bot,ctx),0)
        self.assertEqual(j.ia_dificil._incentivo_cierre_continente('Filipinas',bot,ctx),0)

    def test_batalla_75_vs_13_es_opcion_de_ataque_positiva(self):
        j=oceania_verde()
        bot=j.jugadores[1]
        valor=j.ia_dificil.evaluacion_ataque(
            'Filipinas','Tonga',bot,j.ia_dificil.contexto(bot))
        self.assertIsNotNone(valor)
        self.assertGreater(valor[0],0)
        self.assertGreater(valor[1],.999999)

    def test_dificil_realmente_elige_tonga_sobre_inactividad(self):
        j=oceania_verde()
        bot=j.jugadores[1]
        seleccion=j.ia_dificil.candidato_ataque(bot)
        self.assertIsNotNone(seleccion)
        self.assertEqual(seleccion[-2:],('Filipinas','Tonga'))

    def test_situacion_abiertas_impide_ataque_entre_paises_oceania(self):
        j=oceania_verde()
        j.situacion='Fronteras abiertas'
        self.assertNotIn('Tonga',j.ia_dificil._frentes('Filipinas',j.jugadores[1]))
        candidato=j.ia_dificil.candidato_ataque(j.jugadores[1])
        self.assertFalse(candidato and candidato[-2:]==('Filipinas','Tonga'))

    def test_pacto_de_no_agresion_sigue_bloqueando_tonga(self):
        j=oceania_verde()
        j._nuevo_pacto('mundial',1,2)
        self.assertNotIn('Tonga',j.ia_dificil._frentes('Filipinas',j.jugadores[1]))

    def test_fuerza_insuficiente_no_genera_ataque_suicida(self):
        j=oceania_verde()
        j.tablero['Filipinas']['ejercitos']=5
        val=j.ia_dificil.evaluacion_ataque('Filipinas','Tonga',
                 j.jugadores[1],j.ia_dificil.contexto(j.jugadores[1]))
        self.assertIsNone(val)

    def test_pais_ya_conquistado_no_recibe_bono_de_cierre(self):
        j=oceania_verde()
        j.tablero['Tonga']['propietario']=1
        bot=j.jugadores[1]
        self.assertEqual(j.ia_dificil._incentivo_cierre_continente(
                         'Tonga',bot,j.ia_dificil.contexto(bot)),0)

    def test_normal_no_usa_el_puntaje_de_dificil(self):
        j=oceania_verde()
        j.dificultad='Normal'
        j.fase='INCORPORAR'
        j.ejercitos_a_colocar=3
        j.refuerzos_continente={}
        with patch.object(j.ia_dificil,'_incentivo_cierre_continente',
                          side_effect=AssertionError('Normal no usa IA Difícil')):
            self.assertEqual(j.paso_bot()['accion'],'incorporar')


if __name__=='__main__':
    unittest.main()
