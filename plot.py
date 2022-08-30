import matplotlib.pyplot as plt
import numpy as np
from functools import reduce

def generate_fake_data():
    return -(np.sin(X) * np.cos(Y) + np.cos(X)), -(-np.cos(X) * np.sin(Y) + np.sin(Y))


x = np.arange(0, 2 * np.pi + 2 * np.pi /20, 2 * np.pi /20)
y = np.arange(0, 2 * np.pi + 2 * np.pi /20, 2 * np.pi /20)

X, Y = np.meshgrid(x, y)
u, v = generate_fake_data()


conv = reduce(np.add,np.gradient(u)) + reduce(np.add,np.gradient(v))
#conv[conv>=0] = np.nan
#p = plt.imshow(conv,extent =[0, 2 * np.pi, 0, 2 * np.pi])

fig, ax = plt.subplots(figsize=(7, 7))
#plt.imshow(conv)
p = plt.imshow(conv,extent =[0, 2 * np.pi, 0, 2 * np.pi])
#plt.colorbar(p)


# quiveropts = dict(headlength=0, headaxislength=0, pivot='middle', units='xy')
# ax.quiver(X, Y, u, v, **quiveropts)
ax.quiver(X, Y, u, v)

# ax.xaxis.set_ticks([])
# ax.yaxis.set_ticks([])
plt.axis([0, 2 * np.pi, 0, 2 * np.pi])
#ax.set_aspect('equal')
# ax.axis("off")

#plt.colorbar(c)

#plt.gca().set_axis_off()
#plt.subplots_adjust(top=1, bottom=0, right=1, left=0,hspace=0, wspace=0)
#plt.margins(0, 0)
#plt.gca().xaxis.set_major_locator(plt.NullLocator())
#plt.gca().yaxis.set_major_locator(plt.NullLocator())
#plt.tight_layout()
plt.show()
plt.savefig("mock_data.png", bbox_inches='tight', pad_inches=0)

absmin = np.unravel_index(np.nanargmin(conv), conv.shape)
print(absmin, conv[absmin])