# Gin bots

One day [@quelklef](https://github.com/Quelklef) decided to write a gin rummy bot runner.

## Setup

You'll need pipenv.

```bash
pipenv install
```

## Running

```bash
pipenv run python tournament.py
```

`pipenv run python tournament.py --help` for options.

## Competing

Add a new folder under the `bots/` folder. That folder *must* contain a file named `[your bot name].sh`, which should run your bot. For an example see `bots/simple/`.

## Current Competitors

+ [@quelklef](https://github.com/Quelklef)
  + random
  + simple
  + samplinax (currently disqualified for taking too long)
+ [@samm81](https://github.com/samm81/)
  + sam

### Most recent tournament results
random vs sam: mean = -61.33, stdev = 18.49

random vs simple: mean = -55.07, stdev = 16.99

sam vs simple: mean = +5.47, stdev = 27.04
