# yanytapi

`yanytapi` is a Python wrapper for the [New York Times Article Search API][1]. Based on the excellent [`requests`][12] package, it provides full support for all of the API's search parameters, and also allows access to the request object itself for debugging purposes.
  

## Installation

With pip:

    $ pip install yanytapi


## Dependencies

yanytapi requires the [`requests`][2] package.


## Usage

Simply import and initialize the API with your developer key:

```python
>>> from yanytapi import SearchAPI
>>> api = SearchAPI("YourAPIKey")
```

Then call the `search` function with your desired search parameters/values:

```python
>>> articles = api.search("Obama", 
                          fq={"headline": "Obama", 
                              "source": ["Reuters", 
                                         "AP", 
                                         "The New York Times"]}, 
                          begin_date="20161001", # this can also be an int
                          facet_field=["source", "day_of_week"], 
                          facet_filter=True)
```

The search function returns an iterator of `Doc`'s with the following fields:
```json
[
  "_id",
  "blog",
  "byline",
  "document_type",
  "headline",
  "keywords",
  "lead_paragraph",
  "meta",
  "multimedia",
  "news_desk",
  "pub_date",
  "score",
  "section_name",
  "snippet",
  "source",
  "subsectoinName",
  "type_of_material",
  "uri",
  "web_url",
  "word_count"
]
```

You can specify multiple filters by using a dictionary::

```python
>>> fq = {"headline": "Obama", "source": ["Reuters", "AP", "The New York Times"]}
>>> articles = api.search("Obama", fq=fq)
```

And multiple values by using a list::

```python
>>> facet_field = ["source", "day_of_week"]
>>> articles = api.search("Obama", facet_field=facet_field)
```

More examples:

```python
# simple search
>>> articles = api.search("Obama")
# search between specific dates
>>> articles = api.search("Obama", begin_date="20161001", end_date="20161020", page=2)
# access most recent request object
>>> headers = api.req.headers
```

For a complete overview of the available search parameters, please refer to the [NYTimes Article Search API Documentation][4].


## History

This package was originally written by [Evan Sherlock][5] as [`nytimesarticle`][6]. It was subsequently forked and updated by [Matt Morrison][7], and subsequently released as [`NYTimesArticleAPI`][8], with contributions from [Gerald Spencer][9] and [Andrew Han][10]. `yanytapi` is a third iteration of forking focused mainly on packaging improvements, now maintained by Ed Kohlwey.


## License

This is free software. It is licensed under the [MIT License][11]. Feel free to use this in your own work. However, if you modify and/or redistribute it, please attribute me in some way, and distribute your work under this or a similar license. A shout-out or a beer would be appreciated.



  [1]: https://developer.nytimes.com/article_search_v2.json
  [2]: https://pypi.python.org/pypi/requests
  [3]: https://pypi.python.org/pypi/setuptools
  [4]: http://developer.nytimes.com/docs/read/article_SearchAPI_v2
  [5]: https://github.com/evansherlock
  [6]: https://github.com/evansherlock/nytimesarticle
  [7]: https://github.com/MattDMo
  [8]: https://pypi.python.org/pypi/yanytapi
  [9]: https://github.com/Geethree
  [10]: https://github.com/handrew
  [11]: http://opensource.org/licenses/MIT
  [12]: http://docs.python-requests.org
