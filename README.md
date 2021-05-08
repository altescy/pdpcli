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

PdpCLI is a pandas DataFrame processing CLI tool which enables you to build a pandas pipeline powered by [pdpipe](https://pdpipe.github.io/pdpipe/) from a configuration file. You can also extend pipeline stages and data readers / writers by using your own python scripts.

### Features
  - Process pandas DataFrame from CLI without wrting Python scripts
  - Support multiple configuration file formats: YAML, JSON, Jsonnet
  - Read / write data files in the following formats: CSV, TSV, JSON, JSONL, pickled DataFrame
  - Import / export data with multiple protocols: S3 / Databse (MySQL, Postgres, SQLite, ...) / HTTP(S)
  - Extensible pipeline and data readers / writers


## Installation

Installing the library is simple using pip.
```
$ pip install "pdpcli[all]"
```


## Tutorial

### Basic Usage

1. Write a pipeline config file `config.yml` like below. The `type` fields under `pipeline` correspond to the snake-cased class names of the [`PdpipelineStages`](https://pdpipe.github.io/pdpipe/doc/pdpipe/#types-of-pipeline-stages). Other fields such as `stage` and `columns` are the parameters of the `__init__` methods of the corresponging classes. Internally, this configuration file is converted to Python objects by [`colt`](https://github.com/altescy/colt).

```yaml
pipeline:
  type: pipeline
  stages:
    drop_columns:
      type: col_drop
      columns:
        - name
        - job

    encode:
      type: one_hot_encode
      columns: sex

    tokenize:
      type: tokenize_text
      columns: content

    vectorize:
      type: tfidf_vectorize_token_lists
      column: content
      max_features: 10
```

2. Build a pipeline by training on `train.csv`. The following command generages a pickled pipeline file `pipeline.pkl` after training. If you specify a URL of  file path, it will be automatically downloaded and cached.
```
$ pdp build config.yml pipeline.pkl --input-file https://github.com/altescy/pdpcli/raw/main/tests/fixture/data/train.csv
```

3. Apply the fitted pipeline to `test.csv` and get output of a processed file `processed_test.jsonl` by the following command. PdpCLI automatically detects the output file format based on the file name. In this example, the processed DataFrame will be exported as the JSON-Lines format.
```
$ pdp apply pipeline.pkl https://github.com/altescy/pdpcli/raw/main/tests/fixture/data/test.csv --output-file processed_test.jsonl
```

4. You can also directly run the pipeline from a config file without fitting pipeline.
```
$ pdp apply config.yml test.csv --output-file processed_test.jsonl
```

5. It is possible to override or add parameters by adding command line arguments:
```
pdp apply config.yml test.csv pipeline.stages.drop_columns.column=name
```

### Data Reader / Writer

PdpCLI automatically detects a suitable data reader / writer based on a given file name.
If you need to use the other data reader / writer, add a `reader` or `writer` config to `config.yml`.
The following config is an exmaple to use SQL data reader.
SQL reader fetches records from the specified database and converts them into a pandas DataFrame.
```yaml
reader:
    type: sql
    dsn: postgres://${env:POSTGRES_USER}:${env:POSTGRES_PASSWORD}@your.posgres.server/your_database
```
Config files are interpreted by [OmegaConf](https://omegaconf.readthedocs.io/e), so `${env:...}` is interpolated by environment variables.

Prepare yuor SQL file `query.sql` to fetch data from the database:
```sql
select * from your_table limit 1000
```

You can execute the pipeline with SQL data reader via:
```
$ POSTGRES_USER=user POSTGRES_PASSWORD=password pdp apply config.yml query.sql
```


### Plugins

By using plugins, you can extend PdpCLI. This plugin feature enables you to use your own pipeline stages, data readers / writers and commands.

#### Add a new stage

1. Write your plugin script `mypdp.py` like below. `Stage.register("<stage-name>")` registers your pipeline stages, and you can specify these stages by writing `type: <stage-name>` in your config file.
```python
import pdpcli

@pdpcli.Stage.register("print")
class PrintStage(pdpcli.Stage):
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

2. Execute command with `--module mypdp` and you can see the processed DataFrame after running `drop_columns`.
```
$ pdp apply config.yml test.csv --module mypdp
```

#### Add a new command

You can also add new commands not only stages.

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

2. To register this command, you need to create the `.pdpcli_plugins` file in which module names are listed for each line. Due to module importing order, the `--module` option is unavailable for command registration.
```
$ echo "mypdp" > .pdpcli_plugins
```

3. Run the following command and get a message like below. By using the `.pdpcli_plugins` file, it is is not needed to add the `--module` option to a command line for each execution.
```
$ pdp greet --name altescy
Hello, altescy!
```
