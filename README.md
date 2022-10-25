# Trace Alignment Problem (Reasoning Agents Project 2021)

## Introduction
The trace alignment problem comes from the business process management (BPM) discipline. A definition of this problem can be found in the paper [van der Aalst, 2016]: “The Trace Alignment is the problem of “cleaning” and “repairing” dirty traces to make them compliant with the underlying process model”. Basically, this problem consists in checking if sequences (called traces) of single actions (called events) conform to the expected process behavior and if not, changing as little as possible the traces, by adding or removing events, in order to align them to the standard process. In the paper “On the Disruptive Effectiveness of Automated Planning for LTLf -based Trace Alignment” [De Giacomo,Maggi,Marrella,Patrizi], that we have studied for this project, the authors provided a technique to synthesize the alignment instructions relying on finite automata theoretic manipulations. This technique can be effectively implemented by using planning technology which allows to outperform the results obtained with ad-hoc alignment systems. Specifically, in [De Giacomo,Maggi,Marrella,Patrizi] the traces analyzed are sequences of activity names, while the process behavior is specified by using a declarative approach, i.e. through some constraints defined in LTLf (Linear Temporal Logic over finite traces [De Giacomo and Vardi 2013]). The goal of the trace alignment problem is to make the traces conform with the process by satisfying the constraints defined in LTLf. The proposed approach used the cost-optimal planning to find a successful plan of minimal cost to achieve this goal. In this type of planning the actions have a cost, in particular, adding and removing events have a non-zero cost while moving on the original trace has a zero cost. As previously said, the standard process is defined with a declarative approach, specifically through constraints defined with LTLf formulas coming from DECLARE models. In detail, a DECLARE model consists of a set of constraints (i.e. rule templates applied to activities) and their semantics can be formalized using LTLf in order to make them verifiable and executable. The encoding of the trace alignment problem, proposed in [De Giacomo,Maggi,Marrella,Patrizi], is performed by using PDDL and the results are compared with a technique specifically tailored for the alignment problem (de Leoni, Maggi, and van der Aalst 2012; 2015) and previous approaches based on classical planning (De Giacomo et al. 2016). For our Reasoning Agent’s project we implemented the solution described in [De Giacomo,Maggi,Marrella,Patrizi] and we improved it by slightly modifying the proposed encoding. Also, for the experiments, differently from the analyzed paper, we created a general script that can be used with any kind of LTLf formula, i.e not only with the one coming from DECLARE models. We were able to use any LTLf formula thanks to the LTLf2DFA tool, developed by Francesco Fugitti, which allows us to create from a general LTLf formula the associated DFA. Finally, we compared the results obtained with our implementation of the encoding proposed in the paper, our modified version of the proposed encoding and the results shown in the paper. 


## Requirements
- Python 3.6 or 3.7

- OpyenXES 0.3.0

- LTLf2DFA 1.0.1

- Mona 1.4-18

- Fast Downward 20.06

- numpy 1.21.1

- matplotlib 3.4.2



## How to execute the code
From the CLI (Command Line Interface), give the following command:\
```python <script Name>.py --Traces “ < path of the trace file> (.xes or .txt)” --Constraints “<path of the constraint file> (.xml or .txt)”  ```

The "createProbPddl.py" script performs our modified version of the encoding proposed in the studied paper. 
 
The "createProbPddlDummyFree.py" script performs our implementation of the encoding proposed in the studied paper. 
 
After starting for the first time the createProbPddl.py script, the following folders will be created:
- FD_outputs;
- pddl_problem_files;
- plot_data.
 
After starting for the first time the createProbPddlDummyFree.py script, the following folders will be created:
- FD_outputsDummyFree;
- pddl_problemDummyFree_files;
- plot_data_DummyFree.
 
Specifically:
- FD_outputs/FD_outputsDummyFree: inside these folders the outputs of the Fast Downward planning system are stored;
 
- pddl_problem_files/pddl_problemDummyFree_files: inside these folders the problem files (in pddl) generated from the algorithms are stored. 
 
- plot_data/plot_data_DummyFree: inside these folders the total time and the plan cost, for each planning problem created, are stored. 
 
In addition, if a txt file is given as argument to the parameter "--Traces" of the scripts, a subfolder "traces" is created inside the following folders:
- FD_outputs;
- pddl_problem_files;
- plot_data.
 
To recognize the different executions of the scripts when the traces in input are contained in a txt file, the results are inserted inside a subfolder of "traces" named as the time and the day in whitch the script was started. 
 
The results of our tests can be found at the following link: https://drive.google.com/drive/folders/1qNv0RIBZiIt1Sl5kqt4Nfydv3b4dscvK?usp=sharing

### !!IMPORTANT!!
We wrote these scripts in order to be executed with the files contained in the dataset. Hence, the names of the sub-folders contained in the folders explained before are generated starting from the names of the dataset files. In order to run files xes not contained in the original dataset, you have to change the way in which the "parent_forlder" and the "folder" variables are generated at the line 117 in "createProbPddlDummyFree.py" or at the line 132 in "createProbPddl.py". These two variables are used to create the following folders: 

For example inside FD_OUTPUT: 

|---FD_OUTPUT

.....|---"parent_folder"

...........|---"folder"

.................|---"fd_output.txt"                 

## Team
Alessia Carotenuto \
Emanuele Iacobelli \
Veronica Romano 

## References

- Giuseppe De Giacomo, Fabrizio Maria Maggi, Andrea Marrella, and Fabio Patrizi. On the disruptive effectiveness of automated planning for LTLf - based trace alignment. In Proceedings of the AAAI Conference on Artificial Intelligence, volume 31, 2017.

- Giuseppe De Giacomo, Fabrizio Maria Maggi, Andrea Marrella, and Sebastian Sardina. Computing trace alignment against declarative process models through planning. In Twenty-Sixth International Conference on Automated Planning and Scheduling, 2016.

- Giuseppe De Giacomo and Moshe Y Vardi. Linear temporal logic and linear dynamic logic on finite traces. In Twenty-Third International Joint Conference on Artificial Intelligence, 2013.

- Massimiliano De Leoni, Fabrizio M Maggi, and Wil MP van der Aalst. An alignment-based framework to check the conformance of declarative process models and to preprocess event-log data. Information Systems, 47:258–277, 2015. 

- Massimiliano De Leoni, Fabrizio Maria Maggi, and Wil MP van der Aalst. Aligning event logs and declarative process models for conformance checking. In International Conference on Business Process Management, pages 82–97. Springer, 2012. 

- Wil MP Van Der Aalst, Marcello La Rosa, and Flávia Maria Santoro. Business process management, 2016. 
