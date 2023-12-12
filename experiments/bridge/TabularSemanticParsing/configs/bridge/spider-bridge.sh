#!/usr/bin/env bash

data_dir="data/spider"  # pol_spider_mix
db_dir="data/spider/database"
dataset_name="spider"
model="bridge"
question_split="True"
query_split="False"
question_only="True"
normalize_variables="False"
denormalize_sql="True"
omit_from_clause="False"
no_join_condition="False"
table_shuffling="True"
use_lstm_encoder="True"
use_meta_data_encoding="True"
use_graph_encoding="False"
use_typed_field_markers="False"
use_picklist="True"
anchor_text_match_threshold=0.85
no_anchor_text="False"
top_k_picklist_matches=2
sql_consistency_check="True"
atomic_value_copy="False"
process_sql_in_execution_order="True"
share_vocab="False"
sample_ground_truth="False"
save_nn_weights_for_visualizations="False"
vocab_min_freq=0
text_vocab_min_freq=0
program_vocab_min_freq=0
max_in_seq_len=512
max_out_seq_len=60

num_steps=100000
curriculum_interval=0
num_peek_steps=1000
num_accumulation_steps=3
save_best_model_only="False"
train_batch_size=11
dev_batch_size=16
encoder_input_dim=768
encoder_hidden_dim=400
decoder_input_dim=400
num_rnn_layers=1
num_const_attn_layers=0

use_oracle_tables="False"
num_random_tables_added=0
use_additive_features="False"

schema_augmentation_factor=1
random_field_order="False"
data_augmentation_factor=1
augment_with_wikisql="False"
num_values_per_field=0
pretrained_transformer="bert-base-multilingual-uncased"
fix_pretrained_transformer_parameters="False"
bert_finetune_rate=0.00006
learning_rate=0.0005
learning_rate_scheduler="inverse-square"
trans_learning_rate_scheduler="inverse-square"
warmup_init_lr=0.0005
warmup_init_ft_lr=0.00003
num_warmup_steps=4000
emb_dropout_rate=0.3
pretrained_lm_dropout_rate=0
rnn_layer_dropout_rate=0
rnn_weight_dropout_rate=0
cross_attn_dropout_rate=0
cross_attn_num_heads=8
res_input_dropout_rate=0.2
res_layer_dropout_rate=0
ff_input_dropout_rate=0.4
ff_hidden_dropout_rate=0.0

grad_norm=0.3
decoding_algorithm="beam-search"
beam_size=16
bs_alpha=1.05

data_parallel="False"
