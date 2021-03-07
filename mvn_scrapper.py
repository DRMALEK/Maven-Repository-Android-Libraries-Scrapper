from time import sleep
from urllib.error import URLError
import bs4
from urllib.request import Request, urlopen
import urllib.parse as urlparse
import os
import sys
import time
from bs4.element import ContentMetaAttributeValue
import ssl
import shutil

base_search_url = "https://mvnrepository.com/search?"

base_url = "https://mvnrepository.com"

repos = [
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

sorting_criterias=[
    "relevance",
    "popular",
]


headers={'User-Agent': 'Mozilla/5.0'}

def return_artifact_urls(main_page_response):
    artifact_urls = []

    content = bs4.BeautifulSoup(main_page_response, 'html.parser')

    im_blocks = content.find_all(name="div", attrs={
        "class": "im"
    })

    for block in im_blocks:
        artifact_href = block.find(name="a")["href"]
        artifact_urls.append(base_url + artifact_href)

    return artifact_urls

def extract_realeses_url(artifact_page_response, artifact_url, all_versions):
    releases_url = []
    content = bs4.BeautifulSoup(artifact_page_response, 'html.parser')
    versions_table = content.find(name="table", attrs={
        "class": "grid versions"
    })


    if all_versions == "true" or all_versions == "True":
        versions_table = versions_table.find_all(name="a", attrs={
            "class": "vbtn"
        })

        for version_row in versions_table:
            version_href = version_row["href"]
            releases_url.append(artifact_url + '/'  + version_href.split('/')[1])

    # If not all releases is choosen, just return the last release
    else:
        versions_table_first_row = versions_table.find(name="a", attrs={
                    "class": "vbtn release"
        })
        first_version_href = versions_table_first_row["href"]
        releases_url.append(artifact_url + '/' +  first_version_href.split('/')[1])


    return releases_url


def return_home_page_url(bs4_object):
    info_table = bs4_object.find(name = "table", attrs = {
        "class" : "grid"
    })
    rows = info_table.find_all('tr')

    for row in rows:
        if row.find('th').text == 'HomePage':
            home_page = row.find('a')["href"]
            return home_page


def download_releases(releases_urls, sleep_duration, maximum_tries_per_url):
    dir_lib_created = False
    print(releases_urls)
    for release_url in releases_urls:
        response = send_request(release_url, sleep_duration, maximum_tries_per_url, "lib release page")

        # Try to parse the content of the artifact page, in case of error, continue to the next release
        content = bs4.BeautifulSoup(response, 'html.parser')
        release_downloading_urls_page_url = content.find(name = "a", text = "View All")["href"]

        artifact_name = content.find(name="h2", attrs={
            "class" : "im-title"}).find(name="a").text

        artifact_version = content.find(name="h2", attrs={
            "class" : "im-title"}).find_all(name="a")[-1].text

        artifact_home_page = return_home_page_url(content)

        if not artifact_home_page:
            artifact_home_page = artifact_name

        # Skip libraries that are in the Spring repos, since a log-in is requeried
        base_url = "{0.scheme}://{0.netloc}/".format(urlparse.urlsplit(release_downloading_urls_page_url))
        if base_url == "https://repo.spring.io/" or base_url == "http://repo.spring.io/":
            print("{0} skipped !".format(artifact_name))
            return

        #print(artifact_download_url)
        
        # Start downloading
        try:
            if not dir_lib_created:
                # Create a main directory for the lib
                os.mkdir(os.path.join("out_repo" , artifact_name))
                dir_lib_created = True

            # Create a directory for each verison of the lib
            os.mkdir(os.path.join("out_repo" , artifact_name, artifact_version))

            # Write the home page info into to a file
            with open(os.path.join("out_repo" , artifact_name, "homePage.txt"), "w+") as home_page_file:
                home_page_file.write(artifact_home_page)

                current_try = 0

                release_downloading_urls_page = send_request(release_downloading_urls_page_url, sleep_duration, maximum_tries_per_url, "release downloading urls page")
                content = bs4.BeautifulSoup(release_downloading_urls_page, 'html.parser')

                # Download each file
                # TODO A filtering can be applied to discard not wanted files like javadoc etc.
                for url_element in content.find_all(name = "a"):
                    url_href = url_element.text   # Remove : from the href
                    print("Downloading from --> ", release_downloading_urls_page_url + '/' + url_href)
                    r = Request(release_downloading_urls_page_url + '/' + url_href)
                    try:
                        lib_file_content = urlopen(r, timeout=5).read()
                        with open(os.path.join("out_repo" , artifact_name , artifact_version , url_href), "wb") as output:
                            output.write(lib_file_content)
                    except URLError as e:
                            print('URLError = ' + str(e.reason))
                        
                    finally:
                            time.sleep(sleep_duration)
                        
        # If happens the same library as been encouterd, skip it
        except FileExistsError as e:
            continue
        except Exception as e:
            continue


def build_request_params(criterias, repos):
    request_params = []
    for repo in repos:
        for criteria in criterias:
            for page_index in range(1, 51):
                request_param = {
                        "q": "Android",
                        "repo": repo,
                        "p": page_index,
                        "sort": criteria
                }
                request_params.append(request_param)
    
    return request_params


def main(request_params, sleep_duration, all_versions, maximum_tries_per_url):
    for request_param in request_params:
        params = urlparse.urlencode(request_param)
        url = base_search_url + params
        tries = 0
            
        current_page = send_request(url, sleep_duration, maximum_tries_per_url, "libs page")
        if current_page :
            try:
                artifact_urls = return_artifact_urls(current_page)
            except Exception as excp:
                if str(excp) == "'NoneType' object is not subscriptable":                 # This excpetion means that there is a problem in parsing
                        continue

            for artifact_url in artifact_urls:
                artifact_page = send_request(artifact_url, sleep_duration, maximum_tries_per_url, "artifact page")
                if artifact_page:
                    try:
                        artifact_releases_url = extract_realeses_url(artifact_page, artifact_url, all_versions)
                        download_releases(artifact_releases_url, sleep_duration, maximum_tries_per_url)
                    except Exception as excp:
                        if str(excp) == "'NoneType' object is not subscriptable":                 # This excpetion means that there is a problem in parsing
                            continue

def send_request(url, sleep_duration, maximum_tries_per_url, helper_message):
    tries = 0
    if helper_message == "" : 
        message = ""
    
    else:
        message = "Current {0} : --> {1}\n".format(helper_message, url)

    while tries < maximum_tries_per_url:
        try:
            print(message, end="")
            request = Request(url, headers=headers)
            response = urlopen(request, timeout=5).read()
            return response
        except URLError as e:
            print('URLError = ' + str(e.reason))
        except ssl.SSLError as excp:
            print('Could not retrieve meta data for ' + url + '  [SKIP]  (' + str(excp) + ')')
        except Exception as excp:
            print('Could not retrieve meta data for ' + url + '  [SKIP]  (' + str(excp) + ')')
        finally:
            tries = tries + 1
            time.sleep(sleep_duration)
            
if __name__ == "__main__":
    try:
        repo_name = sys.argv[1]
        sorting_criteria = sys.argv[2]
        sleep_duration = sys.argv[3]
        maximum_tries_per_url = sys.argv[4]
        all_versions = sys.argv[5]
    except Exception as e:
        print("Usage: python3 mvn_scrapper.py [repo name] [sorting criteria] [sleep duration] [maximum tries per url] [all versions]")
        exit

    try:
        sleep_duration = int(sleep_duration)
    except:
        print("Please provide a valid number of seconds !")
        exit(1)

    try:
        maximum_tries_per_url = int(maximum_tries_per_url)
    except:
        print("Please provide a valid number of tries per request !")
        exit(1)

    if repo_name not in repos and repo_name != "all":
        print("Error please choose one of the supported repos ! : " + " ".join(i for i in repos) + " all")
        exit(1)


    if sorting_criteria not in sorting_criterias and sorting_criteria != "all":
        print("Error please choose one of the supported criterias ! : " + " ".join(i for i in sorting_criterias) + " all")
        exit(1)

    if sorting_criteria == "all":
        to_be_scraped_criterias = sorting_criterias

    else:
        to_be_scraped_criterias = [sorting_criteria]

    if repo_name == "all":
        to_be_scraped_repos = repos

    else:
        to_be_scraped_repos = [repo_name]


    try:
        os.mkdir("./out_repo")
    except FileExistsError as e:
        print("Error a directory named out_repo exists ! please delete it or move it to another directory and try again")
        exit(1)

    request_params = build_request_params(to_be_scraped_criterias, to_be_scraped_repos)
    main(request_params, sleep_duration, all_versions, maximum_tries_per_url)
    
