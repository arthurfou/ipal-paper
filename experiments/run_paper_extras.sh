#!/usr/bin/env bash
# Expériences complémentaires du papier (TODO de paper/main.typ), à lancer sur un serveur GPU.
#
# Usage (depuis n'importe où, env conda `madevo` activé, idéalement dans tmux) :
#   ./run_paper_extras.sh [--gpus 0,1] [--seeds 1-5] [--dry-run | --list] <phase>...
#   --list     affiche la file d'évals sans rien lancer ni vérifier
#   --dry-run  résout chaque éval (configs, checkpoints, manifest) sans rien évaluer
#
# Phases (une machine peut prendre une ou plusieurs phases ; relancer est sans risque,
# les évals déjà terminées (DONE) sont sautées) :
#   setup    applique madevo_dyn_modes.patch au repo et écrit les préréglages `sources`
#            *_step8k.yaml. À faire une fois par clone, avant toute autre phase.
#   bench    latence MS et DEVO, GPU et CPU. À lancer SEUL sur une machine libre.
#   dynba    (a) masque aussi appliqué à ω dans la BA à l'inférence : oracle, M1, M2, M3 (EVIMO2)
#   frozen   (b) couplés au step 8000 (DEVO encore gelé, seul f_θ a appris via la pose loss) :
#            M2, M3 sur EVIMO2 (pw3 et pw7) + cross-dataset (pw3)
#   delete   baseline « suppression amont » (type Pellerito et al.) : events effacés où p > 0,5,
#            score map intacte : oracle, M1 (EVIMO2) + M1 cross-dataset
#   gamma    température p ← p^γ, γ ∈ {2, 4} : M1 sur EVIMO2 + cross-dataset (cible : EDS)
#   viz      (c) dumps des score maps / patches pour les figures, seed 1, 1 essai :
#            EVIMO2 (vanilla, oracle, M1) et EDS (vanilla, M1)
#   all      setup, bench, puis toutes les autres phases
#
# Sorties : evals_out/<dataset>/<sources>/<LAUNCH_ID>/seed<N>/ comme d'habitude, avec un
# LAUNCH_ID par expérience (2026-11-25_dynba, _frozen8k, _delete, _gamma2, _gamma4, _viz) ;
# bench dans logs/paper_extras/. Journal de chaque job : logs/paper_extras/<job>.log.
#
# Variables : MADEVO (défaut ~/arthur_ipal/MADEVO), FLEET (défaut $MADEVO/../fleet, pour les
# splits VECtor et TUM-VIE de la campagne cross-dataset).
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MADEVO="${MADEVO:-$HOME/arthur_ipal/MADEVO}"
FLEET="${FLEET:-$(dirname "$MADEVO")/fleet}"
GPUS=0
SEEDS=1-5
DRY=0
LIST=0
PHASES=()

while (( $# )); do
    case "$1" in
        --gpus)    GPUS="${2:?}"; shift 2 ;;
        --seeds)   SEEDS="${2:?}"; shift 2 ;;
        --dry-run) DRY=1; shift ;;
        --list)    LIST=1; DRY=1; shift ;;
        -h|--help) awk 'NR > 1 && /^#/ { sub(/^# ?/, ""); print; next } NR > 1 { exit }' "$0"; exit 0 ;;
        *)         PHASES+=("$1"); shift ;;
    esac
done
(( ${#PHASES[@]} )) || { echo "aucune phase (voir --help)" >&2; exit 2; }
[[ " ${PHASES[*]} " == *" all "* ]] && PHASES=(setup bench dynba frozen delete gamma viz)

expand_seeds() {  # 1-5 | 1,3,5 | 2
    local spec=$1 out=() part
    IFS=, read -ra parts <<< "$spec"
    for part in "${parts[@]}"; do
        if [[ $part == *-* ]]; then out+=($(seq "${part%-*}" "${part#*-}")); else out+=("$part"); fi
    done
    echo "${out[@]}"
}
SEED_LIST=($(expand_seeds "$SEEDS"))
IFS=, read -ra GPU_LIST <<< "$GPUS"

cd "$MADEVO"
LOGDIR=logs/paper_extras
mkdir -p "$LOGDIR"
(( LIST )) || python -c "import torch, devo" 2>/dev/null \
    || { echo "activer l'env conda madevo d'abord" >&2; exit 1; }

# ------------------------------------------------------------------ jeux de réglages
TRIALS_EVIMO="--set +trials=10"
EVIMO="configs/eval/evimo2.yaml $TRIALS_EVIMO"
# Mêmes réglages que la campagne cross-dataset du papier (fleet/n3-n9)
declare -A CROSS=(
    [rpg]="configs/eval/rpg.yaml --set +trials=10"
    [mvsec]="configs/eval/mvsec.yaml --set +trials=10"
    [eds]="configs/eval/eds.yaml --set +trials=3 --set devo.config=config/eval_eds_buf8k.yaml"
    [vector]="configs/eval/vector.yaml --set +trials=3 --set dataset.split=$FLEET/n8/split_all.txt"
    [tumvie]="configs/eval/tumvie.yaml --set +trials=3 --set dataset.split=$FLEET/n6/split_m.txt"
)
CROSS_ORDER=(rpg mvsec tumvie vector eds)   # du plus rapide au plus long
DYN() { echo "--set +devo.cfg_overrides.$1=$2"; }

# ------------------------------------------------------------------ file de jobs
QUEUE=()   # "LAUNCH_ID|SEED|nom|args de jobs/eval_table.sh"
add() {    # add <launch_id> <nom> <args...>  (une entrée par seed)
    local lid=$1 name=$2; shift 2
    for s in "${SEED_LIST[@]}"; do QUEUE+=("$lid|$s|${name}_s$s|$*"); done
}

phase_setup() {
    local patch="$HERE/madevo_dyn_modes.patch"
    if git apply --reverse --check -p1 "$patch" 2>/dev/null; then
        echo "[setup] patch déjà appliqué"
    else
        git apply -p1 "$patch" && echo "[setup] patch appliqué (devo/config.py, devo/devo.py, evals/eval_table.py)"
    fi
    cat > configs/eval/sources/evimo2_pw3_step8k.yaml <<'EOF'
# Couplés pw3 au step 8000 : DEVO encore gelé (dégel à 10 000), seul f_θ a appris, par la
# pose loss à travers ω (et la loss masque). Isole le couplage de l'adaptation de DEVO.
ms_arch: configs/ms/v4_evimo2.yaml
m1: {ms: runs/v4_evimo2_pw3/@latest, ckpt: best_iou.pt}
m2: {coupled: runs/m2_evimo2_pw3/@latest, step: 8000}
m3: {coupled: runs/m3_evimo2_pw3/@latest, step: 8000}
EOF
    cat > configs/eval/sources/evimo2_step8k.yaml <<'EOF'
# Couplés pw7 au step 8000 : DEVO encore gelé (dégel à 10 000).
ms_arch: configs/ms/v4_evimo2.yaml
m1: {ms: runs/v4_evimo2/@latest, ckpt: best_iou.pt}
m2: {coupled: runs/m2_evimo2/@latest, step: 8000}
m3: {coupled: runs/m3_evimo2/@latest, step: 8000}
EOF
    echo "[setup] sources evimo2_pw3_step8k / evimo2_step8k écrits"
    local missing=0
    for e in m2_evimo2_pw3 m3_evimo2_pw3 m2_evimo2 m3_evimo2; do
        n=$(ls ${MADEVO_RUNS:-runs}/$e/*/seed*/checkpoints/ms_step8000.pt 2>/dev/null | wc -l)
        echo "[setup] $e : $n seeds avec ms_step8000.pt"; (( n >= ${#SEED_LIST[@]} )) || missing=1
    done
    (( missing == 0 )) || echo "[setup] ATTENTION : checkpoints step8000 manquants (phase frozen)"
    python -c "from devo.config import cfg; assert 'DYN_BA_WEIGHT' in cfg" \
        && echo "[setup] OK"
}

phase_bench() {
    echo "[bench] GPU : $(nvidia-smi --query-gpu=name,memory.used,utilization.gpu --format=csv,noheader | head -1)"
    echo "[bench] la machine doit être libre (utilisation GPU ~0 %) pour que la mesure ait un sens"
    (( DRY )) && return
    local h; h=$(hostname -s)
    nvidia-smi --query-gpu=name,memory.used,utilization.gpu --format=csv > $LOGDIR/bench_${h}_gpu.log
    CUDA_VISIBLE_DEVICES=${GPU_LIST[0]} python tools/ms_compute_cost.py --device cuda --reps 100 \
        > $LOGDIR/bench_${h}_ms_gpu.log 2>&1
    CUDA_VISIBLE_DEVICES=${GPU_LIST[0]} python tools/devo_compute_cost.py --frames 30 \
        > $LOGDIR/bench_${h}_devo_gpu.log 2>&1
    python tools/ms_compute_cost.py --device cpu --threads 4 --reps 20 > $LOGDIR/bench_${h}_ms_cpu4.log 2>&1
    echo "[bench] fini : $LOGDIR/bench_${h}_*.log"
}

phase_dynba() {
    local L=2026-11-25_dynba X; X="$(DYN DYN_BA_WEIGHT true) --set exp=eval_dynba"
    add $L dynba_evimo2_pw3 $EVIMO --set "methods=[oracle,m1,m2,m3]" --set sources=evimo2_pw3 $X
    add $L dynba_evimo2_pw7 $EVIMO --set "methods=[m1,m2,m3]" --set sources=evimo2 $X
}

phase_frozen() {
    local L=2026-11-25_frozen8k X="--set exp=eval_frozen8k"
    add $L frozen_evimo2_pw3 $EVIMO --set "methods=[m2,m3]" --set sources=evimo2_pw3_step8k $X
    add $L frozen_evimo2_pw7 $EVIMO --set "methods=[m2,m3]" --set sources=evimo2_step8k $X
    for d in "${CROSS_ORDER[@]}"; do
        add $L frozen_${d}_pw3 ${CROSS[$d]} --set "methods=[m2,m3]" --set sources=evimo2_pw3_step8k $X
    done
}

phase_delete() {
    local L=2026-11-25_delete X; X="$(DYN DYN_DELETE true) --set exp=eval_delete"
    add $L delete_evimo2 $EVIMO --set "methods=[oracle,m1]" --set sources=evimo2_pw3 $X
    for d in "${CROSS_ORDER[@]}"; do
        add $L delete_${d} ${CROSS[$d]} --set "methods=[m1]" --set sources=evimo2_pw3 $X
    done
}

phase_gamma() {
    for g in 2 4; do
        local L=2026-11-25_gamma$g X; X="$(DYN DYN_GAMMA $g.0) --set exp=eval_gamma$g"
        add $L gamma${g}_evimo2 $EVIMO --set "methods=[m1]" --set sources=evimo2_pw3 $X
        for d in eds rpg mvsec tumvie vector; do   # EDS d'abord : c'est la cible
            add $L gamma${g}_${d} ${CROSS[$d]} --set "methods=[m1]" --set sources=evimo2_pw3 $X
        done
    done
}

phase_viz() {
    local L=2026-11-25_viz X="--set +save_viz=true --set exp=eval_viz"
    local keep=("${SEED_LIST[@]}"); SEED_LIST=(1)
    add $L viz_evimo2 configs/eval/evimo2.yaml --set +trials=1 --set "methods=[vanilla,oracle,m1]" --set sources=evimo2_pw3 $X
    add $L viz_eds configs/eval/eds.yaml --set +trials=1 --set devo.config=config/eval_eds_buf8k.yaml --set "methods=[vanilla,m1]" --set sources=evimo2_pw3 $X
    SEED_LIST=("${keep[@]}")
}

# ------------------------------------------------------------------ exécution
for p in "${PHASES[@]}"; do
    case "$p" in
        setup) (( DRY )) && echo "[dry-run] setup : patch + sources" || phase_setup ;;
        bench) (( LIST )) || phase_bench ;;
        dynba|frozen|delete|gamma|viz) "phase_$p" ;;
        *) echo "phase inconnue : $p" >&2; exit 2 ;;
    esac
done

(( ${#QUEUE[@]} )) || exit 0
echo "== ${#QUEUE[@]} évals à lancer sur GPU ${GPU_LIST[*]}"

run_one() {  # run_one <gpu> <entrée de file>
    local gpu=$1 lid seed name args
    IFS='|' read -r lid seed name args <<< "$2"
    set -f   # `methods=[m1,m2]` ne doit pas être pris pour un motif de fichiers
    if (( LIST )); then
        printf 'GPU%s  %-22s seed %s  %s\n' "$gpu" "$lid" "$seed" "$args"; return
    fi
    if (( DRY )); then
        echo "GPU$gpu  LAUNCH_ID=$lid SEED=$seed jobs/eval_table.sh $args"
        LAUNCH_ID=$lid SEED=$seed bash jobs/eval_table.sh $args --dry-run > "$LOGDIR/$name.dryrun.log" 2>&1 \
            && echo "        dry-run OK" || echo "        dry-run ÉCHEC : $LOGDIR/$name.dryrun.log"
        return
    fi
    echo "[$(date +%H:%M)] GPU$gpu début $name"
    if CUDA_VISIBLE_DEVICES=$gpu LAUNCH_ID=$lid SEED=$seed bash jobs/eval_table.sh $args > "$LOGDIR/$name.log" 2>&1; then
        echo "[$(date +%H:%M)] GPU$gpu fini  $name"
    else
        echo "[$(date +%H:%M)] GPU$gpu ÉCHEC $name (voir $LOGDIR/$name.log)"
    fi
}

# Une file par GPU, entrées réparties en round-robin ; chaque file tourne en séquence.
pids=()
for gi in "${!GPU_LIST[@]}"; do
    (
        for qi in "${!QUEUE[@]}"; do
            (( qi % ${#GPU_LIST[@]} == gi )) && run_one "${GPU_LIST[$gi]}" "${QUEUE[$qi]}"
        done
    ) &
    pids+=($!)
    (( DRY )) && wait "${pids[-1]}"   # sortie lisible en dry-run
done
wait
(( DRY )) || echo "== terminé. Résultats : evals_out/*/*/2026-11-25_*/seed*/ (DONE = réussi) ; journaux : $LOGDIR/"
