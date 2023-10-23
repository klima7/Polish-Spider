# RAT-SQL

## General
1. Enter [`rat-sql`](rat-sql) directory.
2. Run container with:
    ```
    docker compose up --build
    ```
3. Enter container with command:
    ```
    docker exec -it ratsql bash
    ```

## Training

1. Place spider dataset under [`data/spider`](rat-sql/data/spider)
2. Run dataset preprocessing:
    ```
    python run.py preprocess experiments/spider-bert-run.jsonnet
    ```
3. Run training:
    ```
    python run.py train experiments/spider-bert-run.jsonnet
    ```

## Inference

1. Run evaluation:
    ```
    python run.py eval experiments/spider-bert-run.jsonnet
    ```