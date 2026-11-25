# Expériences complémentaires du papier (à lancer le 24/11 au soir)

| Phase | TODO du papier | Évals (5 seeds) |
|---|---|---|
| `setup` | applique `madevo_dyn_modes.patch` + écrit les sources `*_step8k.yaml` | — |
| `bench` | latence sur GPU libre (§ Computational cost) | 1 passe, **seul sur la machine** |
| `dynba` | (a) masque aussi sur ω dans la BA à l'inférence | 10 (EVIMO2) |
| `frozen` | (b) couplés au step 8000, DEVO encore gelé | 10 EVIMO2 + 25 cross |
| `delete` | baseline « suppression amont » (Pellerito et al.) | 5 EVIMO2 + 25 cross |
| `gamma` | température γ ∈ {2, 4} contre l'excès de masque sur EDS | 60 (EVIMO2 + cross) |
| `viz` | (c) score maps pour les figures qualitatives | 2 (seed 1) |

Pourquoi le step **8000** et pas 10000 : `coupled_step10000.pt` est écrit après la première
mise à jour de DEVO (le dégel a lieu au début du step 10000). Au step 8000, DEVO vaut
exactement les poids pré-entraînés.

## Sur le serveur

```bash
# depuis le portable
scp -r ~/arthur_ipal/paper/experiments <serveur>:arthur_ipal/paper_experiments

# sur le serveur, dans tmux
conda activate madevo
cd ~/arthur_ipal/paper_experiments
./run_paper_extras.sh setup                          # une fois par clone de MADEVO
./run_paper_extras.sh --list --gpus 0,1 all          # voir la file
./run_paper_extras.sh --dry-run --gpus 0 dynba       # vérifier checkpoints et configs
./run_paper_extras.sh --gpus 0,1 dynba frozen viz    # machine 1
./run_paper_extras.sh --gpus 0,1 delete gamma        # machine 2
./run_paper_extras.sh bench                          # machine libre, rien d'autre ne tourne
```

`MADEVO=` si le repo n'est pas dans `~/arthur_ipal/MADEVO`, `FLEET=` si `fleet/` n'est pas à
côté (splits VECtor `n8/split_all.txt` et TUM-VIE `n6/split_m.txt` de la campagne). Relancer
une commande est sans risque : les évals terminées (`DONE`) sont sautées. EDS est le plus
long ; les phases mettent EDS en dernier, sauf `gamma`, dont EDS est la cible.

## Le patch

`madevo_dyn_modes.patch` (vérifié avec `git apply --check` sur le code de la sauvegarde
finale, non testé sur GPU) ajoute à `devo/config.py` quatre réglages **inertes par défaut**
(les chiffres du papier ne bougent pas) :

| Réglage | Effet |
|---|---|
| `DYN_BA_WEIGHT` | ω ← ω·(1 − p) au centre de chaque patch dans `fastba.BA`, comme à l'entraînement couplé |
| `DYN_DELETE`, `DYN_DELETE_THRESH` | voxels mis à zéro où p > 0,5, score map intacte |
| `DYN_GAMMA` | p ← p^γ avant tout usage |

Ils passent par `--set +devo.cfg_overrides.<NOM>=<valeur>`, que `evals/eval_table.py`
transmet à la config DEVO. Le patch touche `devo/devo.py`, qui contient déjà nos crochets
`dyn_score`. À commiter après la campagne si les résultats entrent dans le papier.

## Rapatrier

`evals_out/*/*/2026-11-25_*/` et `logs/paper_extras/`. L'agrégation se fait comme pour le
papier : `tools/aggregate_seeds.py` (EVIMO2) et `fleet/tools/agg_cross.py <ds> --since 2026-11-25_0000`.
