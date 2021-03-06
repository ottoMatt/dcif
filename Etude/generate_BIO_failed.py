# -*- coding: utf-8 -*-
'''
check all parameters
check the test if timout (true default)
'''
import multiprocessing as mp
#from BIO_GLOBAL_lib import *
import copy
from BIO_lib import *

PROCESSES = 1
JAVA_ARGS = ['-d64', '-Xms512m', '-Xmx6g','-jar']
TIMEOUT_MONO = 2000000#correspond a peu pres a 20 minutes
TIMEOUT_MULTI = 600000 #10 min
LENGTH_LIST = [3]
DEPTH_LIST =[-1]
METH_LIST = [ 'max-']#,'min-']#,'all']
METH_N_LIST = [4]#,5,10,15] 1,2,3,

NUMAGENT_LIST = [2,4]#,6,8]
METHODS = ['DICF-PB-Async']#, 'DICF-PB-Star', 'DICF-PB-Token']


METHOD_AGENT_DISTRIBUTION = ['_kmet','_naiveEq']#'naive_indent'
METHOD_TP_DISTRIBUTION_LIST = ['short']#,'random']
PERC_TP_DIST_LIST = [2]#1,5,10]

'''
PROCESSES = 4
JAVA_ARGS = ['-d64', '-Xms512m', '-Xmx2g','-jar']
TIMEOUT_MONO = 5000 #il faut mettre le double de ce qu'on veut ici, bug bizarre 
TIMEOUT_MULTI = 5000
#VAR
LENGTH_LIST = [-1]
DEPTH_LIST =[-1]
METH_LIST = [ 'max-']#,'all']
METH_N_LIST = [2] 
#MULTI
NUMAGENT_LIST = [2,4]
METHODS = ['DICF-PB-Async', 'DICF-PB-Star', 'DICF-PB-Token']
'''



PROBLEM_PATH = 'Problems/Bio/'
GEN_PATH = PROBLEM_PATH
#il faut mettre un lock sur ces deux fichiers quand on écrit



FINISHING_MONO_PROBLEMS_FILENAME = 'finishing_MONO_problems'
FINISHING_MONO_PROBLEMS_FIELDNAMES_ORDER = ['infile_path','infile','outfile','method','timeout','var','csq','dist','numagent']

MONO_PROBLEMS_FILENAME = 'generated_MONO_problems'
MONO_PROBLEMS_FIELDNAMES_ORDER = ['infile_path','infile','methodVar','length','depth','dist','numagent'] 

#failed inclus unfinishing
FAILED_MONO_PROBLEMS_FILENAME = 'failed_MONO_problems'
FAILED_MONO_PROBLEMS_FIELDNAMES_ORDER = FINISHING_MONO_PROBLEMS_FIELDNAMES_ORDER
#MULTI_PROBLEMS_FILENAME = 'generated_MULTI_problems'
MULTI_PROBLEMS_FILENAME = 'MULTI_problems'
MULTI_PROBLEMS_FIELDNAMES_ORDER = ['infile_path','infile','outfile','var','numagent','dist','csq_mono']#numagent et dist sont la uniquement si c'est un probleme distribué...

MULTI_PROBLEMS_ALGO_PARAMETERS_FILENAME = 'algo_parameters_MULTI_problems'
MULTI_PROBLEMS_ALGO_PARAMETERS_FIELDNAMES_ORDER = ['infile_path','infile','outfile','var','verbose','timeout','method','numagent','dist','csq','csq_mono']

FAILED_MULTI_PROBLEMS_FILENAME = 'failed_MULTI_problems'
FAILED_MULTI_PROBLEMS_FIELDNAMES_ORDER = MULTI_PROBLEMS_ALGO_PARAMETERS_FIELDNAMES_ORDER

MULTI_PROBLEMS_ALLSTATS_FILENAME = 'running_stats_MULTI_problems'  

GLOBAL_LOG_FILENAME = 'global_log'

#pas testé dans les cas limites : 
#il faut catché l'exception et supprimer la variante distributionnelle dans ce cas...
#ne pas générer de statistiques, peut etre juste un log des problemes qui n'ont pas été lancés (qd on catch une exception)
#ROBUSTE ainsi

'''
tout mettre dans le même fichier
utililser kwargs : dictionray of parameters... 
'''

def generate_parameters_onesol_var(problem_path,problem_filename,length_list,depth_list,meth_list,methN_list) :
    '''
    generates dictionaries containing arguments for generating variants of sol problems
    '''
    resL = []
    for length in length_list:
        for d in depth_list  :      
            for meth in meth_list:
                argsDict= dict()
                argsDict['infile'] = problem_filename
                argsDict['infile_path'] = problem_path
                argsDict['length'] = str(length)
                argsDict['depth'] = str(d)
                if meth != 'all' :
                    for meth_N in methN_list:
                        subDict = copy.deepcopy(argsDict)
                        subDict['methodVar'] = meth+str(meth_N)
                        resL.append(subDict)
                else :
                    argsDict['methodVar'] = meth
                    resL.append(argsDict)
    return resL
def generate_parameters_sols_var(problems_path, problem_filenames,length_list,depth_list,meth_list,methN_list):
    res =[]
    for filename in problem_filenames :
        dictL = generate_parameters_onesol_var(problems_path, filename,length_list,depth_list,meth_list,methN_list)
        res += dictL
    return res
def generate_parameters_algos_dist(problem_filenames,numagent_list):
    '''
    add here a for methodAgentPAritioning = kmetis or naive_eq
    '''
    print problem_filenames
    resL = []   
    for filename in problem_filenames:
        for method in METHOD_AGENT_DISTRIBUTION:
            for numagent in numagent_list:
                argsDict = dict()
                dist = method+str(numagent)
                argsDict['dist'] = dist
                argsDict['numagent'] = str(numagent)
                argsDict['infile'] = filename
                argsDict['infile_path'] = PROBLEM_PATH
                resL.append(argsDict)        
    return resL
def generate_valid_problem_filenames_with_TP(problem_filenames):
    valid_problem_filenames = []
    for sol_filename in problem_filenames :
        sol_file = par.FileSol(PROBLEM_PATH,sol_filename)
        sol_file.load()
        if sol_file.is_valid():
            valid_problem_filenames.append(sol_filename)        
        nbTP = 0
        for perc in PERC_TP_DIST_LIST :            
            new_sol_file, new_nbTP = sol_file.create_a_FileSol_wit_a_TP_distribution_naiveShort(perc)
            if  nbTP == new_nbTP  or not new_sol_file.is_valid():#(même nombre de TP que le dernier alors on ajoute pas):
                continue
            nbTP = new_nbTP
            new_sol_file.save()#resemble a  probfilename + '_TPnaiveshortdist_per'+str(perc)+'_'+'seuil'+str(seuilMin)
            valid_problem_filenames.append(new_sol_file.filename)
    return valid_problem_filenames
'''
avec ce systeme on doit RE generer le dcf de distribution lors de la phase de preparation multi, a cause du suffix
or on pourrait le stocker dans le dicitonnaire et s'il est present, en faire une copie, et le renommer avec le bon suffixe
'''
def generate_valid_problem_args_with_TP_distributed(problem_filenames,NUMAGENT_LIST,log_file):
    #now for the dist thing    
    parameters_dist_dicts = generate_parameters_algos_dist(problem_filenames,NUMAGENT_LIST)
    spe_dicts = []
    for argsDict in parameters_dist_dicts : 
        dcf_filepath,dcf_filename = generate_distribution(argsDict, log_file,GEN_PATH,java_args=JAVA_ARGS)
        #the generated .dcf has name sol_filename+dist            
        dcf_file = par.FileDCF(dcf_filepath,dcf_filename)
        try:
            dcf_file.load()
        except e:
            addToLog(log_file_GLOBAL, ['erreur : dcf non chargé'])
            raise e
            continue
        for method in METHOD_TP_DISTRIBUTION_LIST:
            for percTotal in PERC_TP_DIST_LIST:
                new_tp_sol_file = dcf_file.create_a_FileSol_wit_a_TPdistribution_for_each_agent(percTotal,method = method)
                if not new_tp_sol_file.is_valid():
                    continue
                new_tp_sol_file.save()
                subDict=copy.deepcopy(argsDict)
                subDict['infile'] = new_tp_sol_file.filename
                subDict['infile_path'] = new_tp_sol_file.path
                subDict['distfile_name'] = dcf_filename
                subDict['distfile_path'] = dcf_filepath
                #ici on doit le recuperere dnas le laucn multi
                spe_dicts.append(subDict)
    return spe_dicts
def generate_parameters_sols_var_for_dist(spe_dicts,length_list,depth_list,meth_list,methN_list):
    res = []            
    for spe_d in spe_dicts :
        params = generate_parameters_onesol_var(spe_d['infile_path'], spe_d['infile'],LENGTH_LIST,DEPTH_LIST,
                                                                           METH_LIST,METH_N_LIST)
        for p in params :
            r = copy.deepcopy(p)
            r.update(spe_d) 
            res.append(r)
    return res
def generate_problems_MONO(log_file):
    problem_filenames = get_problem_files(PROBLEM_PATH,'.sol')
    problem_filenames = remove_ext(problem_filenames,'.sol')
   
    valid_problem_filenames = generate_valid_problem_filenames_with_TP(problem_filenames)
    
    list_parameters_MONO = generate_parameters_sols_var(PROBLEM_PATH,valid_problem_filenames,
                                                        LENGTH_LIST,DEPTH_LIST,
                                                        METH_LIST,METH_N_LIST) 
    valid_distributed_problem_args = generate_valid_problem_args_with_TP_distributed(
                                                        problem_filenames, NUMAGENT_LIST,log_file)
    list_parameters_distributed_MONO = generate_parameters_sols_var_for_dist(
                                            valid_distributed_problem_args,
                                             LENGTH_LIST,DEPTH_LIST,
                                             METH_LIST,METH_N_LIST) 
    res = list_parameters_MONO + list_parameters_distributed_MONO
    addToLog(log_file_GLOBAL,['generating problems MONO :'+str(len(res))+' problems'])
    outputs_config_file_all_rows(res,MONO_PROBLEMS_FIELDNAMES_ORDER,MONO_PROBLEMS_FILENAME,'.csv',GEN_PATH,lock=None)
    #output generated problems... for later use
    return res
                                    
def generate_variant( argsDict_mono, log_file,java_args=[]):
    args = java_args+[MAKESOLVARIANT_JAR]+['-method='+argsDict_mono['methodVar'],'-len='+argsDict_mono['length'],'-d='+argsDict_mono['depth'],argsDict_mono['infile_path']+argsDict_mono['infile'], argsDict_mono['outfile']]
    log = jarWrapper(*args)  
    addToLog(log_file,log)
    

def generate_valid_distributions(argsDict,log_file,java_args=[]):
    argsList = generate_parameters_algos_dist([argsDict['infile']],NUMAGENT_LIST)   
    valid_distributions = []    
    for argsDistribution in argsList :
        dist_outfile_path,dist_outfile_name = generate_distribution(argsDistribution, log_file,GEN_PATH,java_args)
        dcf_file = par.FileDCF(dist_outfile_path, dist_outfile_name)   
        dcf_file.load()
        if dcf_file.is_valid() :
            d = copy.deepcopy(argsDict)
            d.update(argsDistribution) 
            valid_distributions.append(d)  
    return valid_distributions
def generate_algos_parameters(filename, ext,parameters,gen_path) :
    '''
    ici il faudra faire varier les parametres d'ordre pour TOKEN et STAR
    faire toutes les combinaisons
    '''
    timeout,methods,numagent_list = parameters
    dictParameters=[]
    filename = gen_path+ filename + ext
    if not os.path.isfile(filename) :
        open(filename, 'a').close()#touch
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for rowDict in reader:
            for method in methods :
                argsDict = dict() 
                argsDict['infile_path'] = rowDict['infile_path']                      
                argsDict['infile'] = rowDict['infile']
                argsDict['var'] = rowDict['var']
                argsDict['verbose'] = True 
                argsDict['timeout'] = timeout
                argsDict['dist'] = rowDict['dist'] 
                argsDict['numagent'] = rowDict['numagent']     
                if method == 'DICF-PB-Token':
                    if int(argsDict['numagent']) <= 2 :#noticed that TOKEN algos fail when numagent =2, whatever the fixed order is...
                        continue
                    #probably unnecessary to do this...
                    firstToken = get_number_first_agent_having_top_clause(argsDict,log_file)
                    method += '-FixedOrder-'+get_string_tokens(firstToken,argsDict['numagent'])                    
               # elif method == 'DICF-PB-Star':
                #    firstToken = get_number_first_agent_having_top_clause(argsDict,log_file)
                 #   method += '-FixedRoot-'+firstToken                
                argsDict['method'] = method           
                
                argsDict['csq'] = rowDict['outfile']+'_MULTI_'+method
                argsDict['csq_mono'] = rowDict['csq_mono']                
                argsDict['outfile'] = rowDict['outfile']+'_MULTI_'+method   
                dictParameters.append(argsDict)
    return dictParameters

def generate_kmet_distribution(argsDict,gen_path,java_args=[]):
  #generate DCF
    #if already exist do nothing, keep it all the same
    dist_outfile_path = argsDict['infile_path']
    dist_outfile_name = argsDict['infile']+argsDict['dist']
    if os.path.isfile(dist_outfile_path+dist_outfile_name+'.dcf') : 
         return dist_outfile_path,dist_outfile_name
    temp_graph_filename=gen_path+argsDict['infile']+'temp_graph'+argsDict['dist']
    ########buildGraph    
    try:
        os.remove(temp_graph_filename+'.gra')        
    except OSError:
        pass                
    args = java_args+[BUILDGRAPH_JAR]+[argsDict['infile_path']+argsDict['infile'], temp_graph_filename ]
    log = jarWrapper(*args)
    ########kMetis
    try:
        os.remove(temp_graph_filename+'.gra.part.'+argsDict['numagent'])
    except OSError:
        pass
    args = [KMETIS_EX, temp_graph_filename+'.gra', argsDict['numagent']]
    log = exWrapper(*args)
    ########graph2DCF
    
    args = java_args+[GRAPH2DCF_JAR]+[argsDict['infile_path']+argsDict['infile'],temp_graph_filename+'.gra.part.'+argsDict['numagent'] , dist_outfile_path+dist_outfile_name+'.dcf']
    log = jarWrapper(*args)
    #clean un peu...
    if os.path.isfile(temp_graph_filename+'.gra') : 
        os.remove(temp_graph_filename+'.gra')
    if os.path.isfile(temp_graph_filename+'.gra.part.'+argsDict['numagent']) : 
        os.remove(temp_graph_filename+'.gra.part.'+argsDict['numagent'])
    return dist_outfile_path,dist_outfile_name

def generate_naiveEq_distribution(argsDict,gen_path):
    #load the sol file
    nbagent = int(argsDict['numagent'])
    sol_filepath = argsDict['infile_path']
    sol_filename = argsDict['infile']   
    sol_file = par.FileSol(sol_filepath,sol_filename)
    sol_file.load()
    
    dcf_file = sol_file.create_dcf_Agent_distribution(nbagent, method = 'naive_eq')
    dcf_file.save()
    
    return dcf_file.path,dcf_file.filename
def generate_distribution(argsDict,gen_path,java_args=[]) :
    if '_kmet' in argsDict['dist'] :
        p,n=generate_kmet_distribution(argsDict,gen_path,java_args)
    elif '_naiveEq' in argsDict['dist']:
        p,n=generate_naiveEq_distribution(argsDict, gen_path)
    if n != argsDict['infile']+argsDict['dist']:
        raise Exception('PROBLEME GENERATION DISTRIBUTION :'+ n+'not eq to : '+argsDict['infile']+argsDict['dist'])
    return p,n

def generate_MONO_problem_dependencies(argsDict, prefix = ''):
    output_filename = argsDict['infile'] + argsDict['var']
    isDistributed = True        
    argsDict['verbose'] = True 
    argsDict['csq_mono'] = GEN_PATH + output_filename+'_MONO'
    try:
        argsDict['dist']       
    except KeyError :
        isDistributed = False
        argsDict['dist'] = None
        argsDict['numagent'] = None
    if isDistributed :
        if '2' in argsDict['dist'] or '4' in argsDict['dist']: # on n'essaie qu'avec ceux la
            #copy_distribution
            print 'HERERER'
            #origin_dist_filename = argsDict['distfile_name']
            #origin_dist_filepath = argsDict['distfile_path']
            #dist_file = par.FileDCF(origin_dist_filepath, origin_dist_filename)
            #dist_file.load()
            #dist_outfilename = argsDict['infile'] + argsDict['dist'] 
            #dist_outfilepath = argsDict['infile_path']
            #dist_file.save(dist_outfilepath,dist_outfilename)
            generate_distribution(argsDict, GEN_PATH,java_args=JAVA_ARGS) 
            outputs_config_file_one_row(argsDict,MULTI_PROBLEMS_FIELDNAMES_ORDER, prefix+MULTI_PROBLEMS_FILENAME,'.csv',GEN_PATH, lock=lock_MULTI)    
    
def launch_MULTI_problem(paramDict):
    log_filename = paramDict['outfile']+'_'+paramDict['dist']
    with open(log_filename + '.log', 'w') as log_file :
        try:
            addToLog(log_file,['LAUNCH MULTI PROBLEM############################'])
            args = computeArgs(CFLAUNCHER_JAR, paramDict,JAVA_ARGS)
            addToLog(log_file,args)
            #run        
            log=jarWrapper(*args)
            addToLog(log_file,log)
            
            addToLog(log_file,['LAUNCH CMP CSQ##################################'])        
            csq_mono_filename = paramDict['csq_mono']
            csq_multi_filename = paramDict['csq']
            csq_stats_filename = csq_multi_filename + '_CMP'        
            args = JAVA_ARGS+[CMPCSQ_JAR]+[csq_multi_filename,csq_mono_filename,csq_stats_filename]
            log = jarWrapper(*args)
            addToLog(log_file,log)
        
            addToLog(log_file,['MERGE STATS####################################']) 
            #regarde dans le outfile et prend en fonction de la méthode...
            #merge le outfile avec les stats.csq et avec le timeout aussi
            #pour chaque methode faire custom
            csqStatsDict = get_csq_cmp_stats(csq_stats_filename)   
            os.remove(csq_stats_filename+'.csv')
            
            statsDict = get_stats(paramDict)    
            filename_stats_temp = paramDict['outfile']+'.csv'
            os.remove(filename_stats_temp)
            #enlever le .csv local inutile
            #je ne suis psa sur que la methode printée prenne en compte les parametres comme l'ordre des TOKEN ou autre
            #c'est pour ca que je le rajoute ici
            #ajouter timeout
            tempDict = dict()
          #  tempDict['method_precision'] = paramDict['method']  
            #using prefix or so there is no collision between all the rest...
            tempDict['or_method'] = paramDict['method']
            tempDict['or_numagent'] = paramDict['numagent']
            tempDict['or_dist'] = paramDict['dist']
            tempDict['or_csq'] = paramDict['csq'] 
            tempDict['or_csq_mono'] = paramDict['csq_mono'] 
            
            tempDict['infile_path'] = paramDict['infile_path']
            tempDict['infile'] = paramDict['infile']
            tempDict['var'] = paramDict['var']
            tempDict['timed_out'] =from_boolean_to_int( is_timeout_from_file(paramDict, log_file) )
            statsDict.update(csqStatsDict)
            statsDict.update(tempDict)
            
            addToLog(log_file,statsDict)
            outputs_config_file_one_row(statsDict, statsDict.keys(),MULTI_PROBLEMS_ALLSTATS_FILENAME,'.csv',GEN_PATH,lock=lock_MULTI_ALLSTATS)
        except Exception as e:
            addToLog(log_file, [str(e)])
            outputs_config_file_one_row(argsDict,FAILED_MULTI_PROBLEMS_FIELDNAMES_ORDER,FAILED_MULTI_PROBLEMS_FILENAME,'.csv',GEN_PATH, lock=lock_FAILED_MULTI)    


def generate_MULTI_config_to_file_from_fail( prefix= ''):
    '''
    a partir du fichier contenant les variantes de problemes solvables,
    générer les parametres pour les differents algos multi-agents dans un fichier
    '''
    parameters = TIMEOUT_MULTI,  METHODS, NUMAGENT_LIST
    list_parameters_MULTI = generate_algos_parameters(prefix +MULTI_PROBLEMS_FILENAME,
                                                      '.csv', parameters, 
                                                      GEN_PATH)

    outputs_config_file_all_rows(list_parameters_MULTI, 
                                MULTI_PROBLEMS_ALGO_PARAMETERS_FIELDNAMES_ORDER, 
                                prefix+MULTI_PROBLEMS_ALGO_PARAMETERS_FILENAME, 
                                '.csv',GEN_PATH,lock=None)
    
def init(l_mono,l_multi,l_allstats, l_multi_algo, l_failed_mono, l_failed_multi):    
    global lock_MULTI_algos_p    
    global lock_FINISHING_MONO
    global lock_MULTI 
    global lock_MULTI_ALLSTATS
    global lock_FAILED_MONO
    global lock_FAILED_MULTI
    
    lock_MULTI_algos_p = l_multi_algo
    lock_MULTI = l_multi
    lock_MULTI_ALLSTATS = l_allstats
    lock_FINISHING_MONO = l_mono    
    lock_FAILED_MONO = l_failed_mono
    lock_FAILED_MULTI = l_failed_multi
    
if __name__ == '__main__':
    lock_mono=mp.Lock()
    lock_multi = mp.Lock()
    lock_allstats = mp.Lock()
    lock_multi_algo = mp.Lock()
    lock_failed_mono = mp.Lock()
    lock_failed_multi = mp.Lock()
    
    pool = mp.Pool(PROCESSES,initializer=init, initargs=(lock_mono,lock_multi,lock_allstats,lock_multi_algo,lock_failed_mono,lock_failed_multi ))
    print 'pool = %s' % pool        
    
    print 'ee'
    
    #read failed mono problems
    failed_mono_list = []
    filename = GEN_PATH+ FAILED_MONO_PROBLEMS_FILENAME + '.csv'
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for rowDict in reader:
            failed_mono_list.append(rowDict)
    prefix = 'FAILTRY'
        
    print 'eavant generat dependence'
    #generate dependencies
    pool.map(generate_MONO_problem_dependencies,failed_mono_list)
    print 'apresgenerat dependence'
    #generate multi algo parameters
    
    generate_MULTI_config_to_file_from_fail( prefix= prefix)
    
    print 'multi from fail'
