<p align="center">
    <a href="#readme">
        <img alt="logo" width="40%" src="picture/picture.png">
    </a>
</p>

---

**dynamic-singer**, Python API, Dynamic source, N targets, Prometheus exporter for Singer ETL.

This library is an extension for singer.io for easier deployment, metrices, auto-detect schema and sinking to multiple targets. Read more about singer.io at https://www.singer.io/.

**dynamic-singer** also able to run in Jupyter Notebook.

## Table of contents

  * [Installing from the PyPI](#Installing-from-the-PyPI)
  * [How-to](#how-to)
    * [Run using Python](#run-using-python)
    * [Prometheus exporter](#Prometheus-exporter)
    * [N targets](#N-targets)

## Installing from the PyPI

```bash
pip install dynamic-singer
```

## How-to

### Run using Python

If you are familiar with singer, we know to start sourcing from Tap to Target required Bash `|` command, example,

```bash
tap-fixerio --config fixerio-config.json | target-gsheet --config gsheet-config.json
```

For dynamic-singer, you can run this using Python interface,

```python
import dynamic_singer as dsinger
source = dsinger.Source('tap-fixerio --config fixerio-config.json')
source.add('target-gsheet --config gsheet-config.json')
source.start()
```

Check google spreadsheet here, [link](https://docs.google.com/spreadsheets/d/1fH7C2KCi3P1Uef5wNv8-f_oJlYGYat9d5e5zKxkMoOk/edit?usp=sharing)

<img alt="logo" width="40%" src="picture/sheet1.png">

Full example, check [example/fixerio-gsheet.ipynb](example/fixerio-gsheet.ipynb).

### Prometheus exporter

Now we want to keep track metrices from Tap and Targets, by default we cannot do it using singer because singer using Bash pipe `|`, to solve that, we need to do something like,

```bash
tap | prometheus | target | prometheus
```

But `prometheus` need to understand the pipe. And nobody got time for that. Do not worry, by default dynamic-singer already enable prometheus exporter. Dynamic singer captures,

1. output rates from tap
2. data size from tap
3. output rates from target
4. data size from target

```python
import dynamic_singer as dsinger
source = dsinger.Source('tap-fixerio --config fixerio-config.json')
source.add('target-gsheet --config gsheet-config.json')
source.start()
```

So if you go to [http://localhost:8000](http://localhost:8000),

```text
# HELP total_tap_fixerio_total total rows tap_fixerio
# TYPE total_tap_fixerio_total counter
total_tap_fixerio_total 4.0
# TYPE total_tap_fixerio_created gauge
total_tap_fixerio_created 1.5887420455044758e+09
# HELP data_size_tap_fixerio summary of data size tap_fixerio (KB)
# TYPE data_size_tap_fixerio summary
data_size_tap_fixerio_count 4.0
data_size_tap_fixerio_sum 0.738
# TYPE data_size_tap_fixerio_created gauge
data_size_tap_fixerio_created 1.588742045504552e+09

total_target_gsheet_total 4.0
# TYPE total_target_gsheet_created gauge
total_target_gsheet_created 1.588742045529744e+09
# HELP data_size_target_gsheet summary of data size target_gsheet (KB)
# TYPE data_size_target_gsheet summary
data_size_target_gsheet_count 4.0
data_size_target_gsheet_sum 0.196
# TYPE data_size_target_gsheet_created gauge
data_size_target_gsheet_created 1.5887420455298738e+09
```

Name convention simply took from tap / target name.

### N targets

Let say I want to target more than 1 targets, I want to save to 2 different spreadsheets at the same time. If singer, we need to initiate pipe twice.

```bash
tap-fixerio --config fixerio-config.json | target-gsheet --config gsheet-config1.json
```

```bash
tap-fixerio --config fixerio-config.json | target-gsheet --config gsheet-config2.json
```

If we do this, both sheets probably got different data! Oh no!

So to add more than one target using dynamic-singer,

```python
import dynamic_singer as dsinger
source = dsinger.Source('tap-fixerio --config fixerio-config.json')
source.add('target-gsheet --config gsheet-config.json')
source.add('target-gsheet --config gsheet-config1.json')
source.start()
```

Check first google spreadsheet here, [link](https://docs.google.com/spreadsheets/d/1fH7C2KCi3P1Uef5wNv8-f_oJlYGYat9d5e5zKxkMoOk/edit?usp=sharing)

<img alt="logo" width="40%" src="picture/sheet1.png">

Check second google spreadsheet here, [link](https://docs.google.com/spreadsheets/d/1fH7C2KCi3P1Uef5wNv8-f_oJlYGYat9d5e5zKxkMoOk/edit?usp=sharing)

<img alt="logo" width="40%" src="picture/sheet2.png">

Full example, check [example/fixerio-gsheet-twice.ipynb](example/fixerio-gsheet-twice.ipynb).