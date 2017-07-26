#Visualizer

The visualizer is a tool to visualize asprilo problems. It also provides tools to edit and create asprilo instances. For more informations to the general asprilo problem see: <https://github.com/potassco/asprilo/tree/master/docs>

#Requirments

You need Python 2.7, PYQT 5.0 or newer and clingo 5.2 or newer to run the visualizer.

#Execution

You can run the visualizer by calling `visualizer` in your console.

##Arguments

The visualizer accepts following arguments. You can aslo call `visualizer --help` for more information:  

*`-d/--directory`: Sets the default directory. The file browser will show directory and files in this directory and all file dialogs for saving and loading files will have this as default directory.
*`-t/--templates`: A list of files that will be loaded at the beginning.
*`-l/-layouts`: Same as `-t/--templates`.
*`-p/--plans`: Same as `-t/--templates`.
*`-s/--start_solver`: Starts the default solver at the beginning and connect the visualizer to it. The default solver is the solver described in the setting file.
*`-m/--mode`: Starts the visualizer in a specific mode. A mode is a preset of low-level settings. It turns on and off some features. By default all features are activated. Possible modes are currently gtapf, complete and asprilo.

##Piping 

The visualizer accepts piping from another program such as clingo.  
E.g run `clingo [ARGUMENTS] | visualizer [ARGUMENTS]` to pipe a clingo solution directly to the visualizer.  
Your encoding should contain `#show init/2.` and `#show occurs/3.` statements to pipe correct. It also accepts input in asp format.  
E.g:  
init(object(robot, 1), value(at, (1,1))).  
occurs(object(robot, 1), action(move, (0,1), 1)).  

#Loading Instances/Plans

The visualizer provides different ways to load an instance or a plan:
1. Load an instance/plan with the arguments `-t/--templates`, `-l/-layouts` or `-p/--plans`.
2. Pipe an instance/plan into the visualizer. 
3. Use the file dialogs `File->Load instance [STRG + L]` or `File->Load plan [STRG + V]` to load an instance or a plan.
4. Double left click on an file in the file browser to load an instance or right click and then press `load instance` or `load plan` to load an instance or a plan.
5. Right click on a file in the file browser and than press `parse file` to load an instance or a plan.

If you load an instance via 3 or 4 the visualizer will override the current model with the loaded instance. If you load a plan via 3 or 4 it will override the current actions with the loaded plan. This will not delete objects like shelves or robots. You should load a compatible instance before loading a plan.
If you load an instance or a plan via 5 this will override nothing. It will add every loaded atom from the file to the current model.
When an instance is loaded a png file that represents the instance will be created automatically. This can be disabled in the settings. To create png files of all instance (.lp) files in one directories and all sub directories use `File->Create all png files`.
The file browser will only be shown if you use the `-d/--directory` arguments. It can also be toggled on and off in the menu `Tools->File browser [STRG + F]`.

#Control

Use the `> [UP]` button to go one step forward in the plan or the `< [Down]` button to go one step backward. You can pause and unpause the automated visualisation with the `|> [Space]` or `|| [Space]` buttons. The `|<|< [Left]` and `|>|> [Right]` buttons speeds the visualisation up or slows it down. To skip to the end of the plan or restart it use the `>|` and `|<` buttons. You can use the mouse wheel, the `+` and `-` buttons or the `+` and `-` keys to zoom in and zoom out.

#Parser

You can open the parser with the `[STRG + P]` keys or the menu `Tools->Parser`. The parser shows all loaded instances in the left text field. If more than one instance is loaded you can use the tabs to switch between them. The instances can be modified. The right text field shows all atoms that are currently in the solvers model. Use the `reset grounder` button to clear them. The `reset actions` button will clear all current actions in the current model while the `reset model` button will clear the whole model including all objects and all actions. You can reload the current shown program with `reload program` and delete it with `delete program`. `delete programs` will delete all current loaded instances from the parser and will reload all defalut files that are set in the settings. `parse programm` will sent all instances to the solver and start the solving process. The resulting model will be added to the current model. To load an instance use the methods described at [Loading Instances/Plans](#Loading Instances/Plans).

#Editor

The visualizer allows also the editing of instances. You can [load an instance](#Loading Instances/Plans) or create a new one `File->New instance [STRG + N]`. To remove or add objects right click on a node on the model display. Objects can also be moved via drag and drop from one node to another. Use the grid size window `Tools->Grid Size` to adjust the grid of the instance. Products can be edited in the orders window `Tools->Orders`. To add a product right click on a shelf and choose `add product`. right click on a product entry and then click on `remove product` to remove a product from a shelf. Orders can be edited the same way via the orders window `Tools->orders`. You can edit an instance until the instance was sended to the solver or a plan was loaded. As soon as one `occurs` atom was added to the model it is no longer possible to edit it. To save an instance use `File->Save instance [STRG + I]`. To save a plan use `File->Save plan [STRG + A]`.

#Solver

You can use a solver script to solve instances and get plans as solution. The visualizer provides a few default solver scripts and encodings. You can find them in the scipts directory. A solver script can be started separately or with the `Network->Initialize solver` option. If you start it from the visualizer you can enter a command line to start the solver and it will be connected automatically to the visualizer. Use`Network->Solve` now to send the current model to the solver. Enter the port and host of the the solver in the opened dialog. For a local solver use 127.0.0.1 as host. You can use `Network->Fast solve` or `[STRG + S]` keys to skip the host and port dialog. In this case the visualizer will choose default values. As soon as the solver sends a solution to the visualizer the visualizer can display the received actions. If you load a new instance while the solver is solving this will not reset the solver and you can receive wrong actions. To reset the solver you must send a new instance to it. 

#Simulator
