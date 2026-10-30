"""Native iLED plot, using entirely synthetic demonstration data."""
import os
from pathlib import Path
import sys
import sysconfig

os.environ.setdefault('MPLBACKEND', 'Agg')
os.environ.setdefault('MPLCONFIGDIR', '/tmp/iled-matplotlib')
sys.path.insert(0, str(Path(sysconfig.get_paths()['platlib']) / 'CDLE'))
from CDLE_plot import plot_transition_level_figure

os.chdir(Path(__file__).resolve().parent)
Path('cdle').mkdir(exist_ok=True)
# Invented values: not calculated GaN energies or material predictions.
levels = {'v_Ga': [('0/-1', 0.8), ('-1/-2', 1.7)], 'v_N': [('+1/0', 2.3)]}
plot_transition_level_figure(levels, band_gap=3.4)
print('Saved cdle/transition_level.{png,pdf,svg}; all input values are synthetic.')
