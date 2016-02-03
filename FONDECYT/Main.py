import Collaboration as Col


ventana = 60
umbral_relaciones = 0.005
umbral_derivaciones = 0.05
frecuencia_nodos = 0
frecuencia_relaciones = 0
menos_info = True

tiempo_inicio = 2014
tiempo_fin = 2014
archivo = 'Log/log_agenda_episodio_recuperando_horas_final.csv'

###MODO: 0 PARA ACTIVIDADES, 1 PARA PROFESIONALES, 2 PARA ESTAMENTOS
modo = 2

Col.start(archivo , tiempo_inicio, tiempo_fin)

#Col.showImplicitDerivation(ventana, modo, umbral_relaciones, umbral_derivaciones, frecuencia_nodos, frecuencia_relaciones, menos_info)
Col.showduo(ventana, umbral_relaciones, frecuencia_nodos, frecuencia_relaciones, menos_info)
