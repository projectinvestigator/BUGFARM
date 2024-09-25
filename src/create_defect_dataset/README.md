## BugSwarm

We use the real dataset provided by [BugSwarm](http://www.bugswarm.org/) to evaluate the performance of finetuned models. The extracted dataset from BugSwarm is uploaded under `/BUGFARM/real_bugs/` in the anonymous Google Drive folder shared as part of the artifacts. Project files are not uploaded because they are too big, but one can download and mine them using the BugSwarm tool. If project files are available, you can execute the following to create BugSwarm defect dataset:

`python3 src/create_defect_dataset/extract_bugswarm.py`

## Mockito-Closure

We use the real dataset (Mockito and Closure) provided by [Defects4J](https://github.com/rjust/defects4j) to evaluate the performance of finetuned models. The extracted dataset from Defects4J (MC) is uploaded under `/BUGFARM/real_bugs/` in the anonymous Google Drive folder shared as part of the artifacts. You need to have Defects4J V2.0.0 set in order to extract correct and buggy method pairs using the patches provided by Defects4J. Once everything is set, you should execute the following in order to extract method pairs:

`python3 src/create_defect_dataset/extract_mc.py`

## RegMiner

We use the real dataset provided by [RegMiner](https://github.com/SongXueZhi/RegMiner) to evaluate the performance of finetuned models. The extracted dataset is uploaded under `RegMiner/RegMiner_mutants` in the anonymous Google Drive folder shared as part of the artifacts. One can run the following command to extract mutants and methods:

`python3 src/create_defect_dataset/extract_regminer.py`

## LEAM

We run [LEAM](https://github.com/tianzhaotju/LEAM) to generte mutants as part of our fine-tuning dataset. The extracted dataset is uploaded under `LEAM/LEAM_mutants` in the anonymous Google Drive folder shared as part of the artifacts. One can run the following command to extract LEAM mutants and methods:

`python3 src/create_defect_dataset/extract_leam.py`

## muBERT

We run [muBERT](https://github.com/Ahmedfir/mBERTa) to generte mutants as part of our fine-tuning dataset. The extracted dataset is uploaded under `muBERT/muBERT_mutants` in the anonymous Google Drive folder shared as part of the artifacts. One can run the following command to extract muBERT mutants and methods:

`python3 src/create_defect_dataset/extract_mubert.py`

## Finetuning Dataset

After extraction of a dataset, you need to execute the following in order to create the finetuning dataset in the proper format required by CodeT5 artifacts. Each instance of finetuning dataset is required to have a `func` field which indicates the method, `idx` which is a unique ID of that instance, and `target` which shows whether the code is buggy or fixed (1 for fixed, 0 for buggy).

`python3 src/create_defect_dataset/create_defect_dataset.py --type bugfarm --model codebert-base`
