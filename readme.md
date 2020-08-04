# Auditing QUiz Application
A little web app to fill a quiz, analyze answers, score and generate a report.

## Requirements
- python3-flask >= 0.12.2
- python3-magic >= 0.4.16

## Run in user mode
From root of application:
```
$ bash bin/web.sh user 
```

To run with your own quiz config:
```
$ bash bin/web.sh user path/to/quiz_config.yml
```

The application is then available at `http://localhost:8080`.  
Application config can be customized following structure of `config/app_default.yml`, and set as `$AQUA_APP` envrionment variable.

## Quiz config 
### Structure
The application renders the quiz from a yaml file as defined in `quiz_default.yml`.  
- a quiz has one or multiple section(s)
- each section has one or multiple group(s)
- each group has
    - a description
    - one or multiple item(s)
- each item is a question of type `qcm`, `text` or `table`
    - `qcm`: 
        - only one option can be ticked
        - `options` are the list of content received when form is posted, labels displayed are automatically deduced by replacing `_` with space, 
        - `Not Answered` option is automatically added and selected for new quiz, so that all items have a value when posting
    - `text`: 
        - `placeholder`, if not empty string, is the text written by default in the text area
    - `table`: 
        - `nb_rows` is the primary number of rows to create, 
        - columns can be of type `text` or `qcm`,
        - `size` is the displayed width of a column, using the grid system, hence sum of sizes for a table should be 12

### Identifiers unicity
Identifiers in quiz config must be unique within their category:
- section IDs must be uniques
- for a given section, group IDs must be unique
- for a given group, item IDs must be unique
- for a given table, column IDs must be unique

