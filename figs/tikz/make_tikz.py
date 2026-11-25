"""Génère figs/tikz/arch.tex et figs/tikz/ratio.tex (TikZ pur, coordonnées en cm)."""
import math, os
H = os.path.dirname(os.path.abspath(__file__))
f = lambda x: f"{x:.3f}".rstrip("0").rstrip(".")

def heat(x0, y0, nx, ny, s, fn, c):
    out = []
    for i in range(nx):
        for j in range(ny):
            v = min(max(fn(i, j), 0), 1)
            out.append(f"\\fill[{c}!{round(v*100)}!white, draw=white, line width=0.25pt] ({f(x0+i*s)},{f(y0+j*s)}) rectangle +({s},{s});")
    out.append(f"\\draw[slate, line width=0.5pt] ({f(x0)},{f(y0)}) rectangle +({f(nx*s)},{f(ny*s)});")
    return out
blob = lambda i, j: math.exp(-((i-4.6)**2 + (j-2.2)**2) / 1.6)
texture = lambda i, j: 0.45 + 0.4*math.sin(i*1.7 + j*2.3)*math.cos(i*0.9 - j*1.3)

L = [r"\begin{tikzpicture}[x=1cm, y=1cm, font=\fontsize{6.5}{7.5}\selectfont,",
     r"  arr/.style={-{Stealth[length=1.6mm]}, line width=0.7pt},",
     r"  box/.style={rounded corners=0.8mm, line width=0.7pt, fill=white, align=center}]"]
A = L.append
# panels
A(r"\fill[slatelight, rounded corners=1.5mm] (-0.25,-1.3) rectangle (17.25,1.25);")
A(r"\node[anchor=north west, text=slate, font=\fontsize{6}{7}\selectfont] at (-0.1,1.15) {\textsc{DEVO --- pretrained weights, unchanged}};")
A(r"\fill[ourslight, rounded corners=1.5mm] (1.55,-4.15) rectangle (13.55,-1.6);")
A(r"\node[anchor=south east, text=ours, font=\fontsize{6}{7}\selectfont] at (13.4,-4.05) {\textsc{Ours --- motion-segmentation prior}};")
# events
A(r"\draw[slate, line width=0.5pt, fill=white] (0,-0.6) rectangle (1.2,0.6);")
ev = [(0.15,-0.35),(0.42,0.28),(0.7,-0.1),(0.95,0.4),(0.3,0.05),(0.85,-0.4),(0.55,0.45),(1.05,0.05),(0.2,0.42),(0.65,-0.45),(0.4,-0.2),(0.98,-0.22)]
for k,(x,y) in enumerate(ev):
    A(f"\\draw[ink, line width=0.4pt, fill={'ink' if k%2==0 else 'white'}] ({x},{y}) circle (0.035);")
A(r"\node[anchor=north] at (0.6,-0.68) {Events};")
A(r"\draw[arr, slate] (1.3,0) -- (1.85,0);")
for b in range(5):
    o = (4-b)*0.11
    A(f"\\draw[slate, line width=0.5pt, fill=white] ({f(2.0+o)},{f(-0.55+o)}) rectangle +(0.85,0.85);")
A(r"\node[anchor=north] at (2.5,-0.68) {Voxel grid};")
A(r"\draw[arr, slate] (3.45,0) -- (3.9,0);")
A(r"\draw[box, draw=slate] (4.0,-0.45) rectangle (5.15,0.45); \node[align=center] at (4.575,0) {Patch\\scorer};")
A(r"\draw[arr, slate] (5.15,0) -- (5.55,0);")
L += heat(5.65, -0.5, 7, 5, 0.2, texture, "slate")
A(r"\node[anchor=south] at (6.35,0.55) {score map $S$};")
A(r"\draw[arr, slate] (7.05,0) -- (7.55,0);")
A(r"\draw[ours, line width=0.8pt, fill=white] (7.8,0) circle (0.2); \node[text=ours, font=\fontsize{8}{8}\selectfont] at (7.8,0) {$\odot$};")
A(r"\draw[arr, slate] (8.0,0) -- (8.45,0);")
A(r"\draw[slate, line width=0.5pt, fill=white] (8.55,-0.5) rectangle +(1.4,1.0);")
A(r"\draw[ours, line width=0.5pt, densely dotted, fill=ourslight] (9.57,0.04) ellipse (0.34 and 0.27);")
for i,j in [(0.5,0.6),(1.4,3.6),(2.3,1.5),(0.7,4.1),(3.2,4.2),(2.9,0.4),(1.6,2.4),(6.2,0.4),(3.8,2.8),(6.3,4.2),(4.4,0.5)]:
    A(f"\\fill[ink] ({f(8.55+0.2*i-0.06)},{f(-0.5+0.2*j-0.06)}) rectangle +(0.12,0.12);")
A(r"\node[anchor=south] at (9.25,0.55) {top-$P$ patches};")
A(r"\draw[arr, slate] (9.95,0) -- (10.35,0);")
A(r"\draw[box, draw=slate] (10.45,-0.45) rectangle (11.75,0.45); \node[align=center] at (11.1,0) {Update\\operator};")
A(r"\draw[slate, line width=0.6pt, -{Stealth[length=1.4mm]}] (10.85,0.45) arc[start angle=180, end angle=0, radius=0.25];")
A(r"\node[anchor=north] at (11.1,-0.52) {$\delta_{kj}, \omega_{kj}$};")
A(r"\draw[arr, slate] (11.75,0) -- (12.25,0);")
A(r"\draw[ours, line width=0.8pt, dashed, fill=white] (12.45,0) circle (0.2); \node[text=ours, font=\fontsize{8}{8}\selectfont] at (12.45,0) {$\odot$};")
A(r"\draw[arr, slate] (12.65,0) -- (13.05,0);")
A(r"\draw[box, draw=slate] (13.05,-0.45) rectangle (14.65,0.45); \node[align=center] at (13.85,0) {Differentiable\\BA};")
A(r"\draw[arr, slate] (14.65,0) -- (15.05,0);")
A(r"\draw[ink, line width=0.9pt] (15.2,-0.4) .. controls (15.8,0.6) and (16.3,-0.6) .. (17.0,0.35);")
for x,y in [(15.2,-0.4),(15.95,0.02),(16.6,-0.05),(17.0,0.35)]:
    A(f"\\draw[ink, line width=0.4pt, fill=white] ({x},{y}) -- ({f(x-0.12)},{f(y+0.2)}) -- ({f(x+0.12)},{f(y+0.2)}) -- cycle;")
A(r"\node[anchor=north] at (16.1,-0.68) {poses $\mathbf{T}$};")
# ours row
A(r"\draw[ours, line width=0.7pt, fill=white] (2.6,-3.25) -- (2.6,-1.95) -- (3.5,-2.3) -- (3.5,-2.9) -- cycle; \node at (3.05,-2.6) {enc};")
A(r"\draw[box, draw=ours] (3.7,-2.9) rectangle (4.95,-2.3); \node at (4.325,-2.6) {ConvLSTM};")
A(r"\draw[ours, line width=0.6pt, -{Stealth[length=1.4mm]}] (4.1,-2.3) arc[start angle=180, end angle=0, radius=0.2];")
A(r"\draw[ours, line width=0.7pt, fill=white] (5.15,-2.9) -- (5.15,-2.3) -- (6.05,-2.05) -- (6.05,-3.15) -- cycle; \node at (5.6,-2.6) {dec};")
A(r"\draw[arr, ours] (3.5,-2.6) -- (3.7,-2.6); \draw[arr, ours] (4.95,-2.6) -- (5.15,-2.6);")
A(r"\node[anchor=north, align=center] at (4.6,-3.28) {$f_\theta$: causal ConvLSTM U-Net\\1.0\,M params};")
A(r"\draw[arr, ours] (3.15,-0.65) -- (3.15,-2.1);")
A(r"\draw[arr, ours] (6.05,-2.6) -- (7.1,-2.6);")
L += heat(7.1, -3.1, 7, 5, 0.2, blob, "ours")
A(r"\node[anchor=north] at (7.8,-3.15) {dynamic prob.\ $p$};")
A(r"\draw[arr, ours] (7.8,-2.05) -- (7.8,-0.22); \node[anchor=east, text=ours] at (7.72,-1.45) {$1-p$};")
A(r"\draw[arr, ours, dashed] (8.5,-2.6) -- (12.45,-2.6) -- (12.45,-0.22); \node[anchor=east, text=ours] at (12.37,-1.45) {$1-p$ (training)};")
# supervision
A(r"\draw[slate, line width=0.5pt, fill=white] (0,-3.1) rectangle +(1.0,0.75); \fill[ink] (0.62,-2.73) ellipse (0.2 and 0.15);")
A(r"\node[anchor=north, align=center] at (0.5,-3.18) {GT mask\\(M1, M2)};")
A(r"\draw[slate, line width=0.6pt, dashed, -{Stealth[length=1.4mm]}] (1.0,-2.72) -- (2.55,-2.72);")
A(r"\draw[ours, line width=0.6pt, dashed, -{Stealth[length=1.4mm]}] (13.85,-0.45) -- (13.85,-4.5) -- (2.8,-4.5) -- (2.8,-3.2);")
A(r"\node[anchor=north, text=ours] at (9.0,-4.68) {M2, M3: pose loss through Eq.~\eqref{eq:inject} \quad$|$\quad M3: mask target $\mathbb{1}[r_k > \mathrm{med}(r) + 3\,\mathrm{MAD}(r)]$ from BA residuals, no labels};")
A(r"\end{tikzpicture}")
open(os.path.join(H, "arch.tex"), "w").write("\n".join(L) + "\n")

# ratio chart: ATE(method) / ATE(DEVO), log axis 0.5x .. 12x
data = [("RPG",1.00,2.70),("MVSEC",1.01,3.58),("EDS",0.93,3.76),("VECtor",0.92,7.53),("TUM-VIE",1.25,9.58)]
W, lo, hi, rh = 5.6, math.log(0.5), math.log(12.0), 0.55
x = lambda r: W*(math.log(r)-lo)/(hi-lo); n = len(data)
R = [r"\begin{tikzpicture}[x=1cm, y=1cm, font=\fontsize{6.5}{7.5}\selectfont]"]
for r,l in [(0.5,"0.5$\\times$"),(1,"1$\\times$"),(2,"2$\\times$"),(5,"5$\\times$"),(10,"10$\\times$")]:
    st = "ink, line width=0.6pt" if r == 1 else "black!16, line width=0.4pt"
    R.append(f"\\draw[{st}] ({f(x(r))},-0.1) -- ({f(x(r))},{f(n*rh)});")
    R.append(f"\\node[anchor=north, text=slate, font=\\fontsize{{5.5}}{{6.5}}\\selectfont] at ({f(x(r))},-0.15) {{{l}}};")
for k,(name,m1,ft) in enumerate(data):
    y = (n-1-k)*rh + rh/2
    R.append(f"\\node[anchor=east] at (-0.1,{f(y)}) {{{name}}};")
    R.append(f"\\draw[black!14, line width=1.2pt] ({f(x(m1))},{f(y)}) -- ({f(x(ft))},{f(y)});")
    R.append(f"\\fill[slate] ({f(x(ft))},{f(y)}) circle (0.075); \\fill[ours] ({f(x(m1))},{f(y)}) circle (0.075);")
    R.append(f"\\node[anchor=west, text=slate, font=\\fontsize{{5.5}}{{6.5}}\\selectfont] at ({f(x(ft)+0.13)},{f(y)}) {{{ft:.1f}$\\times$}};")
R.append(f"\\node[anchor=north, text=slate, font=\\fontsize{{5.5}}{{6.5}}\\selectfont] at ({f(x(1))},-0.5) {{ATE relative to pretrained DEVO (log scale)}};")
ly = n*rh + 0.2
R.append(f"\\fill[ours] (0.1,{f(ly)}) circle (0.06); \\node[anchor=west, font=\\fontsize{{6}}{{7}}\\selectfont] at (0.22,{f(ly)}) {{M1, plug-in ($w_+ = 3$)}};")
R.append(f"\\fill[slate] (2.6,{f(ly)}) circle (0.06); \\node[anchor=west, font=\\fontsize{{6}}{{7}}\\selectfont] at (2.72,{f(ly)}) {{DEVO fine-tuned on EVIMO2}};")
R.append(r"\end{tikzpicture}")
open(os.path.join(H, "ratio.tex"), "w").write("\n".join(R) + "\n")
