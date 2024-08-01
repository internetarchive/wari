import re
from urllib.parse import quote, unquote

import requests

import config
from src.models.exceptions import MissingInformationError, WikipediaApiFetchError
from src.models.v2.job import JobV2
from src.models.wikimedia.enums import WikimediaDomain


class ArticleJobV2(JobV2):
    """A generic job that can be submitted via the API"""

    # inherited from JobV2
    refresh: bool = False

    # primary definition in this class
    url: str = ""
    lang: str = "en"
    domain: WikimediaDomain = WikimediaDomain.wikipedia
    title: str = ""
    page_id: int = 0

    sections: str = ""
    revision: int = 0  # this is named just as in the MediaWiki API
    dehydrate: bool = True

    @property
    def iari_id(self) -> str:
        # FIXME must make sure iari_id replace wari_id everywhere
        if not self.lang:
            raise MissingInformationError()
        if not self.page_id:
            raise MissingInformationError()
        if not self.revision:
            raise MissingInformationError()
        return f"{self.lang}.{self.domain.value}.{self.page_id}.{self.revision}"

    @property
    def quoted_title(self):
        if not self.title:
            raise MissingInformationError("self.title was empty")
        return quote(self.title, safe="")

    def get_mediawiki_ids(self) -> None:
        from src import app

        app.logger.debug(
            f"ArticleJobV2::get_mediawiki_ids: self.page_id={self.page_id}"
        )

        if not self.page_id:
            app.logger.debug(
                f"ArticleJobV2::get_mediawiki_ids: lang={self.lang}, title={self.title}, lang={self.domain}"
            )
            if not self.lang or not self.title or not self.domain:
                raise MissingInformationError("url lang, title or domain not found")

            # https://stackoverflow.com/questions/31683508/wikipedia-mediawiki-api-get-pageid-from-url
            wiki_fetch_url = (
                f"https://{self.lang}.{self.domain.value}/"
                f"w/rest.php/v1/page/{self.quoted_title}"
            )
            headers = {"User-Agent": config.user_agent}
            response = requests.get(wiki_fetch_url, headers=headers)
            # console.print(response.json())
            if response.status_code == 200:
                data = response.json()
                # We only set this if the patron did not specify a revision they want
                if not self.revision:
                    self.revision = int(data["latest"]["id"])
                self.page_id = int(data["id"])

            elif response.status_code == 404:
                app.logger.error(
                    f"Could not fetch page data from {self.domain} because of 404. See {wiki_fetch_url}"
                )
            else:
                raise WikipediaApiFetchError(
                    f"Could not fetch page data. Got {response.status_code} from {wiki_fetch_url}"
                )

    def __urldecode_url__(self):
        """We decode the title to have a human readable string to pass around"""
        self.url = unquote(self.url)

    def __extract_url__(self):
        """This was generated with help of chatgpt using this prompt:
        I want a python re regex that extracts "en" "wikipedia.org"
        and "Test" from http://en.wikipedia.org/wiki/Test
        """
        from src import app

        app.logger.debug("extract_url: running")
        if self.url:
            self.__urldecode_url__()
            wiki_url_pattern = r"https?://(\w+)\.(\w+\.\w+)/wiki/(.+)"

            matches = re.match(wiki_url_pattern, self.url)
            if matches:
                groups = matches.groups()
                self.lang = groups[0]
                self.domain = WikimediaDomain(groups[1])
                self.title = groups[2]
            if not matches:
                app.logger.error("Not a supported Wikimedia URL")

    @property
    def __valid_sections__(self) -> bool:
        """Validate the sections, it should look like this:
        bibliography|further reading|works cited|sources|external links

        This code was generated by chatgpt

        Spaces around | are not allowed.
        Words separated by spaces are allowed.
        _ is not allowed anywhere"""
        underscore_pattern = re.compile(r"^[^_]*$")
        pipe_delimiter_pattern = r"^(\s*[^\s]+\s*)+(\s*\|\s*[^\s]+\s*)*$"
        if " | " in self.sections:
            return False
        if "||" in self.sections:
            return False
        if not re.fullmatch(underscore_pattern, self.sections):
            return False
        if re.fullmatch(pipe_delimiter_pattern, self.sections):
            # print('The string is formatted correctly.')
            return True
        else:
            # print('The string is not formatted correctly.')
            return False

    def validate_sections_and_extract_url(self):
        # if self.__valid_sections__:
        #     self.__extract_url__()
        self.__extract_url__()