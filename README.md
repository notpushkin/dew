# deɯ

Simple parallel task runner for Python. A nice `concurrent.futures` wrapper for
those who hate boilerplate.

```
pip3 install --user https://u.ale.sh/dew-0.1.0-py3-none-any.whl
```

## Usage

Example:

```py
# grab_instagram_user.py
import json
import requests

def f(username):
    r = requests.get(f"https://instagram.com/{username}")
    if not r.ok:
        return None
    else:
        data = (
            r.text.split("window._sharedData = ", 1)[1]
            .split("</script", 1)[0]
            .rstrip(";")
        )
        return json.loads(data)["entry_data"]["ProfilePage"][0]["graphql"]["user"]
```

```
$ dew --help
Usage: dew [OPTIONS] PYFILE [INFILE]

  Run a piece of code (PYFILE) for every entry in INFILE, in
  parallel.

Options:
  -t, --input-type [lines|json|jsonl|csv|csv-bare]
  --max-workers INTEGER
  -i, --indent INTEGER
  --help

$ dew grab_instagram_user.py users.txt > user_data.json
100%|█████████████████████████| 100/100 [00:07<00:00, 14.03it/s]

$ less user_data.json
{
  "void_himmel": {
    "biography": "♡ artist\n♡ programmer\n♡ japaneese street fashion lover\n♡ photographer\n🦄",
    "is_best_girl": true,
    ...
```

Exceptions thrown for one item (“task”) do not stop processing:

```py
def f(username):
    assert username != "notpushk.in"
    ...
```

```
$ dew grab_instagram_user_but_not_that_guy.py users.txt > user_data.json
  4%|█                        |   4/100 [00:01<00:06, 14.69it/s]
When running f('notpushk.in'):
  File "obvious_plant.py", line 6, in f
    assert username != "notpushk.in"
YeahFuckThatGuyError
100%|█████████████████████████| 100/100 [00:07<00:00, 14.03it/s]

$ less user_data.json
{
  "notpushk.in": null,
  "foobar64": {
    ...
```

You can specify function to run (default `f`) on command line as well:

```
dew tasks.py:fetch_facebook_user fb.txt > fb.json
dew tasks.py:fetch_twitter_user tw.txt > tw.json
```
