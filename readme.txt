Installation

1. Install [PyBox2D](https://github.com/pybox2d/pybox2d) and [pygame](https://www.pygame.org):
  conda create -n pybox2d -c conda-forge python=3.6 pybox2d
  pip install pygame

2. Install other dependencies: 
  pip install numpy scipy matplotlib

3. Download the python code in this GitHub

Run Simulated Autopoiesis (auto.py)

conda activate pybox2d
python -m auto --backend=pygame


Plot figures (produces fig1.png, fig2.png, fig3.png)

python plot.py
python phase-plot.py

