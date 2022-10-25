from opyenxes.data_in.XUniversalParser import XUniversalParser
from opyenxes.classification.XEventAttributeClassifier import XEventAttributeClassifier
import xml.etree.ElementTree as ET
from ltlf2dfa.parser.ltlf import LTLfParser
import string
import subprocess
import os
import numpy as np
import argparse
from datetime import datetime
import re

def createFormula(s):
    s = s.replace("u"," U ")
    s = s.replace("\/"," | ")
    s = s.replace("/\ "," & ")
    s = s.replace("[]"," G ")
    s = s.replace("x"," X ")
    s = s.replace("<>"," F ")
    return s

def activity(a):
    A = ''
    for i in a:
        A += 'act_'+str(i)+' '
    A += '- activity '
    return A


def traceState(tS):
    trace_state = ''
    for i in tS:
        trace_state += 't'+i+' '
    trace_state += '- trace_state '
    return trace_state

def automatonState(aS):
    automaton_state = ''
    for i in aS:
        for j in i:
            automaton_state += 'a'+j[0]+'_'+j[1]+' '
    automaton_state += '- automaton_state '
    return automaton_state

def currentState(cs):
    cur_states = ''
    for i in cs:
        for j in i:
            cur_states += '(cur_state a'+j[0]+'_'+j[1]+') '
    return cur_states

def TcurrentState(cs):
    cur_states = ''
    for i in cs:
        cur_states += '(cur_state t'+i+') '
    return cur_states

def TfinalState(fs):
    final_state = ''
    for i in fs:
        final_state += '(final_state t'+i+') '
    return final_state

def finalState(fs):
    final_state = ''
    for i in fs:
        for j in i:
            final_state += '(final_state a'+j[0]+'_'+j[1]+') '
    return final_state


def traceInit(tI):
    ti = ''
    for i in tI:
        ti += '(trace t'+i[0]+' act_'+i[1]+' t'+i[2]+') '
    return ti

def automaton(aut):
    ris = ''
    for i in aut:
        for j in i:
            ris += '(automaton a'+j[0]+'_'+j[1]+' act_'+j[2]+' a'+j[0]+'_'+j[3]+') '
    return ris

def createGoal(Tdic):
    g = '(:goal (and '
    g += TcurrentState(Tdic['cur_state'])
    g += '(forall (?s - automaton_state) (imply (cur_state ?s) (final_state ?s)) )'
    g += ') )\n'
    return g

def createInit(Tdic):
    i = '(:init '
    i += traceInit(Tdic['trace'])
    i += currentState(final_init['cur_state'])
    i += TcurrentState(Tdic['cur_state'])
    i += finalState(final_init['final_state'])
    i += TfinalState(Tdic['final_state'])
    i += automaton(final_init['automaton'])
    i += ')\n'
    return i

def createObjects(Tdic):
    o = '(:objects '
    o += automatonState(final_objects['automaton_state'])
    o += activity(final_objects['activity'])
    o += traceState(Tdic['trace_state'])
    o += ')\n'
    return o

def startCustomFiles(tracesPath, constraintsPath):
    
    num_files = 1
    averages = np.zeros(num_files)
    averages_cost = np.zeros(num_files)    

    #These lines have to be changed in case of using different files (.xes, .xml or .txt), since the names of the folders are generated basing on the names of the actual ones
    trace = tracesPath.split('/')[-1]
    parent_folder = trace.replace('.txt','')
    folder = datetime.now().strftime("%d_%m_%Y_%H:%M:%S")

    createFolders(parent_folder,folder)
    
    num_traces = initTrace(tracesPath, parent_folder, folder, constraintsPath)

    tot_time_cost, tot_cost = createPlotDataFile(parent_folder, folder, num_traces)

    averages[0]=np.mean(tot_time_cost)        
    averages_cost[0]=np.mean(tot_cost)

    with open('FD_outputsDummyFree/'+str(parent_folder)+'/Obtained averages.txt', "w", encoding="utf-8") as f:
        f.write("Total Time Average: "+str(averages)+'\nTotal Cost Average: '+str(averages_cost))

def createFolders(parent_folder, folder):
    try:
        os.makedirs('./pddl_problemDummyFree_files/'+parent_folder)
    except:
        pass
    
    try:
        os.makedirs('./pddl_problemDummyFree_files/'+parent_folder+'/'+folder)
    except:
        pass
    
    try:
        os.makedirs('./FD_outputsDummyFree/'+parent_folder+'/'+folder)
    except:
        pass
        
    try:
        os.makedirs('./plot_data_DummyFree/'+parent_folder)
    except:
        pass 

def initConstraint(constraintsPath):

    global final_objects, final_init, final_goal

    parser = LTLfParser()

    if constraintsPath.endswith(".txt"):
        txt=True
        xes=False
        try:
            file = open(constraintsPath,"r")
            allc=[]
            rows=file.readlines()
            curr_aut_activities={}
            for l in range(len(rows)):
                f = rows[l].replace("\n", "").strip()
                parameters = re.findall('"(.+?)"',f)
                parameters = list(dict.fromkeys(parameters))
                curr_aut_activities[str(l)] = [x.replace("act_","") for x in parameters]
                allc.append(f)
        except:
            raise IOError('[ERROR]: Unable to import txt file')
    else:
        xes=True
        txt=False
        
        tree = ET.parse(constraintsPath)
        root = tree.getroot()
        allc = root.findall('./assignment/constraintdefinitions/')

    final_objects = {'automaton_state': [], 'activity': [] }
    final_init = {'automaton': [], 'cur_state': [], 'final_state': [] }
    final_goal = {'cur_state': [] }

    for j in range(1,len(allc)+1):

        objects = {'automaton_state': [], 'activity': [] }
        init = {'automaton': [], 'cur_state': [], 'final_state': [] }
        goal = {'cur_state': [] }

        c = allc[j-1]

        if xes==True:
            LTLformula = createFormula(c.find('./template/text').text.replace('"',"").lower())
            formula = parser(LTLformula) 
            dfa = formula.to_dfa(mona_dfa_out=True)
            params = c.findall('./constraintparameters/parameter/branches/branch')
            alph = list(string.ascii_uppercase)[0: len(params)]
            curr_aut_activities = {}
            for i in range(0, len(params)):
                act_id = params[i].get('name').split(' ')[1].split('-')[0]
                curr_aut_activities[alph[i]] = act_id
        elif txt==True:
            formula = parser(c.replace('"', ""))
            dfa = formula.to_dfa(mona_dfa_out=True)
        
        parse = dfa.split('\n')
        var_order = parse[0].split(':')[1].strip().split(" ")
    

        if txt:
            automaActions = curr_aut_activities[str(j-1)]
        else:
            automaActions = curr_aut_activities.values()
        
        externalActions = [x for x in trace_objects['activity'] if x not in automaActions]         
        all_actions = trace_objects['activity']
        for i in automaActions:
            if i not in all_actions:
                all_actions.append(i)

        all_actions = list(map(lambda x: int(x) , all_actions))
        all_actions.sort()
        objects['activity'].append([str(j),list(map(lambda x: str(x) ,all_actions))])

        #Initial State
        init['cur_state'].append([str(j),'1'])

        final_states = parse[2].split(':')[1].strip().split(" ")
        if len(final_states) == 1:
            init['final_state'].append([str(j),final_states[0]])
            objects['automaton_state'].append([str(j),final_states[0]])
            goal['cur_state'].append([str(j),final_states[0]])
        else:
            for i in final_states:
                objects['automaton_state'].append([str(j),i])
                init['final_state'].append([str(j),i])

        rejecting_states = (parse[3].split(':')[1].strip().split(" "))
        rejecting_states.remove('0')
        for i in rejecting_states:
            objects['automaton_state'].append([str(j),i])

        for s in parse:
            if 'State' in s:
                if 'State 0' in s:
                    continue

                temp = s.split(':')
                s1 = temp[0].replace("State ","")            
                temp = temp[1].split('->')
                act = [i for i in temp[0].strip()]
                s2 = temp[1].strip().replace("state ","")

                #Discards loops (=from a state to the same state).
                #We can apply this modification to the automata because
                #we have a codification on the "current state" and a loop
                #does not move the current state so we can discard it.
                if s1==s2:
                    continue

                newAct = act

                newAct = list(filter(('X').__ne__, newAct))
                s = sum(list(map(lambda x: int(x),newAct)))
                
                #If the sum > 1 it means we have multiple events true in a given instant of time
                #but in BP we can have only 1 event at time. Hence, we can discard this transition.
                if s > 1:
                    continue
                #If the sum = 1 it means we have a value true and the others are 0 or X. The X can be only 0
                #because if we set them as 1 we will have a value multiple events true in the instant of time.
                elif s == 1:
                    
                    if xes==True:
                        action = var_order[act.index('1')]
                        act = curr_aut_activities[action]
                    else:
                        action = act.index('1')
                        act = curr_aut_activities[str(j-1)][action]
                    init['automaton'].append([str(j),s1,act,s2])
                
                else:
                    #Case: all X are 0
                    for i in externalActions:
                        init['automaton'].append([str(j),s1,i,s2])
                    
                    #Case: one X at time is 1
                    indices = [index for index, element in enumerate(act) if element == 'X']
                    for i in indices:
                        if xes==True:
                            action = var_order[i]
                            act = curr_aut_activities[action]
                        else:    
                            act = curr_aut_activities[str(j-1)][i] 

                        
                        init['automaton'].append([str(j),s1,act,s2])
                    
        for i in objects.keys():
            final_objects[i].append(objects[i])
        for i in init.keys():
            final_init[i].append(init[i])
        for i in goal.keys():
            final_goal[i].append(goal[i])    


def initTrace(tracesPath, parent_folder, folder, constraintsPath):

    global trace_objects, trace_init, trace_goal
    global final_objects, final_init, final_goal

    if tracesPath.endswith(".txt"):
        try:
            file = open(tracesPath,"r")
            log_list=[]
            row=file.readlines()
            for l in range(len(row)):
                log_list.append(row[l].replace("\n", "").split(" "))
        except:
            raise IOError('[ERROR]: Unable to import txt file')
    else:    
        try:
            with open(tracesPath) as log_file:
                log = XUniversalParser().parse(log_file)[0]
            classifier = XEventAttributeClassifier("Event Name", ['concept:name'])
            log_list = list( map(lambda trace: list(map(classifier.get_class_identity, trace)), log) )
        except:
            raise IOError('[ERROR]: Unable to import xes file')
    
    domain = '(:domain traceAlignmentDomain)\n'
    metric = '(:metric minimize (total-cost))\n)'

    num_traces = len(log_list)
    
    for x in range(0,num_traces):

        trace_objects = { 'trace_state': [], 'activity': [] }
        trace_init = {'trace': [], 'cur_state': [], 'final_state': [] }
        trace_goal = {'cur_state': [] }
        
        namefile = 'traceAlignmentProblemDummyFree_'+str(x)
        problem = '(define (problem '+namefile+')\n'

        trace_init['cur_state'].append('1')

        t = log_list[x]
        num_eve = len(t)+1

        for i in range(1,num_eve):
            if ".xes" in tracesPath:
                e = t[i-1].split(" ")[1]
            else:
                e = t[i-1].split("_")[1]
            if e not in trace_objects['activity']: 
                trace_objects['activity'].append(e)            
            trace_init['trace'].append([str(i),e,str(i+1)])
            trace_objects['trace_state'].append(str(i))

        trace_init['final_state'].append(str(num_eve))
        trace_goal['cur_state'].append(str(num_eve))
        trace_objects['trace_state'].append(str(num_eve))

        initConstraint(constraintsPath)
        
        all_actions = final_objects['activity'][0][0][1]
        for i in range (1,len(final_objects['activity'])):
            for [_,l] in final_objects['activity'][i]:
                for h in l:
                    if h not in all_actions:
                        all_actions.append(h)

        final_objects['activity'] = all_actions 

        problemFile = problem+domain+createObjects(trace_objects)+createInit(trace_init)+createGoal(trace_goal)+metric
        
        with open('./pddl_problemDummyFree_files/'+parent_folder+'/'+folder+'/'+namefile+'.pddl', "w", encoding="utf-8") as f:
            f.write(problemFile)
        print('----Trace Analized %i ----'%x)

    for i in range(0,num_traces):
        s = './fast-downward.py "/home/veronica/Downloads/ReasoningAgents21-main/pddl_domain_file/traceAlignmentDomainDummyFree.pddl" "/home/veronica/Downloads/ReasoningAgents21-main/pddl_problemDummyFree_files/'+str(parent_folder)+'/'+str(folder)+'/traceAlignmentProblemDummyFree_'+str(i)+'.pddl" --search "astar(blind())" > /home/veronica/Downloads/ReasoningAgents21-main/FD_outputsDummyFree/'+str(parent_folder)+'/'+str(folder)+'/FD_outputDummyFree'+str(i)+'.txt'
        p = subprocess.Popen(s, cwd="/home/veronica/Downloads/downward/", shell=True)
        print('----Problem started %i----'%i)
        p.wait()
        print('----Problem finished %i----'%i)
    
    return num_traces


def createPlotDataFile(parent_folder, folder, num_traces):

    filePlotData=open("/home/veronica/Downloads/ReasoningAgents21-main/plot_data_DummyFree/"+str(parent_folder)+"/plot_data_"+str(folder)+".txt", 'w+')
    tot_time_cost=np.zeros(num_traces)
    filePlotData.write("Plan Length;Plan Cost;Total Time\n")
    tot_cost = np.zeros(num_traces)

    for i in range(0,num_traces):
        
        s= 'FD_outputsDummyFree/'+str(parent_folder)+'/'+str(folder)+'/FD_outputDummyFree'+str(i)+'.txt'
        f = open(s,'r')
        r = f.readlines()

        for elem in r:

            if "Plan length:" in elem:
                plan_len=elem.split(':')[1].strip().split(' ')[0]
                filePlotData.write(plan_len+";")

            if "Plan cost:" in elem:
                plan_c=elem.split(':')[1].strip()
                filePlotData.write(plan_c+";")
                tot_cost[i] = plan_c                

            if "Total time:" in elem:
                tot_time=elem.split(':')[1].strip().replace('s', '')
                tot_time_cost[i]=tot_time
                filePlotData.write(tot_time+";\n")
                    
    filePlotData.close()

    return tot_time_cost, tot_cost

def startDatasetFiles(tracesPath, constraintsPath):

    num_files = 1
    averages = np.zeros(num_files)
    averages_cost = np.zeros(num_files) 
    trace = tracesPath.split('/')[-1]

    if tracesPath.endswith(".xes"):
        
        parent_folder = "".join(str(item)+"-" for item in trace.split('-')[:5])
        folder = trace.replace('.xes','')
    else:
        parent_folder = trace.replace('.txt','')
        folder = datetime.now().strftime("%d_%m_%Y_%H:%M:%S")


    createFolders(parent_folder,folder)
    
    num_traces = initTrace(tracesPath, parent_folder, folder, constraintsPath)

    tot_time_cost, tot_cost = createPlotDataFile(parent_folder, folder, num_traces)
    averages[0]=np.mean(tot_time_cost)        
    averages_cost[0]=np.mean(tot_cost)

    with open('FD_outputsDummyFree/'+str(parent_folder)+'/Obtained averages.txt', "w", encoding="utf-8") as f:
        f.write("Total Time Average: "+str(averages)+'\nTotal Cost Average: '+str(averages_cost))
    

trace_objects = {}
trace_init = {}
trace_goal = {}
final_objects = {}
final_init = {}
final_goal = {}

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Aligns the given trace with the given constraints.')
    parser.add_argument('--Traces', metavar='T', type=str,
                        help='Path of the file that contains the traces')
    parser.add_argument('--Constraints', metavar ='C', type=str,
                        help='Path of the file that contains the constraints')
    
    args = parser.parse_args()
    tracesPath = args.Traces
    constraintsPath = args.Constraints

    if (tracesPath.endswith('.xes') or tracesPath.endswith('.txt')) and (constraintsPath.endswith('.xml') or constraintsPath.endswith('.txt')):
        startDatasetFiles(tracesPath, constraintsPath)
    else:
        print(' File extensions non valid or incompatible. They must be ".xes" and ".xml" or both ".txt" ')
