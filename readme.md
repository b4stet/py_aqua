# Auditing QUiz Application
A little web app to drive an audit, analyze answers, score and generate a report.

## Requirements
- python3-flask >= 0.12.2
- python3-magic >= 0.4.16

## Run
From root of application:
```
$ python3 -m run
```

To run with your own quiz config file:
```
$ AQUA_QUIZ=path/to/quiz_config.yml python3 -m web
```

The application is then available from `http://localhost:8080`.

## Quiz config structure
The application generate the quiz from `quiz_default.yml` or another yaml file if supplied.  
Its structure is as follow:
- a quiz has one or multiple section(s)
- each section has one or multiple group(s)
- each groupe has
    - a description
    - one or multiple item(s)
- each item is a question of type `qcm`, `text` or `table`
    - `qcm`: 
        - only one option can be ticked
        - `label` is the text displayed near the radio button, 
        - `value` is the content received when the form is posted
        - `Not Answered` option is automatically added and selected for new quiz, so that all items have a value when posting
    - `text`: 
        - `placeholder`, if not empty string, is the text written by default in the text area
    - `table`: 
        - `nb_rows` is the primary number of rows to create, 
        - columns can be of type `text` or `qcm` (as defined as above),
        - `size` is the displayed width of a column, using the grid system, hence total of sizes for a table should be 12

## Identifiers unicity
Identifiers in quiz config must be unique within their category:
- section IDs must be uniques
- for a given section, group IDs must be unique
- for a given group, item IDs must be unique
- for a given table, column IDs must be unique

