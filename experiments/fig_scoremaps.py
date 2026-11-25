import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
plt.rcParams.update({"font.family":"STIXGeneral","mathtext.fontset":"stix","font.size":7,"pdf.fonttype":42})
cm=LinearSegmentedColormap.from_list("o",["#ffffff","#fff4ec","#c2410c"])
b="evimo2/evimo2_pw3/2026-11-25_6000/seed1/dumps/"; s="scene14_dyn_test_04_000000.npz"
O,V,M=[np.load(b+k+"/"+s) for k in ("oracle","vanilla","m1")]
i=22; gt=O["scores"][i]>127
E=np.load("eds/evimo2_pw3/2026-11-25_6050/seed1/dumps/m1/11_all_characters.npz"); j=2539
panels=[(O["scores"][i]/255,V["patch_xy"][i],gt,"(a) EVIMO2: GT mask, DEVO patches"),
        (M["scores"][i]/255,M["patch_xy"][i],gt,"(b) EVIMO2: M1 $p$, M1 patches"),
        (E["scores"][j]/255,E["patch_xy"][j],None,"(c) EDS (static scene): M1 $p$")]
fig,ax=plt.subplots(1,3,figsize=(7.0,1.9))
for a,(img,xy,g,t) in zip(ax,panels):
    a.imshow(img,cmap=cm,vmin=0,vmax=1,interpolation="nearest")
    xy=xy.astype(float); xi=np.clip(np.round(xy[:,0]).astype(int),0,159); yi=np.clip(np.round(xy[:,1]).astype(int),0,119)
    dyn=g[yi,xi] if g is not None else np.zeros(len(xy),bool)
    a.scatter(xy[~dyn,0],xy[~dyn,1],s=5,marker="s",c="#1f2937",linewidths=0)
    a.scatter(xy[dyn,0],xy[dyn,1],s=12,marker="s",facecolors="none",edgecolors="#1f2937",linewidths=0.8)
    if g is not None: a.contour(g.astype(float),levels=[0.5],colors="#475569",linewidths=0.5,linestyles="--")
    a.set_title(t,fontsize=7,pad=3); a.set_xticks([]); a.set_yticks([])
    for sp in a.spines.values(): sp.set_color("#475569"); sp.set_linewidth(0.5)
fig.tight_layout(pad=0.3,w_pad=0.6)
fig.savefig("/home/arthur/arthur_ipal/paper/figs/scoremaps.pdf",bbox_inches="tight",pad_inches=0.02); 
print((V["patch_xy"][i]).shape)
