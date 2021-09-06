# Changelog

## 0.4.0

### Added

-   Docs:
    - Add specification for new domain Md

-   Misc:
    - Add script to convert instance between M-domain and Md-domain

### Changed

-   Generator:
    - Revise for clingo 5.5 compatibility
-   Visualizer:
    - Revise for clingo 5.5 compatibility

### Fixed

-   Checker:
    - Fix checker to detect swapping conflicts
-   Generator:
    - Fix incompatibility between incremental mode (`-I`) and cli option `--oap`

## 0.3.0

### Added

-   Docs:
    - Add detailed documentation of experiments of ICLP'18 paper
    - Add scientific publications to index page
    - Exhaustively update visualizer page
-   Generator:
    - Add aspif output for debugging
    - Add provenance (original cli invocation) to generated instances
    - Add the number of order lines to instance file names
-   Visualizer:
    - Table with detailed robot information
    - Highlighting for selected robots
    - Add ability for robot path drawing
    - Add energy management for robots
    - Add energy overview to the robots table
    - Add energy display to the model view
    - Update visualizer for noarch conda version
    - Delivery actions can now be performed simultaneously to other actions
    - Multiple delivery actions can now be performed at one time step by one agent

### Changed

-   Generator:
    - Update to python 3
    - Make compatible with/require cingo>=5.4.0
    - Simplify generator code
    - Use conda as recommended installation method
-   Visualizer:
    - Update to python 3
    - Make compatible with/require clingo>=5.4.0
    - Windows can now be dragged and dropped
    - Update solver and simulator script
    - Performance improvements
    - Use conda as recommended installation method
-   Misc:
    - Added conda recipes for both visualizer and generator to potassco's recipes repo at <https://github.com/potassco/conda/tree/master/asprilo>

### Fixed

-   Docs:
    - Fix several formatting and linking issues, also wrt jekyll/gh-phages
-   Checker:
    - Fix issues #25, #26
-   Generator:
    - Fix various bugs
-   Visualizer:
    - Fix various bugs


## 0.2.0

### Added

-   Docs:
    - Add description for checker
    - Add description for experiments
-   Checker:
    - Add checker for C and M domain
-   Generator:
    - Add incremental multi-shot generation to manage grounding size
    - Add a multitude of generator options to fine-tune the resulting instances
    - Add support for YAML-formatted batch scripts
    - Add batch generation scripts for different domains and layouts
    - Add ground program observer for analytical output of grounding size
-   Visualizer:
    - Add support for manually adding orders via GUI
    - Add rudimentary support to stream orders
    - Add rudimentary support for exogenous events
    - Add various convenience features to GUI
    - Add various command line options and piping support
-   Misc:
    - Add new small example instance

### Changed

-   Docs:
    - Migrate from org-mode to markdown format
    - Revise specification
    - Revise description of the generator, visualizer and instance sets
-   Checker:
    - Revise checker for A and B domain
-   Generator:
    - Refactor code to support different generation modes
    - Change generator ASP encoding to reduce grounding size
    - Remove python batch scripts
    - Rename main generator script to `gen`
-   Visualizer:
    - Refactor whole source code for better maintainability and robustness
    - Make windows for orders and inventory dockable in sidebar
    - Rename main visualizer script to `viz`
-   Misc:
    - Remove old example instance

### Fixed

-   Docs:
    - Fix incorrect links and missing images in documentation
-   Generator:
    - Fix exception for invocation w/o arguments
    - Fix solve calls to work with clingo 5.2.x API
-   Visualizer:
    - Fix closing of sockets after communication with solver terminates
    - Fix solve calls to work with clingo 5.2.x API


## 0.1.0

Initial Release

