# Auditing QUiz Application
A light web app to drive an audit, analyze answers, score and generate a report.

The application itself is just a templating rendering the quiz and the gap analysis defined in `config/quiz_default.yml`.
It allows to:
- fill or complete the quiz
- review the soundness of answers
- deduce the gap analysis
- generate a report (in html and/or docx)

## Requirements
- flask >= 0.12.2
- bs4 >= 4.7.1
- matplotblib >= 3.0.3
- pywaffle >= 0.6.1

## Use Case examples
### User mode versus reviewer mode
The application is built to run either in `user` mode, either in `reviewer` mode:
- in `user` mode, user can start a new quiz, load a previous answers file, save its answers
- in `reviewer` mode, user has an additional `gap analysis` menu, can enable/disable the review of answers and generate the gap analysis

In both modes, nothing is stored server side (no database, no file).

### Example 1
Users can fill the quiz autonomously.  

- with additional layers (nginx/apache2, authentication), you can expose the application in `user` mode.  
- users fill, save their answers as json and send you the json file by other mean
- you run the application locally in reviewer mode, load their answers, review and generate the gap analysis

### Example 2
Assessment is driven with users.

- you run the application locally in `user` mode, or in `reviewer` mode (with review disabled)
- you fill and save answers with the user
- later, in reviewer mode, you load answers, review and generate the gap analysis (docx and/or html)

## Run
### Web
From root of application:
```
$ bash bin/web.sh  --mode <user|reviewer>
```

To run with your own quiz config and/or app config:
```
$ bash bin/web.sh --mode <user|reviewer> --quiz path/to/quiz_config.yml --app path/to/app_config.yml
```

With default configs (`config/app_default.yml` and `config/quiz_default.yml`):
- user mode is available at `http://localhost:5000`.  
- reviewer mode is available at `http://localhost:8080`.  

### CLI
Several CLI commands are available to generate the report in docx format from the json file and to analyse the quiz.

1. Docx report generation:  
  The path to the docx template is defined in `analysis.docx_template` key of `quiz_config.yml`.  
  Then, to generate the document (with default config, or with your own):
    ```
    bash bin/cli.sh generate_report --review path/to/review.json --output filename.docx
    bash bin/cli.sh --quiz path/to/quiz_config.yml generate_report --review path/to/review.json --output filename.docx
    ```

2. Check validity of quiz config (all keys are present, ID unicity, ...):  
  Script stops at the first error: fix it and rerun until you get 'All good, quiz config is valid.'
    ```
    bash bin/cli.sh check_quiz
    bash bin/cli.sh --quiz path/to/quiz_config.yml check_quiz
    ```

3. Analyze items in your quiz (section, group, category and priority of each item):
  An `--output` option prints either as json (default), or as csv.
    ```
    bash bin/cli.sh list_quiz
    bash bin/cli.sh --quiz path/to/quiz_config.yml list_quiz --output csv
    ```

## Quiz config 
__WARNING:__ do not expose the quiz configuration. Indeed, some parts are in html format (pointed below), and therefore not escaped by rendering.

### Structure
The application renders the quiz from a yaml file as defined in the sample `quiz_default.yml`.  
- a quiz has one or multiple section(s)
- each section has one or multiple group(s)
- each group has
    - a `description`, in html format (only `<p>/<br>` and `<ul>/<li>` tags are supported for docx generation)
    - one or multiple item(s)
- each item is a question of one of the following types, with required parameters:
    - `comment` (the only one optional) aims to support the question, in html format
    - `qcm_unique`: 
        - only one option can be ticked
        - `options` are the list of possible answers 
        - `Not Answered` option is automatically added and selected for new quiz, so that all items have a value when posting
    - `qcm_multiple`: 
        - several options can be ticked
        - `options` are the list of possible answers 
        - `None` and `Not Answered` option is automatically added and selected for new quiz, so that all items have a value when posting
    - `text`: 
        - `placeholder`, if not empty string, is the text written by default in the text area
    - `table_simple` (first row is header): 
        - `nb_rows` is the primary number of rows to create, 
        - columns can be of type `text` or `qcm`,
        - `size` is the displayed width of a column, using the grid system, hence sum of sizes for a table should be 11 (1 is reserved for trash button)
    - `table_double` (first row and first column are headers): 
        - `rows` is the list of first column header, 
        - columns can be of type `text`, `qcm_multiple` or `qcm_unique`,
        - `size` is the displayed width of a column, using the grid system, hence sum of sizes for a table should be 12
- each item also has `analysis` part, to mark its weight and the theme to be attached to for the category score:
    - `category` will be used in the gap analysis, to group items by theme, it refers to the id defined in `analysis.categories[].id` key
    - `priority` (eg. low/medium/high) corresponds to a weight in scoring, and a remediation priority in the report
- each item, last, has a `reviewer` part, listing rules as a `qcm`, to deduce score and remediations from answers:
    - `option` is the label, a default `Not Reviewed` being automatically added. The keyword `disabled` discard the question in scoring
    - `score` is the value assigned to the review option
    - `status` (eg. ok/ko/partial) corresponds to the class of the review option, and will be used to depict quiz performance in the report
    - `helper` is a sentence indicating in which case reviewer should select this option
    - `review` is a sentence interpreting the review option and will appear in the report
    - `remediation` is a sentence indicating remediation when needed and will appear in the report
    - `short` is a short version of the remediation that will be used in the executive summary of the docx version of the report

### Unicity constraints
Due to `id` and qcm `option` being used as keys in answers and review files, some constraints should be followed for their values:
- no white space (for qcm options, '_' are replaced by white space on rendering),
- no '-',
- keyword `review` is forbidden.

Also, identifiers in quiz config must be unique within their category:
- section IDs must be uniques
- for a given section, group IDs must be unique
- for a given group, item IDs must be unique
- for a given table, column IDs must be unique

## Gap analysis config
Gap analysis report contains several chapters:
- a `summary` chapter, 
- one chapter for each category, 
- an appendix reproducing user answers.

### Scoring
Several plots are built from scores:
- Final and category grades 
- Grades distribution per category
- Grades distribution per sections
- Items distribution per status, as whole
- In each category, item distribution per status

Each score comes from the sum of `priority x item_score` for category/section scores, and sum of `priority x category_score` for the final score.
- all scores in the gap analysis range from 0 to 100
- priorities are weights defined under `analysis.priorities` key of `quiz_default.yml`

Score are then converted into a grade letter, a color, and a tag, all defined under `analysis.scoring` key for plots and summary chapter.
Item status are also converted in a color, under `analysis.statuses` key for plots.

### Summary chapter
The text is picked up from `analysis.summary.text` and `analysis.categories[].summary` keys, based on the tag assigned to final and category scores respectively.  
Then, a table gathers the main remediations among all categories, as defined by `analysis.summary.priorities[]`.

### Category chapters
Each category chapter has 3 parts:
- a description of items covered, defined under `analysis.categories[].description` in html format  (only `<p>/<br>` and `<ul>/<li>` tags are supported for docx generation) 
- the list of remediations, table automatically built from review results, ordered by priority
- the gap analysis: a waffle plot of item statuses and a table pointing strengh or weakness of each answer
