# benchmark

## python env setup
```bash
python3 -m venv ~/.py3_env
source ~/.py3_env/bin/activate
pip install -r ./bench/requirements.txt
```

## MIPS Steps of each Layer
```bash
./bench/steps_simple_mp.sh
# or
./bench/steps_llama_mp.sh
```

Plot:
```bash
python3 ./bench/stats_log_convert.py
python3 ./bench/stats_plot.py
python3 ./bench/stats_plot_stacked_time.py
```

## Challenge Benchmark

```bash
./bench/challenge_simple.sh | tee ./logs/challenge_simple.log
# or
./bench/challenge_simple_mp.sh | tee ./logs/challenge_simple_mp.log
# or
./bench/challenge_llama.sh | tee ./logs/challenge_llama_mp.log
```

```bash
python3 ./bench/challenge_log_convert.py
```

```bash
python3 ./bench/challenge_plot.py
```