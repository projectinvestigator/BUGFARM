## LEAM mutant generation

In this section, we will show how to perform experiments of [LEAM](https://github.com/tianzhaotju/LEAM) mutant generation.

One can run the following command to reproduce the experiments:
```
bash scripts/run_leam.sh
```

The above command will 1) generate input files for LEAM, 2) run LEAM to mutate, and 3) parse results. One can find output files in `src/leam/output/timestamp`, which includes detailed mutants information for each project, and all mutants in one file `src/leam/output/timestamp/results/all_leam_mutants.jsonl`, here `timestamp` is a unique hash automatically generated for current run.