# Mvn-Repository-Android-Libraries-Scrapper
A scrapper to download the most popular and most relevance Android third-party libraries From the maven repository

## Requirments 
  1. Python 3
  2. beautifulsoup4   4.9.3

## Usage

  `python3 mvn_scrapper.py [repository name] [sorting criteria] [sleep duration in seconds between requests] [maximum tries per url] [download_all]`


  Repository name argument can be anyone of : [
    "jcenter",
    "central",
    "ibiblio-m2",
    "springio-plugins-release",
    "spring-libs-milestone",
    "sonatype-releases",
    "springio-libs-release",
    "google",
    "ibiblio-m2"
]

  Sorting criteria can be anyone of : [
    "relevance",
    "popular",
]

  Download_all is parameter to indicate whether to download all releases of a library (true) or not (false) to Just download the last release.
