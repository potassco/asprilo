#Vorrausetzungen

Zur Ausführung des Visualizers werden Python 2.7 (nicht 3.0), PYQT 5.0 oder neuer und clingo 5.0 oder neuer benötigt.

#Ausführung

Das Programm wird über die Konsole mit dem Befehl "python visualizer.py" gestartet. Es können noch
zusätzliche Argumente angegeben werden. So kann man z.B mit `-d / --directory` das Programm in einem
beliebigen Verzeichnis öffnen. Mit dem Befehl "python visualizer.py -d ." wird das Programm in
dem aktuellen Arbeitsverzeichnis geöffnet werden. Der Befehl "python visualizer.py -h" zeigt weitere
verfügbare Argumente an. 

#Laden von Instanzen 

Eine Instanz kann über das Menü `"File" -> "Load instance"` oder über den Dateibrowser mit Doppelklick
auf eine Instanz Datei geladen werden. Über `"File" -> "New instance"` können neue saubere Instanzen
erstellt werden. Eine Instanz kann solange bearbeitet werden bis der Solver für diese Instanz
aufgerufen wird. Sobald der Solver für eine Instanz aufgerufen wurde muss die Instanz neu geladen
oder eine neue Instanz erstellt werden, um sie wieder zu bearbeiten. Beim Laden der Instanz
speichert der Visualizer eine Darstellung der Instanz unter dem gleichen Namen wie die Instanz als
png automatisch.

#Bearbeiten von Instanzen

Objekte einer Instanz wie robot, shelves und `"picking stations"` können im
Instanz-Darstellungsfenster über das Kontextmenü, welches per Rechtsklick auf eine Node aufgerufen
wird, bearbeitet werden. So können Objekte entfernt und hinzugefügt werden. Außerdem lassen sich
über das Kontextmenü einzelne Nodes zu Highways erklären und Nodes entfernen oder hinzufügen. Die
Größe der Instanzen lässt sich über das Menü `"Windows" -> "Set grid size"` einstellen. Um products zu
einem shelf hinzuzufügen oder zu entfernen, kann über `"Windows" -> "Show products"` ein neues Fenster
geöffnet werden. Ein Rechtsklick auf ein shelf oder ein product öffnet ein Kontextmenü, das dies
ermöglicht. Orders können entsprechend über das Menü `"Windows" -> "Show orders"` bearbeitet
werden. Bearbeite Instanzen können mit `"File" -> "Save instance"` gespeichert werden.

#Solver 
Um eine Instanz einem Programm zum solven zu übergeben, kann über `"Solver" -> "Initialize solver"`
mit einem Kommandozeilenbefehl ein Solver gestartet werden. Dies startet lediglich den Solver und
stellt noch keine Verbingung zwischen Solver und Visualizer her. Die geladene Instanz kann nun über
`"Solver" -> "Solve"` dem Solver übergeben werden. Hierzu müssen host und port des Solvers eingegeben
werden. Um die Instanz einem lokalen Solver zu übergeben, muss der host auf "127.0.0.1" gestetzt
werden. Sollte noch keine Verbindung zu einem Solver aufgebaut sein, wird dann eine Verbindung
aufgebaut, falls dies möglich ist, und die Instanz an den Solver gesendet. Falls bereits eine
Verbindung besteht wird, falls sich port oder ip geändert haben die alte Verbindung getrennt und
eine neue aufgebaut, ansonsten wird die neue Instanz an den gleichen Solver gesendet. So muss ein
Solver nur einmal initialisiert werden, um mehrere Instanzen zu lösen. Lösungen für eine Instanz
können mit `"File" -> "Save answer"` gespeichert und später über `"Visualize answer"` wieder angezeigt
werden. Um eine Lösung zu Laden muss vorher die entsprechende Instanz geladen werden.

#Solver-Visualizer-Kommunikation

Nachdem der Visualizer eine Verbindung mit dem Solver aufgebaut hat werden die einzelnen asp Atome
an den Solver gesendet. Diese werden mit einem "." von einander getrennt. Nachdem das Senden der
Instanz abgeschlossen ist wird "\n" gesendet. Der Visualizer wartet dann, dass der Solver eine
Antwort sendet. Diese sollte die entsprechenden Atome zum lösen der Instanz also occurs-Atome
beinhalten. Folgende keywords sind für die Kommunikation reserviert: `%$RESET` teilt dem SOlver
mit, dass es sich um eine neue Instanz handelt.

#Online

Work in progress.
