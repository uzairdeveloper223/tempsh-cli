# tempsh-cli

temporary file upload cli tool

## install

```bash
pipx install git+https://github.com/uzairdeveloper223/tempsh-cli
```

or with pip:

```bash
pip install git+https://github.com/uzairdeveloper223/tempsh-cli
```

for progress bar support:

```bash
pipx install git+https://github.com/uzairdeveloper223/tempsh-cli[progress]
```

## usage

```bash
tempsh-cli document.pdf
echo "hello world" | tempsh-cli
cat image.png | tempsh-cli
tempsh-cli -h
```

## features

- upload files up to 4gb
- stdin support
- files expire after 3 days
- cross-platform

## license

GPL-3.0