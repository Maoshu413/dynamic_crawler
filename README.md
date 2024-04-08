# dynamic_crawler 0.1.0
**Crawler using ad hoc Selenium for dynamically-loaded websites and elements. Example code crawls category lists drop-downs and URLs (can by DIY for other uses).**

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.9-blue.svg)

This project demonstrates how to use ad-hoc Selenium Python APIs to effectively crawl websites with dynamically loaded contents, emphasizing effectively waiting for elements to be accessible after reloading. Crawler solves the issue of invisible clickables (element.click) by using JavaScript.

Contains an example code with a primary and secondary dropdown list and a redirect button that only directs list selections when clicked.

---

![Example Usage GIF](https://drive.google.com/uc?export=download&id=19ND_YF-RmRAybBAAlU7-eT2gkJQ2SFsf)

The example code all_categories_crawler.py contains the following steps:

1. Load the page from a base URL
2. Scrapes the contents of two dropdown list boxes
3. Iterate selections of the two list boxes and press a “Go” button to refresh the domain list in a table
4. Write the scraped data to a file


**The example code can be modified to fit your personal use case. Most functions within the code are very useful and can be directly called.**

---

Crawled a lot of complicated and complex websites in the development process. Some websites automatically refresh after an element is clicked; others require an additional step of clicking another button that redirects the user (e.g. “Go”). This crawler code accommodates all of those instances.
