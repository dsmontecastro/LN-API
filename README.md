# Light Novels API
Link: [https://ln-api-baql.onrender.com/](https://ln-api-baql.onrender.com/)

A minimal REST-API for light-novels coming from some of the more well-known publishers.
The website is made using __Python-Flask, MongoDB,__ and __LibSASS__.
The web-scraping is handled by __Python and Selenium__.


<br>


## JSON Schemas

### _Entry_ Object
| Attribute | Type             | Description                                              |
| --------- | ---------------- | -------------------------------------------------------- |
| _id       | ObjectID         | _Primary-Index_ created and used by __MongoDB__.         |
| date      | Date(YYYY-MM-DD) | Scheduled release date.                                  |
| table     | StringLiteral    | Name of the __Publisher__ of the specific _entry_.       |
| url       | String           | Link to the source page in the __Publisher__'s website.  |
| cover     | String           | Link to the cover page used by the __Publisher__.        |
| title     | String           | Full title of the _entry_, including the current volume. |
| blurb     | String           | Summary of the volume, chapter, or entire book.          |
| genres    | Array<String>    | List of associated tags and genres.                      |
| credits   | Array<Person>    | List of the credited __Person__(s).                      |
| media     | Array<Media>     | List of __Media__ formats used in the _entry_.           |


### _Media_ Object
| Attribute | Type          | Description                                                       |
| --------- | ------------- | ----------------------------------------------------------------- |
| format    | StringLiteral | "Audio", "Digital", or "Physical".                                |
| isbn      | String        | 10 or 13-digit [ISBN Code](https://isbn.org/about_isbn_standard). |
| price     | Decimal128    | Expected price in _US-Dollars ($)_.                               |


### _Person_ Object
| Attribute | Type   | Description                         |
| --------- | ------ | ----------------------------------- |
| name      | String | (Pen) Name used by the individual.  |
| position  | String | Position in the publishing process. |




<br>


## API Usage

### Modes
| Mode | Description                                                                   |
| ---- | ----------------------------------------------------------------------------- |
| show | Display results using the website UI.                                         |
| json | Display results as a JSON collection with the _count_ and array of _entries_. |


### Publishers
| Source               | Code |
| -------------------- | ---- |
| Cross Infinite World | CIW  |
| J-Novel Club         | JNC  |
| Kodansha             | KOD  |
| Seven Seas Ent.      | SEA  |
| Yen Press            | YEN  |
| All Tables           | ALL  |


### Filters
| Field   | Query              | Notes                  |
| ------- | ------------------ | ---------------------- |
| title   | ?title={string}    | -                      |
| credits | ?credits={string}  | Repeatable (AND)       |
| genres  | ?genres={string}   | Repeatable (OR)        |
| date    | ?date={YYYY-MM-DD} | Greater than or Equal  |
| format  | ?format={string}   | Audio/Digital/Physical |
| price   | ?price=${X.X}      | Less than or Equal     |
| isbn    | ?isbn={ISBN-Code}  | 10 or 13-digit Code    |



### To-do List:
* Deploy Scraper somewhere CRON-able
* Make API-Filters Hide-able (maybe?)