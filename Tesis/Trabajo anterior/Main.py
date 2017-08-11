import Collaboration as Col

# set params:
# files of: clusters, log, explicit derivation and hba1c measurements
# ?center, ?age, ?start and finish dates etc...

cluster_assignment = 'Log/Cluster/hemoglobina2.csv'
#cluster_assignment = 'Log/Cluster/transition_log_V4.csv'

#complete_log = 'Log/testlog.csv'
complete_log = 'Log/3_log_since_T90_1.csv'

#referrals = 'Log/testreferrals.csv'
referrals = 'Log/referrals.csv'

dm_measurements = 'Log/hba1c_log.csv'

#####################################################################################################################
# Params for the Implicit derivation:                                                                               #
#           time_window_id: int. The maximum time between activities to consider to be in a relation                #
#           relations_threshold_id: int. Edges with a relative frequency over this value will be shown              #
#           referrals_threshold: int. Nodes with a relative frequency over this value will be shown as ellipses     #
#           node_frequency_filter: int. Nodes with a frequency of occurrence below this value will be eliminated    #
#                                  before computing relation values.                                                #
#           edge_frequency_filter: int. Edges with a frequency of occurrence below this value will be eliminated    #
#                                  before computing relation values.                                                #
#                                                                                                                   #
#####################################################################################################################

time_window_id = 120
relations_threshold_id = 0.05
referrals_threshold = 0.1
node_frequency_filter = 0
edge_frequency_filter = 0

#####################################################################################################################
# Params for the Explicit derivation:                                                                               #
#           time_window_ed: int. The maximum time between activities to consider to be in a relation                #
#           relations_threshold_ed: int. Edges with a relative frequency over this value will be shown              #
#           professional_labeled_threshold: int. Edges with a relative frequency over this value will be shown.     #
#                                   applied to the graph with detailed role information                             #
#           node_freq_filter_ed: int. Nodes with a frequency of occurrence below this value will be eliminated      #
#                                  before computing relation values.                                                #
#           relative_freq_filter_ed: int. Edges with a relative frequency below this value will be eliminted        #
#                                   before computing relation values                                                #
#           absolute_freq_filter_ed: int. Edges with a frequency of occurrence below this value will be eliminated  #
#                                  before computing relation values.                                                #
#           start: int[A,B]. Activities will be considered only after month A of year B                             #
#           finish: int[A,B]. Activities will be considered only before month A of year B                           #
#                                                                                                                   #
#####################################################################################################################





time_window_ed = 120
relations_threshold_ed = 0
professional_labeled_threshold = 0.05
node_freq_filter_ed = 0
relative_freq_filter_ed = 0  # pre process %
absolute_freq_filter_ed = 0.001  # pre process absolute frequency
start = [1, 2001]
finish = [11, 2016]

#####################################################################################################################
# Other Params:                                                                                                     #
#           relations_threshold_ed: int. Edges with a relative frequency over this value will be shown              #
#           relative_freq_filter_ed: int. Edges with a relative frequency below this value will be eliminted        #
#                                   before computing relation values                                                #
#           absolute_freq_filter_ed: int. Edges with a frequency of occurrence below this value will be eliminated  #
#                                  before computing relation values.                                                #
#                                                                                                                   #
#####################################################################################################################

less_info = False
relation_freq_mode = False  # alg. that defines the shape of nodes according the number of inbound and outbound arrows
filtering_most_freq = True  # it doesn't consider cardiovascular controls when calculating the the relations' threshold
cv_freq = 0  # pre process the event log according the number of attentions per patient

percentage_difference_ed = 0
absolute_difference_ed = 0

nodes_significance = 0
relations_significance = 0

# mode for implicit derivation: 0 = activities, 1 = professionals, 2 = estates
mode = 0

# Diagrams creation

#cluster = '[7-9]'
#Col.read_files(cluster_assignment, ['[7-9]', '>9', 'empeora', 'estable', 'mejora', 'Medio_inestable', 'Muy_inestable'],
#               complete_log, referrals, start, finish, cv_freq)

#cluster_list = ['Delegador', 'Deleg. reasig.', 'Subcon. simple', 'Subcon. multiple', 'Subcon. coord.', "Grupo2", "Grupo Int2"]
#cluster = 'Derivacion'

cluster_list = ['Mejora', 'Compensado', 'Medianamente Descompensado', 'Altamente Descompensado']

Col.read_files(cluster_assignment, cluster_list,
               complete_log, referrals, start, finish, cv_freq)


# Col.show_compensation_graph(cluster)


# professionals and activities per patient
#professionals_1 = Col.people_per_patient(cluster)
#activities_1 = Col.act_per_patient(cluster)

#####################################################################################################################
# Function: show_implicit_derivation                                                                                #
# Params:   cluster: string. Represents the route of the log to be analyzed                                         #
#           time_window_id: int. The maximum time between activities to consider to be in a relation                #
#           mode: 0 = Activities, 1 = Professionals, 2 = Roles                                                      #
#           relations_threshold: int. Edges with a relative frequency over this value will be shown                 #
#           referrals_threshold: int. Label in nodes with a relative frequency over this value will be shown with   #
#                               yellow color.                                                                       #
#           node_frequency_filter: int. Nodes with a frequency of occurrence below this value will be eliminated    #
#                                  before computing relation values.                                                #
#           edge_frequency_filter: int. Edges with a frequency of occurrence below this value will be eliminated    #
#                                  before computing relation values.                                                #
#           less_info: boolean. if True, pre-processed information will not appear in generated reports             #
#                                                                                                                   #
# calls a method to draw the graph, returns a node list, a dictionary (relations) of edges used for the drawing,    #
# a dictionary (statistics) with KEY: a tuple (A,B) and VALUE: a list of tuples (N,K) that indicates the activity   #
# B immediately after A happened N times per patient with a frequency of K in all log                               #
# It also writes reports of the nodes, edges and statistics computed.                                               #
#                                                                                                                   #
#                                                                                                                   #
#####################################################################################################################

#nodes_A, edges_A, activities_per_patient_freq_A, num_of_patients_A = Col.show_implicit_derivation(cluster, time_window_id, mode,
#                            relations_threshold_id, referrals_threshold, node_frequency_filter, edge_frequency_filter,
#                                                                less_info, relation_freq_mode, filtering_most_freq)

#####################################################################################################################
# Function: show_explicit_derivation                                                                                #
# Params:   cluster: string. Represents the route of the log to be analyzed                                         #
#           time_window_ed: int. The maximum time between activities to consider to be in a relation                #
#           relations_threshold_ed: int. Edges with a relative frequency over this value will be shown              #
#           node_freq_filter_ed: int. Nodes with a frequency of occurrence below this value will be eliminated      #
#                                  before computing relation values.                                                #
#           absolute_freq_filter_ed: int. Edges with a frequency of occurrence below this value will be eliminated  #
#                                  before computing relation values.                                                #
#           relative_freq_filter_ed: int. Edges with a relative frequency below this value will be eliminted        #
#                                   before computing relation values                                                #
#           less_info: boolean. if True, pre-processed information will not appear in generated reports             #
#           start: int[A,B]. Activities will be considered only after month A of year B                             #
#           finish: int[A,B]. Activities will be considered only before month A of year B                           #
#                                                                                                                   #
# calls a method to draw the graph, returns a node list, a dictionary of edges used for the drawing,                #
# a dictionary (effective_referrals) with KEY: a tuple (A,B) and VALUE: the times where A reffers to B and the      #
# patient did come to the appoint.                                                                                  #
#                                                                                                                   #
#                                                                                                                   #
#                                                                                                                   #
#####################################################################################################################
for c in cluster_list:
#	if c != "Subcon. simple":
#		continue
	ed_nodes_A, ed_edges_A, detailed_relation_A, effective_referrals_A, total_referrals_A, \
	annual_average_referrals_A = Col.show_explicit_derivation(c, time_window_ed, relations_threshold_ed, professional_labeled_threshold,node_freq_filter_ed,
	                                                            absolute_freq_filter_ed, relative_freq_filter_ed, less_info, start, finish)

#####################################################################################################################
# Function: show_duo                                                                                                #
# Params:   cluster: string. Represents the route of the log to be analyzed                                         #
#           time_window_ed: int. The maximum time between activities to consider to be in a relation                #
#           relations_threshold: int. Edges with a relative frequency over this value will be shown                 #
#           node_freq_filter: int. Nodes with a frequency of occurrence below this value will be eliminated         #
#                                  before computing relation values.                                                #
#           edge_freq_filter_ed: int. Edges with a frequency of occurrence below this value will be eliminated      #
#                                  before computing relation values.                                                #
#           less_info: boolean. if True, pre-processed information will not appear in generated reports             #
#                                                                                                                   #
# calls a method to draw the graph, returns a node list and a dictionary of edges used for the drawing.             #
# It also writes reports of the nodes, edges and statistics computed.                                               #
#                                                                                                                   #
#                                                                                                                   #
#                                                                                                                   #
#####################################################################################################################
#duo_nodes_A, duo_edges_A = Col.show_duo(cluster, time_window_ed, relations_threshold_id, node_freq_filter_ed, edge_frequency_filter, less_info)




###SI QUIERES COMPARAR DOS LOGS, USA LOS COMANDOS QUE SIGUEN Y USA LA FUNCION Col.compare(...)

#cluster2 = 'cluster1'
#Col.read_files(cluster_assignment, ['cluster0', 'cluster1', 'cluster2', 'cluster3', 'cluster4', 'cluster5'],
#               complete_log, referrals, start, finish, cv_freq)

# professionals and activities per patient
#professionals_1 = Col.people_per_patient(cluster)
#activities_1 = Col.act_per_patient(cluster)

#####################################################################################################################
# Function: show_implicit_derivation                                                                                #
#####################################################################################################################

#nodes_B, edges_B, activities_per_patient_freq_B, num_of_patients_B = Col.show_implicit_derivation(cluster, time_window_id, mode,
#                           relations_threshold_id, referrals_threshold, node_frequency_filter, edge_frequency_filter,
#                                                                less_info, relation_freq_mode, filtering_most_freq)


#####################################################################################################################
# Function: show_explicit_derivation                                                                                #
#####################################################################################################################
#ed_nodes_B, ed_edges_B, detailed_relation_B, effective_referrals_B, total_referrals_B, \
#annual_average_referrals_B = Col.show_explicit_derivation(cluster, time_window_ed, relations_threshold_ed, node_freq_filter_ed,
#                                                            absolute_freq_filter_ed, relative_freq_filter_ed, less_info, start, finish)


#####################################################################################################################
# Function: show_duo                                                                                                #
#####################################################################################################################
# #duo_nodes_B, duo_edges_B = Col.show_duo(cluster, time_window_ed, relations_threshold, node_freq_filter, edge_freq_filter, less_info)


#####################################################################################################################
# Function: compareImplicit                                                                                         #
# Params:   cluster: string. Represents the route of the first log to be analyzed                                   #
#           cluster2: string. Represents the route of the second log to be analyzed                                 #
#           nodes_A: dictionary. The Key represents a node in the graph and the value is the number of appearances  #
#                   in the first log.                                                                               #
#           edges_A: dictionary. The Key represents a tuple (A,B) of nodes node in the graph and the value is the   #
#                   number of appearances of the relation from A to B in the first log                              #
#                   in the first log.                                                                               #
#           nodes_B: dictionary. The Key represents a node in the graph and the value is the number of appearances  #
#                   in the second log.                                                                              #
#           edges_B: dictionary. The Key represents a tuple (A,B) of nodes node in the graph and the value is the   #
#                   number of appearances of the relation from A to B in the first log                              #
#                   in the second log.                                                                              #
#           activities_per_patient_freq_A: dictionary. The Key represents a tuple (A,B) of                          #
#                                           a relation                                                              #
#           activities_per_patient_freq_B: dictionary. The Key represents a tuple (A,B) of                          #
#                                           a relation                                                              #
#           num_of_patients_A: integer. The number of patients in the first log                                     #
#           num_of_patients_B: integer. The number of patients in the second log                                    #
#           nodes_significance: float. If the difference of the frequency of nodes from the two logs, in percentage,#
#                               is above this value, will cause to highlight the node with the frequency of higher  #
#                               value.                                                                              #
#           relations_significance: float. If the difference of the frequency of edges from the two logs, in        #
#                                percentage, is above this value, will cause to highlight the edge from the log     #
#                                with the frequency of higher value.                                                #
#                                                                                                                   #
# calls a method to draw a comparison graph. This will show de difference in % of the appearences of nodes and      #
# edges from the two logs.                                                                                          #
#                                                                                                                   #
#####################################################################################################################

#Col.compareImplicit(cluster, cluster2, nodes_A, edges_A, nodes_B, edges_B, activities_per_patient_freq_A, activities_per_patient_freq_B, num_of_patients_A, num_of_patients_B, nodes_significance, relations_significance)



#####################################################################################################################
# Function: compareExplicit                                                                                         #
# Params:   ed_nodes_A: dictionary. The Key represents a node in the graph and the value is the number of           #
#                   appearances in the first log.                                                                   #
#           ed_edges_A: dictionary. The Key represents a tuple (A,B) of nodes in the graph and the value is the     #
#                   number of appearances of the relation from A to B in the first log                              #
#           annual_avegare_referrals_A: dictionary. The Key represents a tuple (A,B) of nodes in the graph and the  #
#                   value is the average number of appearances of the relation from A to B in one year in the first #
#                   log.                                                                                            #
#           ed_nodes_B: dictionary. The Key represents a node in the graph and the value is the number of           #
#                   appearances in the second log.                                                                  #
#           ed_edges_B: dictionary. The Key represents a tuple (A,B) of nodes in the graph and the value is the     #
#                   number of appearances of the relation from A to B in the second log                             #
#           annual_avegare_referrals_B: dictionary. The Key represents a tuple (A,B) of nodes in the graph and the  #
#                   value is the average number of appearances of the relation from A to B in one year in the       #
#                   second log.                                                                                     #
#           nodes_significance: float. If the percentage difference between the frequency of appearance of nodes    #
#                   from both logs is below this value, will cause to ignore those nodes in the graph drawing       #
#           relations_significance: float. If the percentage difference between the frequency of appearance of edges#
#                   from both logs is below this value, will cause to ignore those edges in the graph drawing       #
#                                                                                                                   #
# calls a method to draw a comparison graph. This will show de difference in % of the appearences of nodes and      #
# edges from the two logs.                                                                                          #
#                                                                                                                   #
#####################################################################################################################

#Col.compareExplicit(ed_nodes_A, ed_edges_A, annual_average_referrals_A, ed_nodes_B, ed_edges_B, annual_average_referrals_B, nodes_significance, percentage_difference_ed, absolute_difference_ed)



#Col.compareDuo(archivo1, archivo2, nodosLogA, relacionesLogA, nodosLogB, relacionesLogB, estadisticosLogA, estadisticosLogB, casosA, casosB, significancia_nodos, significancia_relaciones)
#Col.compareAdherence(derivacionesEfectivasA, derivacionesTotalesA, derivacionesEfectivasB, derivacionesTotalesA, archivo1[4:], archivo2[4:])

###COMPARA A LAS PERSONAS QUE ATIENDEN A UN MISMO PACIENTE Y AL NUMERO DE ACTIVIDADES SOBRE LOS MISMOS###
#Col.compareData(personas1, personas2, actividades1, actividades2, archivo1, archivo2)






#Col.showAll(ventana, modo, umbral_relaciones, umbral_relaciones, frecuencia_nodos, frecuencia_relaciones, menos_info)
