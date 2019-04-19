"""
#matplotlib-2d之Watermark image
#使用PNG作为格式(Use a PNG file as a watermark)

#OUT:
   loading /home/tcaswell/.virtualenvs/bleeding/lib/python3.7/site-packages/matplotlib/mpl-data/sample_data/logo2.png
```python
"""
from __future__ import print_function
import numpy as np
import matplotlib.cbook as cbook
import matplotlib.image as image
import matplotlib.pyplot as plt

# Fixing random state for reproducibility
np.random.seed(19680801)


datafile = cbook.get_sample_data('logo2.png', asfileobj=False)
print('loading %s' % datafile)
im = image.imread(datafile)
im[:, :, -1] = 0.5  # set the alpha channel

fig, ax = plt.subplots()

ax.plot(np.random.rand(20), '-o', ms=20, lw=2, alpha=0.7, mfc='orange')
ax.grid()
fig.figimage(im, 10, 10, zorder=3)

plt.show()