# Simulated Autopoiesis in Liquid Automata

Living systems cannot be understood separately from they environment they live in. They are organised in a causal circular process of becoming, and it is this very circularity that is a necessity for living – autopoietic - systems. An autopoietic system is alive if it produces itself in the physical space, based on interactions between physical elements that go on to produce new physical elements necessary for the regeneration of the system. A living system is a self-referential domain of interactions in the physical space, generally a network of 'chemical' relationships. However, there are many kinds of chemical networks that aren't alive, consider a chemical explosion which exhibits a runaway chain reaction of positive feedback. The signature of life is the emergence of a structure that distinguishes self from non-self, closing it off from its environment. This closure emerges from, and is dynamically and homeostatically maintained by, the underlying organisation. There are thus , two key components to autopoiesis:

1. Organisational closure: A network of the processes of production. e.g. a chemical reaction system
2. Maintenance of Identity: The appearance of a homeostatically maintained boundary that divides self from non-self. e.g. a cell-wall

Simulated autopoiesis is a demonstration of how autopoiesis works and enables us to study simpler autopoietic systems not found in nature. We define an organisationally closed system, with the aim of generating structural closure. The system explored here is defined as a organisationally closed chemical reaction system (CRS), bathed in a liquid substrate that provides the raw materials from which the system builds itself. The seed is a catalytic agent (triangle) that transforms the substrate (circles) into its structural building blocks (squares). The system, in effect, feeds off the substrate particles. The link particles are able to self-organise (blue links) themselves into a structure akin to a long-chain polymer. This long chain of bonded links is able to wrap around and close in on itself to form a closed boundary, analogous to a cell wall enclosing the catalyst.

<image width=300 alt="autopoiesis screenshot" src="images/ScreenShot.png">

This is a 2D particle simulation with additional rules about how particle state changes on contact with other particles. Unlike cellular automata, there is no fixed grid, just particles moving about and colliding with each other in a continuous space. Similarly, there is no clock setting the beat on which the rules are applied; time is continuous and the rules are applied when objects collide, or spontaneously. By analogy with cellular automata, we call this a 'Liquid Automaton', a variety of _collision-based_ system. This system is based on just three rules, defined below, based on a _cellular_ automaton devised by Varela. These rules are invoked on contact (as with rules 1 and 2), or may occur spontaneously (as with rule 3).

1. composition: K + 2S -> K + L
2. concatenation: L<sup>n</sup> + L -> L<sup>n+1</sup>
3. disintegration:  L -> 2S

Where:
* K - catalyst (triangle)
* S - substrate (circle)
* L - link (square)

Composition only occurs when a catalyst comes into simultaneous contact with a pair of substrate particles, which are then fused together to form a link particle. Concatenation enables the self-organisation of the boundary. Links are able to make up to two connections, and when two links collide, and are able to do so, they form a bond between them (shown as a blue line). As these links are being formed around the catalyst, it's likely that the bonded links will close the circle, enclosing the catalyst. The embodiment of the catalyst as a shape with a certain extent, creates an internal pressure that holds the links apart, (mostly) preventing them forming useless tight enclosures. These 'zombie' structures without a catalyst at their heart, lack the organisation necessary to repair themselves. Links are also subject to decay, and may spontaneously disintegrate back into a pair of substrate particles. Disintegration triggers the homeostatic repair of incomplete boundaries, and also serves to recycle 'waste' links that may have drifted too far from the catalyst, along with the aforementioned Zombies. In this experiment, a single catalyst particle is introduced at the beginning, which is not subject to disintegration. Autopoiesis is intriguing because re-production is not seen as an essential quality of life. Hence, this minimal model is not concerned with the creation of new catalyst.
 
We present a Minimal Autopoietic Simulation, demonstrating both organisational and structural closure. It invites investigation of more interesting chemical networks with more sophisticated metabolisms.
 
This work will be presented at the upcoming [Workshop on Liquid and Colloid Cybernetics](https://eur01.safelinks.protection.outlook.com/?url=https%3A%2F%2Funcomp.uwe.ac.uk%2Fworkshop-on-liquid-and-colloid-cybernetic-systems%2F&data=05%7C01%7CSteve.Battle%40uwe.ac.uk%7Cd4498d42d03549e01bc708da52b0f78f%7C07ef1208413c4b5e9cdd64ef305754f0%7C0%7C0%7C637913217257147321%7CUnknown%7CTWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D%7C3000%7C%7C%7C&sdata=jT%2BiGGcM0iml2c9%2BdojLuQyVrWanomaekxWGksnTdfU%3D&reserved=0) at the Arnolfini, Bristol.

![Autopoiesis animation](images/animation.gif)

## Installation

1. Install [PyBox2D](https://github.com/pybox2d/pybox2d) and [pygame](https://www.pygame.org):
  * conda create -n pybox2d -c conda-forge python=3.6 pybox2d
  * pip install pygame
2. Download the python code in this GitHub: auto.py
3. Run auto.py:  
  * conda activate pybox2d
  * python -m auto --backend=pygame 

## References

Humberto Maturana, Francisco J. Varela, _Autopoiesis and Cognition_, D. Reidel Publishing Co., 1972.  
Francsico Varela, _Principles of Biological Autonomy_, North Holland, 1979.  
Hordijk, W., Steel, M. _Autocatalytic sets and boundaries_, J Syst Chem 6, 1, 2015.  
Tommaso Toffoli, Symbol Super Colliders, in Collision-Based Computing, Andrew Adamatzky (ed.), Springer, 2002.  
Kurt W. Fleischer, A Multiple-Mechanism Developmental Model for Defining Self-Organizing Geometric Structures, California Institute of Technology, 1995  
Randall D Beer, Characterizing autopoiesis in the game of life, Artif Life. 2015 Winter;21(1):1-19. doi: 10.1162/ARTL_a_00143.  
Andrew Adamatzky, Towards fungal computer, Interface Focus, The Royal Society Publishing, 2018. http://doi.org/10.1098/rsfs.2018.0029  
Yokomori, T., Okubo, F. Theory of reaction automata: a survey. J Membr Comput 3, 63–85 2021. https://doi.org/10.1007/s41965-021-00070-6  
