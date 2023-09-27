## Finetuning Bug Detector

After generating bug datasets (i.e., train.jsonl, valid.jsonl, test.jsonl) and placing them under `/data/defect/`, you can execute the following command to finetune a model of your choice for 10 epochs:

`bash scripts/exp_with_args.sh defect none codebert 0 -1 64 2 512 3 2 10 1000 saved_models_train_leam_codebert-test_bugfarm tensorboard_train_leam_codebert-test_bugfarm results/train_leam_codebert-test_bugfarm.txt leam-base leam-base codebert-base`

The above command will finetune a bug detector based on codebert-base model on GPU 0. Then, it will store the best model, last model, predictions, cached datasets under `/saved_models_train_leam_codebert-test_bugfarm`.
