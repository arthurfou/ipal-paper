# MADEVO — brouillon du papier (LaTeX, IEEEtran)

```bash
pdflatex main && bibtex main && pdflatex main && pdflatex main   # → main.pdf
```

| Fichier | Rôle |
|---|---|
| `main.tex` | le texte (anglais), tables et annexe (« Supplementary Material ») |
| `IEEEtran.cls`, `IEEEtran.bst` | classe et style biblio IEEE (CTAN, v1.8b / 1.14), absents de la TeX Live locale ; à remplacer par le gabarit de la conférence visée |
| `figs/tikz/make_tikz.py` | génère `figs/tikz/arch.tex` (schéma d'architecture) et `figs/tikz/ratio.tex` (graphique cross-dataset), en TikZ. Modifier le script, pas les `.tex` générés |
| `figs/scoremaps.pdf` | figure des patchs (annexe), produite par `experiments/fig_scoremaps.py` (à lancer depuis `~/arthur_ipal/evals_out`) |
| `figs/qual_*.jpg` | figure qualitative (annexe), images de `videos/MS_pw3_s1_8scenes_eval.mp4` |
| `refs.bib` | copie de `archive/reports/references.bib` + RPG stéréo, VECtor, TUM-VIE et la biblio 2025-2026 |
| `NUMBERS.md` | d'où vient chaque chiffre |
| `experiments/` | script et patch des runs complémentaires du 25/11, logs du bench |

Pour une soumission anonyme : retirer le bloc `\author{...}`, l'URL du code et les
remerciements de `main.tex`.

Remplace le brouillon LaTeX de juillet (`archive/reports/paper_arthur/main.tex`), dont la
thèse (« l'auto-supervisé bat le GT ») et tous les chiffres sont périmés.
