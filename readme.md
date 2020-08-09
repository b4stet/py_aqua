# Auditing QUiz Application
A little web app to fill a quiz, analyze answers, score and generate a report.

## Requirements
- python3-flask >= 0.12.2
- python3-magic >= 0.4.16

## Usage examples
### User mode versus reviewer mode
The application is built to run either in `user` mode, either in `reviewer` mode:
- in `user` mode, user can start a new quiz, load a previous answers file, save its answers
- in `reviewer` mode, in addition, user can enable and perform the review of answers and generate the gap analysis

In both modes, nothing is stored server side (no database, no file) to avoid complexity and allow running it locally without headache.

### Example 1
You want to let users fill the quiz autonomously.  

- with an additional layer (ningx/apache2), you can expose the application in user mode.  
- users send you their answers by other mean
- you run the application locally in reviewer mode, load their answers, review and generate the gap analysis

### Example 2
You drive the assessment with a user.

- you run the application locally in user mode, or in reviewer mode with review disabled
- you fill and save answers with the user
- later, in reviewer mode, you load its answers, review and generate the gap analysis

## Run
From root of application:
```
$ bash bin/web.sh <user|reviewer>
```

To run with your own quiz config:
```
$ bash bin/web.sh <user|reviewer> path/to/quiz_config.yml
```
Application config can be customized following structure of `config/app_default.yml` (explained below).  
If you plan to use `!include` tag, your main config and their parts must be in `config/` folder.

With default config
- user mode is available at `http://localhost:5000`.  
- reviewer mode is available at `http://localhost:8080`.  


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
- each item also has a `reviewer` part, listing accepted answers and their associated information for scoring and report:
    - keys are rendered as `qcm`, their name being the value of options, and a default `Not Reviewed` being automatically added
    - `score` is the value assigned to the review option
    - `priority` (eg. low/medium/high) corresponds to a weight in scoring, and a remediation priority in the report
    - `status` (eg. ok/ko/partial) corresponds to the class of the review option, and will be used to depict quiz performance in the report
    - `helper` is a sentence indicating in which case reviewer should select this option
    - `review` is a sentence interpreting the review option and will appear in the report
    - `remediation` is a sentence indicating remediation when needed and will appear in the report

### Identifiers unicity
Identifiers in quiz config must be unique within their category:
- section IDs must be uniques
- for a given section, group IDs must be unique
- for a given group, item IDs must be unique
- for a given table, column IDs must be unique
