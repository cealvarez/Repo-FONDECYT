MINI PROGRAMA PARA GENERAR GRAFOS DE COLABORACION

INSTRUCCIONES DE USO

1- instalar las librerias "pandas", "numpy" y "graphviz"

IMPORTANTE: INSTALACI�N DE GRAPHVIZ
	Descargar la librer�a http://www.graphviz.org/Download.php 
	- Instalar graphviz (descargar archivo MSI)
	- Agregar carpeta 'bin' a la variable de entorno 'path' (C:\Program Files\graphviz-2.38\release\bin) *PUEDE ESTAR EN OTRA RUTA
	- Desde la carpeta 'Scripts' en la carpeta de Python, abrir la terminal y ejecutar
		pip install Graphviz

2- El programa cuenta con 4 archivos .py y una serie de carpetas que se detallan a continuaci�n:
	- Reader.py: encargado de leer el log y procesar la informaci�n.
	- Collaboration.py: encargado de los algoritmos de colaboraci�n en base a la informaci�n procesada por Reader.py
	- Graph.py: encargado de representar gr�ficamente el output de los algoritmos de Collaboration.py, filtrando elementos dependiendo del threshold
	- Main.py: el ejecutable principal, encargado de hacer funcionar los dem�s archivos y donde se pueden pasar par�metros para los grafos
	Las principales variables en el Main se describen a continuaci�n:
		- ventana: corresponde a la ventana de tiempo (en d�as) que se aplicar� al procesamiento de los datos
		- umbral_relaciones: corresponde al umbral de relaciones que mostrar� la librer�a gr�fica en caso de que la frecuencia relativa de la relaci�n sea superior al 
		umbral
		- umbral_derivaciones: corresponde al umbral de flechas que salen del nodo (derivaciones), la librer�a pintar� las letras del nodo de amarillo en caso de que la
		frecuencia relativa de derivaciones sea mayor a este umbral
		- frecuencia_nodos: par�metro que pre-procesa los datos, eliminando aquellos nodos con una frecuencia menor a la indicada
		- frecuencia_relaciones: par�metro que pre-procesa los datos, eliminando aquellas relaciones con una frecuencia menor a la indicada
		- menos_info: boolean. Si es False, generar� reportes con todos los datos. Si es True, generar� reportes solo con los datos usados despu�s de los filtros
		(ver secci�n 3)
		- tiempo_inicio: a�o en el cual se empiezan a considerar datos del log 
		- tiempo_fin: a�o en el cual se terminan de considerar datos del log
		- archivo: ruta al log, el cual por defecto se encuentra en la carpeta Log
		- modo: 0 para derivaciones entre actividades, 1 para derivaciones entre profesionales, 2 para derivaciones entre estamentos
	- Graph-output: Carpeta donde se guardan los grafos generados
	- Input: Carpeta con los archivos "Events" que excluye los eventos de ese archivo en el procesamiento de datos y "No_Triggers" que excluye a las actividades
	que ah� aparecen del algoritmo de si es trigger o no
	- Log: donde se encuentra el log
	- Reports: archivos que muestran las relaciones existentes y su frecuencia, as� como la cantidad de veces que aparecen los nodos y el # de derivaciones

3- En la carpeta Reports hay archivos que detallan las relaciones existentes en el log (menos_info = False) o las filtradas por los umbrales (menos_info = True).
Las estad�sticas siempre son las utilizadas seg�n umbrales, la finalidad del par�metro "menos_info" es proporcionar informaci�n completa o resumida de las relaciones
existentes dependiendo de lo que el usuario considere relevante.

4- Es importante que cada vez que se corra el programa, se cierre el archivo de grafo generado. Por defecto el archivo tiene un formato de nombre
	ID_UMBRALRELACION_VENTANA_UMBRALDERIVACION_FRECUENCIANODO_FRECUENCIARELACIONES.pdf

	Si no se cambia los parametros y se corre el programa con el archivo abierto, no lo actualizar�.

5-IMPORTANTE: para que Reader.py lea el log, se debe cumplir con lo siguiente:
	- la primera linea debe tener un header con los nombres de las columnas.
	- puede existir cualquier cantidad de tags, pero los m�nimos que deben estar son:
		id_paciente
		acto
		estamento
		fecha
		id_clinico
		vino
	tal cual est� escrito
	- no importa el orden de los tags
	- separador debe ser ';'
	- los nombres de las actividades, profesionales y estamentos solo debe contener caracteres alfanum�ricos o '_' (gui�n bajo)
	- la fecha debe venir en formato YYYY/mm/dd HH:MM (ej: 2014/02/10 17:20)
	- El archivo puede o no encontrarse en la carpeta 'Log', eso se define en el par�metro "archivo" del Main


Algunos supuestos hechos al generar el c�digo:

El log solo considera aquellos eventos donde el paciente fue (vino = 1)
A nivel de colaboraci�n entre profesionales y estamentos, se elimin� todo evento que lo ejecute un param�dico o la sala de procedimientos
ECG+ESPIROMETRIA se fusion� en ECG
I_CURACION_PIE_DIAB se fusion� con I_CURACION_ENFERMERA
A nivel de estamento, hay autoarcos. No as� a nivel de profesional

Cualquier duda me pueden consultar =)
Si hay alg�n error av�senme tambi�n
		
