### Install requirements
```bash
pip install -r requirements.txt
(For HiGHS , install it with conda:)
conda install -c conda-forge highs

Run a single instance in cbc (example: 10 teams)
python main.py --n 10 --solver cbc
Run a single instance in highs (example: 10 teams)
python main.py --n 10 --solver highs
Run study for multiple sizes (6, 8, 10, 12, 14 teams, both solvers)
python scripts/run_study.py

Results:
JSON files in res/MIP/
CSV + plot → res/study/  (in case of runnning the study file)
