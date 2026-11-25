# Provenance des chiffres du papier

Source unique : `~/madevo_final_2411/` (campagne finale, sauvegarde du 24/11/2026).

| Dans le papier | Source |
|---|---|
| Table 1 (DEVO pré-entraîné), Table 2 (DEVO affiné), ablation `all` | `RESULTATS_PAPIER.md` §1 (`tools/aggregate_seeds.py`) ; runs `evals_out/evimo2*/2026-11-11_1930`, `…/2026-11-14_0000`, `evimo2/2026-11-15_0000`, `none/2026-11-14_0000` |
| Table 3, Figure 2 (cross-dataset) | `RESULTATS_PAPIER.md` §2 et `RESULTATS_PAPIER_annexe.md` (`fleet/tools/agg_cross.py --since 2026-11-15_0000`). Ratios de la figure : M1 pw3 / vanilla et DEVO-ft / vanilla |
| Table 5 (coût), 1,0 M paramètres | `paper/experiments/bench/bench_venturi_*.log` (25/11, P = 96 ; remplace `docs/compute_cost.md`, compté à ~5 400 arêtes) |
| Table 5 (par séquence) et « 4 séquences = 89 % de l'erreur » | moyenne sur les 5 seeds des `per_scene.csv` : `evimo2/2026-11-11_1930` (vanilla, oracle), `evimo2_pw3/2026-11-11_1930` (M1), `none/2026-11-14_0000` (DEVO-ft), `evimo2_pw3/2026-11-14_0000` (M2, M3). Les moyennes retombent sur les Tables 1-2 |
| Définition du masque (1 cm, 0,2 s, 1,9 % de positifs, 66 % de frames vides, bruit 0,66 cm, 61 % en `all`) | `arthur_ipal/MADEVO/docs/mask_motion.md` |
| Hyperparamètres (100 epochs, lr, 40k/10k, k = 3, β = 0,5, cible 0,02, P = 96) | `configs/ms/v4_evimo2.yaml`, `configs/coupled/_base_evimo2.yaml`, `config/eval_evimo.yaml` |
| MS flagge 11-35 % de l'image sur EDS contre 1-9 % sur RPG/MVSEC | `RESULTATS_PAPIER.md` §2 (`tools/ms_score_stats.py`) |
| Bugs corrigés (§ Reproducibility) | `arthur_ipal/INTEGRITY_CHECK.md` |
| 41 % de gain de l'oracle au stage | `CLAUDE.md` (chiffre du stage, masque `all`, mono-seed) |

## Vérifié dans le code (à garder en tête en relisant)

- À l'inférence, le masque n'atténue **que la score map** (`devo/devo.py` → `patchify(dyn_score=…)`) ;
  la BA CUDA (`fastba.BA`) ne le reçoit pas. L'atténuation de ω n'existe qu'à l'entraînement couplé
  (`devo/enet.py`, `devo/ba.py`, `dyn_weights`). Le papier le dit (§ III-C, TODO associé).
- `best_iou.pt` est choisi sur le split d'éval : biais assumé, compensé par les lignes `last.pt` de la Table 1.
- M2/M3 `scratch` et `large` utilisent `pos_weight` 7 (configs qui étendent `_base_evimo2.yaml`).

## Ajouts du 24/11 (après-midi)

| Dans le papier | Source |
|---|---|
| IoU de validation du MS (0,36 ± 0,02 pw3, 0,35 pw7, 0,26 large, 0,93 `all`) | `tools/ms_best_iou.py` sur `runs/v4*_evimo2*/2026-11-11_1141/seed*` (env `madevo`), moyenne ± écart-type des 5 seeds |
| Tests de Wilcoxon (oracle p = 0,051, M1 pw3 p = 0,24, pw7 p = 0,77 ; M2-large vs DEVO-ft p = 0,31, M2 pw3 p = 0,44, M3-large p = 0,58) | `scipy.stats.wilcoxon` sur les 40 paires (seed, séquence) des `per_scene.csv` (mêmes dossiers que la Table 5, plus `evimo2_large/2026-11-14_0000`). Seed i de la méthode apparié à la seed i de la référence |
| Annexe B, table des définitions du masque | `docs/mask_motion.md` (split train, dilatation 3 px) |
| Annexe C, figure qualitative (`figs/qual_1-4.jpg`) | images de `arthur_ipal/videos/MS_pw3_s1_8scenes_eval.mp4` (M1 pw3, seed 1, `best_iou.pt`, seuil 0,5) aux instants 41,5 s, 4,5 s, 32 s et 53,5 s (`ffmpeg fps=2`, images 083, 009, 064, 107), bandeau de titre retiré |
| Annexe D, tables cross-dataset par séquence | `RESULTATS_PAPIER_annexe.md`, colonnes vanilla, M1 pw3/pw7/`all`, DEVO-ft, M2 pw3, M3 pw3 |
| Related Work, références 2025-2026 | métadonnées vérifiées sur les pages arXiv (2607.07374, 2506.06596, 2504.18447, 2609.30947, 2512.06868, 2401.01887) |

## Expériences complémentaires du 25/11 (§ V-D « Alternative injections », Table 4, Figure 4, Discussion)

Runs de `paper/experiments/run_paper_extras.sh`, rapatriés dans `~/arthur_ipal/evals_out/` ;
résumé serveur (moyennes simples) dans `~/arthur_ipal/paper_experiments/RESULTATS_EXTRAS.md`.
Le lancement sur la flotte a renuméroté les LAUNCH_ID : `2026-11-25_PDMM`, P = phase
(1 dynba, 2 frozen8k, 3 delete, 4 gamma2, 5 gamma4, 6 viz), D = dataset (0 evimo2, 1 rpg,
2 mvsec, 3 tumvie, 4 vector, 5 eds), MM = méthode (10 oracle, 20 m1, 30 m2, 40 m3 ; 00/50 viz).
Mêmes checkpoints que la campagne (manifests vérifiés).

| Dans le papier | Source / méthode |
|---|---|
| Table 4, colonne EVIMO2, et tous les Wilcoxon de § V-D et de la Discussion | `per_scene.csv` des `evals_out/evimo2/*/2026-11-25_*`, même calcul que la Table 1 ; Wilcoxon sur les 40 paires (seed, séquence) contre la ligne de référence de la campagne (`2026-11-11_1930`, `2026-11-14_0000`) |
| Table 4, colonne EDS | `fleet/tools/agg_cross.py eds` (racine locale), un LAUNCH_ID à la fois ; la référence (33,8 / 31,4) est reproduite à l'identique sur `~/madevo_final_2411/evals_out` |
| Coupled + ω à l'inférence « within 0.06 cm » | dynba M2/M3 : 1,21/1,24 (w+3), 1,39/1,42 (w+7) contre 1,19/1,26 et 1,39/1,48 |
| Frozen step 8k : RPG 1,0 cm | `RESULTATS_EXTRAS.md` (0,99 et 0,96, moyennes simples, 5 seeds) |
| 5,4 % / 2,7 % / 0,7 % de patchs sur cellules mobiles | phase viz (`2026-11-25_6000`, seed 1, 1 essai) : masque oracle échantillonné aux `patch_xy` de chaque méthode, toutes frames des 8 séquences |
| Figure 4 | `paper/experiments/fig_scoremaps.py` : frame 22 de `scene14_dyn_test_04` (choisie : 15 patchs DEVO sur l'objet contre 1 pour M1), frame 2539 de EDS `11_all_characters` (frame médiane, 21 % des cellules à p > 0,5) |

Table 4, colonnes RPG / MVSEC / VECtor / TUM-VIE (et EDS, identique au calcul local) :
`~/arthur_ipal/extras_2511/RESULTATS_EXTRAS.md` (25/11 22:24, 200/202 évals), section
« Cross-dataset au format du papier » (`cross_table.py` = `agg_cross.py` par LAUNCH_ID ; TUM-VIE
sur les 5 scènes mocap). Seul VECtor γ=4 n'a que 4 seeds (marqué † dans la table).
Latences (§ Computational cost) : phase `bench` lancée le 25/11 à 09:24 sur venturi, GPU libre (0 %, 138 Mo), logs dans `paper/experiments/bench/` (MS : `bench_venturi_ms_gpu.log` et `_ms_cpu4.log` ; DEVO : `_devo_gpu.log`, colonne ms/frame). « 11 % » = 2,0 / 18 ms à 640×480.
Le hostname des runs (`*.polytechnique.fr`) confirme l'attribution des remerciements.
