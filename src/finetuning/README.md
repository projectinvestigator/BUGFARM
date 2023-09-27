## Finetuning Bug Detector

After generating bug datasets (i.e., train.jsonl, valid.jsonl, test.jsonl) and placing them under `/data/defect/`, you can execute the following command to finetune a model of your choice for 10 epochs:

`python3 src/finetuning/finetune_defect.py --model_tag codet5_base --task defect --sub_task none --gpu 0`

The above command will finetune a bug detector based on codet5-base model on GPU 0. Then, it will store the best model, last model, predictions, cached datasets under `/saved_models`.
