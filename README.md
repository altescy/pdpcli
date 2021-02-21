PdpCLI
======

[![Actions Status](https://github.com/altescy/pdpcli/workflows/CI/badge.svg)](https://github.com/altescy/pdpcli/actions?query=workflow%3ACI)
[![Python version](https://img.shields.io/pypi/pyversions/pdpcli)](https://github.com/altescy/pdpcli)
[![PyPI version](https://img.shields.io/pypi/v/pdpcli)](https://pypi.org/project/pdpcli/)
[![License](https://img.shields.io/github/license/altescy/pdpcli)](https://github.com/altescy/pdpcli/blob/master/LICENSE)

### Quick Links

- [Introduction](#Introduction)
- [Installation](#Installation)
- [Tutorial](#Tutorial)
  - [Basic Usage](#basic-usage)
  - [Data Reader / Writer](#data-reader--writer)
  - [Plugins](#plugins)


## Introduction

PdpCLI is a pandas DataFrame processing CLI tool which enables you to build a pandas pipeline powered by [pdpipe](https://pdpipe.github.io/pdpipe/) from a configuration file. You can also extend pipeline stages and data readers/ writers by using your own python scripts.

### Features
  - Process pandas DataFrame from CLI without wrting Python scripts
  - Support multiple configuration file formats: YAML, JSON, Jsonnet
  - Read / write data files in the following formats: CSV, TSV, JSONL, XLSX
  - Extensible pipeline and data readers / writers


## Installation

Installing the library is simple using pip.
```
$ pip install pdpcli
```


## Tutorial

### Basic Usage

1. Write a pipeline config file `config.yml` like below. The `type` fields under `pipeline` correspond to the snake-cased class names of the [`PdpipelineStages`](https://pdpipe.github.io/pdpipe/doc/pdpipe/#types-of-pipeline-stages). The other fields such as `stage` and `columns` specify the parameters of the `__init__` methods of the corresponging classes. Internally, this configuration file is converted to Python objects by [`colt`](https://github.com/altescy/colt).

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

2. Build a pipeline by training on `train.csv`. The following command generage a pickled pipeline file `pipeline.pkl` after training.
```
$ pdp build config.yml pipeline.pkl --input-file train.csv
```

3. Apply fitted pipeline to `test.csv` and get output of the processed file `processed_test.jsonl` by the following command. PdpCLI automatically detects the output file format based on the file name. In the following example, processed DataFrame will be exported as the JSONL format.
```
$ pdp apply pipeline.pkl test.csv --output-file processed_test.jsonl
```

4. You can also directly run the pipeline from a config file if you don't need to fit the pipeline.
```
$ pdp apply config.yml test.csv --output-file processed_test.jsonl
```

5. It is possible to change parameters via command line:
```
pdp apply.yml test.csv pipeline.stages.drop_columns.column=age
```

### Data Reader / Writer


### Plugins

By using plugins, you can extend PdpCLI. The plugin feature enables you to use your own pipeline stages, data reader / writer and commands.

#### Add a new stage

1. Write your plugin script `mypdp.py` like the following. `PrintStage` just shows the DataFrame on stdout.
```python
import pdpcli

@pdpcli.PdPipelineStage.register("print")
class PrintStage(pdpcli.PdPipelineStage):
    def _prec(self, df):
        return True

    def _transform(self, df, verbose):
        print(df.to_string(index=False))
        return df
```

2. Update `config.yml` to use your plugin.
```yml
pipeline:
    type: pipeline
    stages:
        drop_columns:
        ...
        
        print:
            type: print
            
        encode:
        ...
```

2. Execute command with `--module mypdp` and you can see the DataFrame after `drop_columns`.
```
$ pdp apply config.yml test.csv --module mypdp
```

#### Add a new command

You can also add new coomands not only stages.

1. Add the following script to `mypdp.py`. This `greet` command prints out a greeting message with your name.
```python
@pdpcli.Subcommand.register(
    name="greet",
    description="say hello",
    help="say hello",
)
class GreetCommand(pdpcli.Subcommand):
    requires_plugins = False

    def set_arguments(self):
        self.parser.add_argument("--name", default="world")

    def run(self, args):
        print(f"Hello, {args.name}!")

```

2. To register this command, you need to create the`.pdpcli_plugins` file. Due to the module import order, the `--module` option is unavailable for command registration.
```
$ echo "mypdp" > .pdpcli_plugins
```

3. Run the following command and get the message like below. By using the `.pdpcli_plugins` file, it is unnecessary to enter the `--module` option for each execution.
```
$ pdp greet --name altescy
Hello, altescy
```
