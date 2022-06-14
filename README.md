# Simulated Autopoiesis in Liquid Automata

Living systems cannot be understood separately from they environment they live in. They are organised in a causal circular process of becoming, and it is this very circularity that is a necessity for living – autopoietic - systems. An autopoitetic system is alive if it produces itself in the physical space, based on interactions between physical elements that go on to produce new physical elements necessary for the regeneration of the system. A living system is a self-referential domain of interactions in the physical space, generally a network of 'chemical' relationships. However, there are many kinds of chemical networks that aren't alive, consider a chemical explosion which exhibits a runaway chain reaction of positive feedback. The signature of life is the emergence of a structure that distinguishes self from non-self; it is closed-off from its environment. This closure emerges from, and is dynamically/homeostatically, maintained by the underlying organisation.

Simluated autopoiesis is a demonstration of how autopoiesis works, but is not itself alive because software operates in a virtual rather than a physical space. The system is defined as a network of simulated chemical reactions, bathed in a liquid substrate that provides the raw materials from which the system builds itself. The seed is a catalytic agent that transforms the substrate into its structural building blocks. These are able to self-assemble, forming a boundary around the catalyst.

## Installation

1. Install [PyBox2D](https://github.com/pybox2d/pybox2d):
  * conda create -n pybox2d -c conda-forge python=3.6 pybox2d
  * conda activate pybox2d
  * pip install pygame
2. Download the python code in this GitHub: auto.py
3. Run auto.py:
  * python -m auto --backend=pygame 

Humberto Maturana, Francisco J. Varela, _Autopoiesis and Cognition_, D. Reidel Publishing Co., 1972.  
Francsico Varela, _Principles of Biological Autonmy_, North Holland, 1979.  
Hordijk, W., Steel, M. _Autocatalytic sets and boundaries_, J Syst Chem 6, 1, 2015.  


![Autopoiesis screenshot](images/ScreenShot.png)

![Autopoiesis animation](images/animation.gif)
