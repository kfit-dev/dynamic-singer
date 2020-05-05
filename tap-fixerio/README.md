# tap-fixerio

A [Singer Tap] Tap to extract currency exchange rate data from [fixer.io].

## How to use it

### Install and Run

First, make sure Python 3 is installed on your system or follow these
installation instructions for [Mac] or [Ubuntu].

Then, get an access key from [fixer.io](http://fixer.io). You need at
least the basic plan to get exchange rates from a base currency (such as
USD).

Then, convert `config.sample.json` to
`~/singer.io/tap_fixerio_config.json`; fill out your parameters:

Config Key | Required? | Default | Description
--- | --- | --- | ---
`subscription_plan` | Yes | 'free' | Your fixer.io subscription plan
`start_date` | Yes | Today | The starting date from which rates will be pulled in `YYYY-MM-DD` format (overridden if a state file is passed)
`access_key` | Yes | None | Your fixer.io access key
`symbols` | No | None | An optional list of currency symbols to fetch in the following format: ['USD', 'GBP', etc.]. If not specified fixer will return a list of all exchange rates for each day
`base` | Yes | 'USD' | The base rate to which others will be converted (not available in free subscription plan, for which it is set to 'EUR')

It's recommended to use a virtualenv:

```bash
python3 -m venv ~/.virtualenvs/tap-fixerio
source ~/.virtualenvs/tap-fixerio/bin/activate
pip install -U pip setuptools
pip install -e '.'
```

Like all Singer taps, the output of `tap-fixerio` should be piped to a Singer target. 
Deactivate the `tap-fixerio` virtual environment by using the `deactivate` command, 
then set up the `target-csv` virtual environment according to the instructions
[here](https://github.com/singer-io/target-csv/blob/master/README.md).

Once `target-csv`, or another Singer target, is installed in its own virtual
environment run them with the following command:

```bash
~/.virtualenvs/tap-fixerio/bin/tap-fixerio --config ~/singer.io/tap_fixerio_config.json | ~/.virtualenvs/target-csv/bin/target-csv
```

The data will be written to a file called `exchange_rate.csv` in your
working directory.

```bash
$ cat exchange_rate.csv
AUD,BGN,BRL,CAD,CHF,CNY,CZK,DKK,GBP,HKD,HRK,HUF,IDR,ILS,INR,JPY,KRW,MXN,MYR,NOK,NZD,PHP,PLN,RON,RUB,SEK,SGD,THB,TRY,ZAR,EUR,USD,date
1.3023,1.8435,3.0889,1.3109,1.0038,6.869,25.47,7.0076,0.79652,7.7614,7.0011,290.88,13317.0,3.6988,66.608,112.21,1129.4,19.694,4.4405,8.3292,1.3867,50.198,4.0632,4.2577,58.105,8.9724,1.4037,34.882,3.581,12.915,0.9426,1.0,2017-02-24T00:00:00Z
```

---

Copyright &copy; 2017 Stitch

[Singer Tap]: https://singer.io
[fixer.io]: https://fixer.io
[Mac]: http://docs.python-guide.org/en/latest/starting/install3/osx/
[Ubuntu]: https://www.digitalocean.com/community/tutorials/how-to-install-python-3-and-set-up-a-local-programming-environment-on-ubuntu-16-04