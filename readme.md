# Auditing QUiz Application
A light web app to drive an audit, analyze answers, score and generate a report.

## Requirements
- flask >= 0.12.2
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
- users send you their answers by other mean (the saved json file)
- you run the application locally in reviewer mode, load their answers, review and generate the gap analysis

### Example 2
Assessment is driven with users.

- you run the application locally in `user` mode, or in `reviewer` mode (with review disabled)
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
The application renders the quiz from a yaml file as defined in the sample `quiz_default.yml`.  
- a quiz has one or multiple section(s)
- each section has one or multiple group(s)
- each group has
    - a description, in html multines format
    - one or multiple item(s)
- each item is a question of one of the following types, has a category and a priority:
    - `category` will be used in the gap analysis, to group items by theme, it refers to the id defined in `analysis.categories[].id` key
    - `priority` (eg. low/medium/high) corresponds to a weight in scoring, and a remediation priority in the report
    - `qcm`: 
        - only one option can be ticked
        - `options` are the list of content received when form is posted, labels displayed are automatically deduced by replacing `_` with space, 
        - `Not Answered` option is automatically added and selected for new quiz, so that all items have a value when posting
    - `text`: 
        - `placeholder`, if not empty string, is the text written by default in the text area
    - `table`: 
        - `nb_rows` is the primary number of rows to create, 
        - columns can be of type `text` or `qcm`,
        - `size` is the displayed width of a column, using the grid system, hence sum of sizes for a table should be 11 (1 is reserved for trash button)
- each item also has a `reviewer` part, listing rules as a `qcm`, to deduce score and remediations from answers:
    - `option` is the label, a default `Not Reviewed` being automatically added
    - `score` is the value assigned to the review option
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

## Gap analysis config
Gap analysis report contains a `summary` chapter, then one for each category, and finally an appendix grouping user answers.

### Scoring
Several plots are built from scores:
- Final and category grades 
- Grades distribution per category
- Grades distribution per sections
- In each category, item distribution per status

Each score comes from the sum of `priority x item_score` for category/section scores, and sum of `priority x category_score` for the final score.
- all score range from 0 to 100
- priorities are weights defined under `analysis.priorities` key of `quiz_default.yml`

Score are then converted into a grade letter, a color, and a tag, all defined under `analysis.scoring` key for plots and summary chapter.
Item status are also converted in a color, under `analysis.statuses` key for plots.

### Summary chapter
The text is picked up from `analysis.summary.text` and `analysis.categories[].summary` keys, based on the tag assigned to final and category scores respectively.  
Then, a table gathers the main remediations among all categories, as defined by `analysis.summary.priorities[]`.

### Category chapters
Each category chapter has 3 parts:
- a description of items covered, defined under `analysis.categories[].description` as html multilines format, and a waffle plot of item statuses
- the list of remediations, table automatically built from review results, ordered by priority
- the gap analysis: a table listing strengh or weakness of each answer
