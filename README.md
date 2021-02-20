PdpCLI
======

[![Actions Status](https://github.com/altescy/pdpcli/workflows/CI/badge.svg)](https://github.com/altescy/pdpcli/actions?query=workflow%3ACI)

### Quick Links

- [Introduction](#Introduction)
- [Tutorial](#Tutorial)


## Introduction

PdpCLI is a pandas DataFrame processing CLI tool which enables you to build a pandas pipeline powered by [pdpipe](https://pdpipe.github.io/pdpipe/) from a configuration file. You can also extend pipeline stages and data readers/ writers by using your own python scripts.

### Features
  - Process pandas DataFrame from CLI without wrting Python scripts
  - Support multiple configuration file formats: YAML, JSON, Jsonnet
  - Read / write data files in the following formats: CSV, TSV, JSONL, XLSX
  - Extensible pipeline and data readers / writers


## Tutorial

### Basic Usage

1. Write a pipeline config file `config.yml` like below. The `type` fields under `pipeline` correspond to the snake-cased class names of the [`PdpipelineStages`](https://pdpipe.github.io/pdpipe/doc/pdpipe/#types-of-pipeline-stages).

```yaml
pipeline:
  type: pipeline
  stages:
    drop_columns:
      type: col_drop
      columns: foo

    encode:
      type: one_hot_encode
      columns: sex

    tokenize:
      type: tokenize_text
      columns: profile

    vectorize:
      type: tfidf_vectorize_token_lists
      column: profile
```

2. Build pipeline by training on `train.csv`. The following command generage a pickled pipeline file `pipeline.pkl`.
```
$ pdp build config.yml pipeline.pkl --input-file train.csv
```

3. Apply fitted pipeline to `test.csv` and output the processed file `processed_test.jsonl` by the following command. PdpCLI automatically detects the output file format based on the file name. In the following example, processed DataFrame will be exported as the JSONL format.
```
$ pdp apply pipeline.pkl test.csv --output-file processed_test.jsonl
```

4. You can also directly run the pipeline from a config file if you don't need to fit the pipeline.
```
$ pdp apply config.yml test.csv --output-file processed_test.jsonl
```
