# DAGW Format validator

A validator for the Danish GigaWord (DAGW) project format.

## Requirements
Python 3.7 or higher.

## Running

```
python src/validate.py <path_to_section>
```

For help:

```
python src/validate.py --help
```

which will return

```
usage: validate.py [-h] input

Validates a specific section of DAGW

positional arguments:
  input       Path to directory containing the section

optional arguments:
  -h, --help  show this help message and exit
```

## Authors

* **Manuel R. Ciosici** - *Initial work* - [manuelciosici](https://github.com/manuelciosici)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
