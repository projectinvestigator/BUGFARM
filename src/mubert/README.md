## muBERT mutant generation

In this section, we will show how to perform experiments of [muBERT](https://github.com/Ahmedfir/mBERTa) mutant generation.

One can run the following command to reproduce the experiments:
```
bash scripts/run_mubert.sh
```

The above command will 1) generate input files for muBERT, 2) run muBERT to mutate, and 3) parse results. One can find output files in `src/leam/output/timestamp`, which includes detailed mutants information for each project, and all mutants in one file `src/leam/output/timestamp/all_mubert_mutants.jsonl`, here `timestamp` is a unique hash automatically generated for current run.