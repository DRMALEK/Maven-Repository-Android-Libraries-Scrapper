# Mvn-Repository-Android-Libraries-Scrapper
A scrapper to download the most popular and most relevance Android third-party libraries From the maven repository

## Requirments 
  1. Python 3
  2. beautifulsoup4   4.9.3

## Usage

  `python3 mvn_scrapper.py [repository name] [sorting criteria] [sleep duration in seconds between requests] [maximum tries per url] [download_all]`

## Explanation 

  *Repository name* can be anyone of : [
    "jcenter",
    "central",
    "ibiblio-m2",
    "springio-plugins-release",
    "spring-libs-milestone",
    "sonatype-releases",
    "springio-libs-release",
    "google",
    "ibiblio-m2"
] ,or "all" to download libs from all the listed repos

  *Sorting criteria* can be anyone of : [
    "relevance",
    "popular",
], or "all" to use both cirterias 

  *Download_all* is an argument to indicate whether to download all releases of a library (true) or not (false), to  download just the last release of the library.
  
  
### Notes

The downloaded libraries will be stored in a folder named "out_repo" in the current working directory.

### Part of a Tübitak 1001 project. https://wise.cs.hacettepe.edu.tr/projects/security-risks/
