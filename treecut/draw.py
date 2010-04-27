"""
Draws vertically presented hierarchical tree, along with the associated values
"""

import itertools

import numpy as np
import matplotlib
matplotlib.use("Agg")
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt

# latex fonts
_ = lambda x: r"$\rm{%s}$" % (x.replace(" ", r"\ ")) 
label_style = dict(rotation=90, ha="center", va="center", color="w",
        bbox=dict(boxstyle="round", fc="k"))

def clear_ax(ax):
    ax.set_xlim(0,1)
    ax.set_ylim(0,1)
    ax.set_axis_off()


class Dendrogram(object):

    def __init__(self, ext_tree, cutoff=.05, **kwargs):

        self.tree = ext_tree
        self.accessions = []
        self.values = self.tree.values
        self.xinterval = 0

        self.figure = fig = plt.figure(1, (8,8))
        root = fig.add_axes([0,0,1,1])
        tree_ax = fig.add_axes([0,.5,1,.5])
        value_ax = fig.add_axes([0,.3,1,.2])

        self.draw_tree(tree_ax)
        self.draw_values(value_ax)
        self.draw_modules(value_ax, cutoff=cutoff)

        for a in (tree_ax, value_ax, root): 
            clear_ax(a)


    def draw_tree(self, ax):

        t = self.tree.node
        farthest, max_dist = t.get_farthest_node()

        margin = .1
        xstart = margin
        ystart = 1 - margin
        canvas = 1 - 2 * margin
        # scale the tree so that the height is about .9
        scale = canvas / max_dist

        num_leaves = len(t.get_leaf_names())
        self.xinterval = xinterval = canvas / (num_leaves - 1)

        coords = {}
        i = itertools.count()
        for n in t.traverse("postorder"):
            dist = n.get_distance(t)
            yy = ystart - scale * dist

            if n.is_leaf():
                xx = xstart + i.next() * xinterval
                self.accessions.append(n.name)
            else:
                children = [coords[x] for x in n.get_children()]
                children_x, children_y = zip(*children)
                min_x, max_x = min(children_x), max(children_x)
                # plot the horizontal bar
                ax.plot((min_x, max_x), (yy, yy), "k-")
                # plot the vertical bar
                for cx, cy in children:
                    ax.plot((cx, cx), (cy, yy), "k-")
                xx = np.mean(children_x)

            coords[n] = (xx, yy)

        ax.text(xstart*.5, .5, "Phylogeny", label_style)

    
    def draw_values(self, ax):
        
        margin = .1
        xstart = margin
        ystart = .4 
        xinterval = self.xinterval

        accession_values = np.array([self.values[x] for x in self.accessions], dtype="f")
        min_val, max_val = accession_values.min(), accession_values.max()
        # draw the gauge to the right showing the data range
        gauge, tip = 1-margin*.7, .005
        ax.plot((gauge, gauge), (ystart, 1), "b-")
        ax.plot((gauge-tip, gauge+tip), (ystart, ystart), "b-")
        ax.plot((gauge-tip, gauge+tip), (1, 1), "b-")
        ax.text(gauge+tip, ystart, _("%.1f" % min_val), color="b")
        ax.text(gauge+tip, 1, _("%.1f" % max_val), va="top", color="b")

        scale = (1 - ystart) / (max_val - min_val)
        accession_values -= min_val 
        accession_values *= scale

        for i, a in enumerate(accession_values):
            xx = xstart + i * xinterval
            ax.plot((xx, xx), (ystart, ystart + a), "k-")

        ax.text(xstart*.5, .6, "Values", label_style) 

    
    def draw_modules(self, ax, cutoff=.05):

        margin = .1
        xstart = margin
        ystart = .4
        xinterval = self.xinterval

        modules = self.tree.get_modules(cutoff=cutoff)
        lmean = np.mean

        for e in modules:
            mcolor = "g" if lmean(e.a) < lmean(e.b) else "r"
            accs = e.get_leaf_names()
            xx = xstart + min(self.accessions.index(x) for x in accs) * xinterval
            width = (len(accs) - 1) * xinterval
            ax.add_patch(Rectangle((xx, ystart), width, 1-ystart, fc=mcolor, alpha=.3, lw=0))
            ax.text(xx+width*.5, ystart-.05, r"$%.1f$" % lmean(e.a), color=mcolor, ha="center", va="top")
            ax.text(xx+width*.5, ystart-.13, r"$(P=%.1g)$" % e.val, color=mcolor, ha="center", va="top")


    def savefig(self, image_name, **kwargs):

        self.figure.savefig(image_name, **kwargs)