# TF-IDF Crawler

The TF-IDF Crawler is composed of several modules to crawl and extract site content, identify keywords and on-page topics using ngrams, and creating TF-IDF scores for discovered ngrams across all crawled pages.  Crawled pages can also be tagged with a category to perform category-level TF-IDF analysis.

## Background

Ngram extraction and TF-IDF scoring can help to summarize and categorize large bodies of content.

Ngrams (`n-`gram) are groups of one or more words and phrases that have been extracted from content based on stop words and punctuation.

[TF-IDF](http://www.tfidf.com/) scoring is a combination of `term frequency` (how often an ngram appears within a document) and `inverse document frequency` which indicates how often an ngram appears across all documents in the corpus.

Using TF and IDF together eliminates words that occur across all content (as they are not unique).  TF-IDF scores can also reveal unique ngrams that are only used with a limited set of documents within the corpus.

Some usecases for TF-IDF scores are to identify when keywords or topics are repeated over multiple documents, finding the most relevant document in a large corpus for target ngrams, and comparing TF-IDF scores between two similar corpuses to identify overlapping content or content gaps.

## TF-IDF Crawler Modules

The TF-IDF Crawler consists of three modules - the `thread-crawler`, the `htmlextractor`, and the `tfidf` module.

### Thread-crawler

The `thread-crawler` takes a list of URLs and fetches their content using threaded HTTP requests.  Five thread workers (worker count can be adjusted) simultaneously get the HTML content of each URL in the list.  Each page's body content is extracted using the `HTMLextractor` module and inline scripts are removed. Additional extractors can be added for specific sections of a page's HTML or to extract categorical information/tagging for category-level TF-IDF analysis.

The `thread-crawler` can export a CSV with each URL that was crawled, the start and end times for requesting that page, and the page's content.  Additional columns can be added for other extracted information.

Once the entire list of URLs has been crawled the `tfidf` module can begin extracting ngrams and calculating TF-IDF scores for each document and for any categories.


### HTMLextractor

The `HTMLextractor` module is an extremely flexible HTML DOM parser extension that can extract page content using `dataDefinitions`.  A `dataDefinition` matches a DOM element by tag name, attributes, or parent `dataDefinition` or a combination of all three. This enables matching for tags with inconsistent IDs or attributes and matching across different tags that have the same attribute or parent `dataDefinition`.

The `thread-crawler` just uses the `HTMLextractor` module to get all content within the `body` tag but additional extractors configured with `dataDefinitions` can be used to extract elements within the page (e.g. getting categorical information from a heading tag).

The `tfidf` extracts ngrams from each page's content to begin the TF-IDF scoring process.

### TFIDF

The `tfidf` module takes the crawled and extracted page content and extracts ngrams to create TF-IDF scores. First each document is analyzed to extract ngrams. A global ngram list tracks all ngrams found across all documents.

Once all ngrams have been extracted for all documents the `tfidf` module begins calculating the TF-IDF scores for each document.  TF-IDF scores are provided in a matrix of ngrams and documents. Overall term frequency is included as well as the most "relevant" document for each ngram - which is the document that has the highest TF-IDF score for that ngram.

If categories were included in the original URL list or extracted during the crawl then the TF-IDF scores will be calculated for each category.  The process is essentially identical to the document score except that each document's content is combined in each category before calculating the TF-IDF score.

## Getting Started

You'll first need to create a list of URLs containing the content you'd like to analyze.  If needed you can [crawl a site](https://github.com/myawesomebike/Text-Extraction-and-Processing) first to get your URL list or get a list of URLs from an XML sitemap.  Create a CSV of your list with URLs in the first column and any categories on the same row (see `test-urls.csv`).

Set the `csvPath` to your URL list in `thread-crawler.py` and start `thread-crawler.py`.

The crawler will begin fetching content from your URL list, extract ngrams, and then calculate the TF-IDF score.  This process can take a while if you're crawling a large site with extensive content.

The site crawl data, document TF-IDF scores, and category TF-IDF scores will be exported to CSV for additional analysis.

## TF-IDF Analysis Examples

This repo contains example data based on blog content from the [Github blog](https://github.blog/).

- `test-urls.csv` - A list of Github blog URLs with their categories

Running `thread-crawler.py` should generate three exports:

- `test-site-crawl.csv` - The crawl export of all of the blog page content
- `test-site-tfidf - documents.csv` - The TF-IDF scores for all ngrams by document
- `test-site-tfidf - categories.csv` - The TF-IDF scores for all ngrams by category

Ten posts from each blog section were included in the analysis and their document and category scores are also included.

### Finding terms used on all pages

If an ngram appears across all documents in a corpus then its TF-IDF score will be 0 and there will be no relevant document.

![Non-unique ngrams](https://github.com/myawesomebike/TFIDF/raw/main/img-frequent.png)

The terms above appear on all Github blog pages that were analyzied.

### Finding unique and relevant ngrams by page

Looking at TF-IDF scores by document will show which ngrams were most-associated or unqiue to that document.

![Relevant document ngrams](https://github.com/myawesomebike/TFIDF/raw/main/img-unique.png)

Term frequency can be used to determine if other documents contain a ngram and indicate how relevant this document is if the ngram is used often elsewhere.
