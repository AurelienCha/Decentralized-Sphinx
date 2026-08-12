clear
start=$(date +%s)
mkdir -p .benchmark/data/.logs
mkdir -p .benchmark/results
rm -rf .benchmark/data/.logs/*

# Parameters values
PATH_LENGTH=(3 4 5 6 7)
THRESHOLD=(3 5 10 20) 
MIXNODES=(100)
STTPS=(50)
CLIENTS=(40)
# Most important parameters: 'PATH_LENGTH', 'THRESHOLD'

# Compute the number of runs
total_runs=$((${#PATH_LENGTH[@]} * ${#THRESHOLD[@]} * ${#MIXNODES[@]} * ${#STTPS[@]} * ${#CLIENTS[@]}))

i=0
# Run all tests
for p in "${PATH_LENGTH[@]}"; do  # PATH_LENGTH
    for t in "${THRESHOLD[@]}"; do  # THRESHOLD
        for m in "${MIXNODES[@]}"; do  # NBR_MIXNODES
            for s in "${STTPS[@]}"; do  # NBR_STTPS
                for c in "${CLIENTS[@]}"; do  # NBR_CLIENTS
                    i=$((i + 1))
                    echo "Run: $i / $total_runs"
                    ./run.sh -p $p -t $t -m $m -s $s -c $c -v 0
                    dir=.benchmark/data/.logs/p${p}_t${t}_m${m}_s${s}_c${c}
                    mkdir $dir
                    mv .logs/* -t $dir
                done
            done
        done
    done
done

end=$(date +%s)
echo "All ${total_runs} runs achieved in $((end - start)) sec"

python .benchmark/data/gather_data.py

python .benchmark/run_original_sphinx.py

python .benchmark/comparison_time.py

end=$(date +%s)
echo "Benchmark finished in $((end - start)) sec"


