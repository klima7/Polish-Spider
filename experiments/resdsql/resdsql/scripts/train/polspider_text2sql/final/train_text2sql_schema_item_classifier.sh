set -e

# train schema item classifier (CSpider version)
python -u schema_item_classifier.py \
    --batch_size 7 \
    --gradient_descent_step 5 \
    --device "0" \
    --learning_rate 1e-5 \
    --gamma 2.0 \
    --alpha 0.75 \
    --epochs 64 \
    --patience 1000 \
    --seed 42 \
    --save_path "./models/polspider_schema_item_classifier" \
    --tensorboard_save_path "./tensorboard_log/polspider_final_schema_item_classifier" \
    --train_filepath "./data/preprocessed_data/preprocessed_train_polspider.json" \
    --dev_filepath "./data/preprocessed_data/preprocessed_dev_polspider.json" \
    --model_name_or_path "xlm-roberta-large" \
    --use_contents \
    --add_fk_info \
    --mode "train"