# Changelog


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

