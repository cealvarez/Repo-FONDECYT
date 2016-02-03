MINI PROGRAMA PARA GENERAR GRAFOS DE COLABORACION

INSTRUCCIONES DE USO

1- instalar las librerias "pandas", "numpy" y "graphviz"

IMPORTANTE: INSTALACIÓN DE GRAPHVIZ
	Descargar la librería http://www.graphviz.org/Download.php 
	- Instalar graphviz (descargar archivo MSI)
	- Agregar carpeta 'bin' a la variable de entorno 'path' (C:\Program Files\graphviz-2.38\release\bin) *PUEDE ESTAR EN OTRA RUTA
	- Desde la carpeta 'Scripts' en la carpeta de Python, abrir la terminal y ejecutar
		pip install Graphviz

2- El programa cuenta con 4 archivos .py y una serie de carpetas que se detallan a continuación:
	- Reader.py: encargado de leer el log y procesar la información.
	- Collaboration.py: encargado de los algoritmos de colaboración en base a la información procesada por Reader.py
	- Graph.py: encargado de representar gráficamente el output de los algoritmos de Collaboration.py, filtrando elementos dependiendo del threshold
	- Main.py: el ejecutable principal, encargado de hacer funcionar los demás archivos y donde se pueden pasar parámetros para los grafos
	Las principales variables en el Main se describen a continuación:
		- ventana: corresponde a la ventana de tiempo (en días) que se aplicará al procesamiento de los datos
		- umbral_relaciones: corresponde al umbral de relaciones que mostrará la librería gráfica en caso de que la frecuencia relativa de la relación sea superior al 
		umbral
		- umbral_derivaciones: corresponde al umbral de flechas que salen del nodo (derivaciones), la librería pintará las letras del nodo de amarillo en caso de que la
		frecuencia relativa de derivaciones sea mayor a este umbral
		- frecuencia_nodos: parámetro que pre-procesa los datos, eliminando aquellos nodos con una frecuencia menor a la indicada
		- frecuencia_relaciones: parámetro que pre-procesa los datos, eliminando aquellas relaciones con una frecuencia menor a la indicada
		- menos_info: boolean. Si es False, generará reportes con todos los datos. Si es True, generará reportes solo con los datos usados después de los filtros
		(ver sección 3)
		- tiempo_inicio: año en el cual se empiezan a considerar datos del log 
		- tiempo_fin: año en el cual se terminan de considerar datos del log
		- archivo: ruta al log, el cual por defecto se encuentra en la carpeta Log
		- modo: 0 para derivaciones entre actividades, 1 para derivaciones entre profesionales, 2 para derivaciones entre estamentos
	- Graph-output: Carpeta donde se guardan los grafos generados
	- Input: Carpeta con los archivos "Events" que excluye los eventos de ese archivo en el procesamiento de datos y "No_Triggers" que excluye a las actividades
	que ahí aparecen del algoritmo de si es trigger o no
	- Log: donde se encuentra el log
	- Reports: archivos que muestran las relaciones existentes y su frecuencia, así como la cantidad de veces que aparecen los nodos y el # de derivaciones

3- En la carpeta Reports hay archivos que detallan las relaciones existentes en el log (menos_info = False) o las filtradas por los umbrales (menos_info = True).
Las estadísticas siempre son las utilizadas según umbrales, la finalidad del parámetro "menos_info" es proporcionar información completa o resumida de las relaciones
existentes dependiendo de lo que el usuario considere relevante.

4- Es importante que cada vez que se corra el programa, se cierre el archivo de grafo generado. Por defecto el archivo tiene un formato de nombre
	ID_UMBRALRELACION_VENTANA_UMBRALDERIVACION_FRECUENCIANODO_FRECUENCIARELACIONES.pdf

	Si no se cambia los parametros y se corre el programa con el archivo abierto, no lo actualizará.

5-IMPORTANTE: para que Reader.py lea el log, se debe cumplir con lo siguiente:
	- la primera linea debe tener un header con los nombres de las columnas.
	- puede existir cualquier cantidad de tags, pero los mínimos que deben estar son:
		id_paciente
		acto
		estamento
		fecha
		id_clinico
		vino
	tal cual está escrito
	- no importa el orden de los tags
	- separador debe ser ';'
	- los nombres de las actividades, profesionales y estamentos solo debe contener caracteres alfanuméricos o '_' (guión bajo)
	- la fecha debe venir en formato YYYY/mm/dd HH:MM (ej: 2014/02/10 17:20)
	- El archivo puede o no encontrarse en la carpeta 'Log', eso se define en el parámetro "archivo" del Main


Algunos supuestos hechos al generar el código:

El log solo considera aquellos eventos donde el paciente fue (vino = 1)
A nivel de colaboración entre profesionales y estamentos, se eliminó todo evento que lo ejecute un paramédico o la sala de procedimientos
ECG+ESPIROMETRIA se fusionó en ECG
I_CURACION_PIE_DIAB se fusionó con I_CURACION_ENFERMERA
A nivel de estamento, hay autoarcos. No así a nivel de profesional

Cualquier duda me pueden consultar =)
Si hay algún error avísenme también
		
