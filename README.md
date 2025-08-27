# STS MIP Project
# Sports Tournament Scheduling (MIP)
This project implements a Mixed-Integer Programming (MIP) model for the Sports Tournament Scheduling problem.  
The model is built in **Python with PuLP** and can be solved using **CBC**or **HiGHS**.
### Install requirements
```bash
pip install -r requirements.txt
(For HiGHS , install it with conda:)
conda install -c conda-forge highs
```

# HOW TO RUN
Run a single instance in cbc (example: 10 teams)
python main.py --n 10 --solver cbc
Run a single instance in highs (example: 10 teams)
python main.py --n 10 --solver highs
Run study for multiple sizes (6, 8, 10, 12, 14 teams, both solvers)
python scripts/run_study.py

#Results:
JSON files in res/MIP/
CSV + plot → res/study/  (in case of runnning the study file)
