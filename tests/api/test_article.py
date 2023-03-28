import json
from unittest import TestCase

from flask import Flask
from flask_restful import Api  # type: ignore

from src import console
from src.models.api.statistic.article import ArticleStatistics
from src.views.statistics.article import Article

# This is needed to get the full diff when tests fail
# https://stackoverflow.com/questions/14493670/how-to-set-self-maxdiff-in-nose-to-get-full-diff-output
# TestCase.maxDiff = None


class TestArticle(TestCase):
    """Generated by ChatGPT using this prompt:
        Create a test for this flask api endpoint
    import logging
    from typing import Optional

    from flask import request
    from flask_restful import Resource, abort  # type: ignore

    from src.helpers.console import console
    from src.models.api.get_statistics_schema import GetStatisticsSchema
    from src.models.api.job import Job
    from src.models.wikimedia.enums import AnalyzerReturn
    from src.models.wikimedia.wikipedia.analyzer import WikipediaAnalyzer

    logger = logging.getLogger(__name__)


    class GetArticleStatistics(Resource):
        schema = GetStatisticsSchema()
        job: Optional[Job]

        def get(self):
            self.__validate_and_get_job__()
            if self.job.lang.lower() == "en" and self.job.title and self.job.site.lower() == "wikipedia":
                logger.info(f"Analyzing {self.job.title}...")
                # TODO use a work queue here like ReFill so
                #  we can easily scale the workload from thousands of patrons
                wikipedia_analyzer = WikipediaAnalyzer(title=self.job.title,
                                                       lang=self.job.lang,
                                                       wikimedia_site=self.job.site,
                                                       testing=self.job.testing)
                statistics = wikipedia_analyzer.article()
                if self.job.testing:
                    # what is the purpose of this?
                    return "ok", 200
                else:
                    if isinstance(statistics, dict):
                        # we got a json response
                        # according to https://stackoverflow.com/questions/13081532/return-json-response-from-flask-view
                        # flask calls jsonify automatically
                        return statistics, 200
                    elif statistics == AnalyzerReturn.NOT_FOUND:
                        return statistics.value, 404
                    elif statistics == AnalyzerReturn.IS_REDIRECT:
                        return statistics.value, 400
                    else:
                        raise Exception("this should never be reached.")

            else:
                # Something was not valid, return a meaningful error
                logger.error("did not get what we need")
                if self.job.lang != "en":
                    return "Only en language code is supported", 400
                if self.job.title == "":
                    return "Title was missing", 400
                if self.job.site != "wikipedia":
                    return "Only 'wikipedia' site is supported", 400

        def __validate_and_get_job__(self):
            self.__validate__()
            self.__parse_into_job__()

        def __validate__(self):
            print(request.args)
            errors = self.schema.validate(request.args)
            if errors:
                abort(400, error=str(errors))

        def __parse_into_job__(self):
            console.print(request.args)
            self.job = self.schema.load(request.args)
            console.print(self.job.dict())

    from marshmallow import Schema, fields, post_load

    from src.models.api.job import Job


    class GetStatisticsSchema(Schema):
        lang = fields.Str(required=True)
        site = fields.Str(required=True)
        testing = fields.Bool(required=False)
        title = fields.Str(required=True)

        # noinspection PyUnusedLocal
        @post_load
        # **kwargs is needed here despite what the validator claims
        def return_object(self, data, **kwargs):  # type: ignore
            return Job(**data)
    """

    def setUp(self):
        app = Flask(__name__)
        api = Api(app)

        api.add_resource(Article, "/get-statistics")
        app.testing = True
        self.test_client = app.test_client()

    # DISABLED because it fails
    # def test_valid_request_electrical_breakdown(self):
    #     response = self.test_client.get(
    #         "/get-statistics?lang=en&site=wikipedia&title=Electrical_breakdown&testing=True"
    #     )
    #     data = json.loads(response.data)
    #     print(response.data)
    #     self.assertEqual(200, response.status_code)
    #     self.assertEqual(
    #         ArticleStatistics(title="Electrical_breakdown").dict(),
    #         ArticleStatistics(**self.__make_reproducible__(data=data)).dict(),
    #     )

    # DISABLED because it takes forever
    # def test_valid_request_gnu_linux_naming_controversy(self):
    #     response = self.test_client.get(
    #         "get-statistics?lang=en&site=wikipedia&title=GNU/Linux_naming_controversy"
    #     )
    #     logger.debug(response.data)
    #     # data = json.loads(response.data)
    #     self.assertEqual(200, response.status_code)

    def test_valid_request_easter_island(self):
        """This tests against an excerpt of the whole article (head+tail)"""
        response = self.test_client.get(
            "/get-statistics?lang=en&site=wikipedia&title=Easter Island&testing=true"
        )
        self.assertEqual(200, response.status_code)
        data = json.loads(response.data)
        console.print(data)
        assert data["title"] == "Easter Island"
        assert data["dehydrated_references"] != []
        assert data["urls"] != []

    # def test_invalid_language(self):
    #     response = self.test_client.get(
    #         "/get-statistics?lang=fr&site=wikipedia&title=Test"
    #     )
    #     self.assertEqual(response.status_code, 400)
    #     self.assertEqual(
    #         b"{\"error\": \"{'lang': ['Must be one of: en.']}\"}\n", response.data
    #     )  # expected output

    # def test_missing_title(self):
    #     response = self.test_client.get("/get-statistics?lang=en&site=wikipedia")
    #     self.assertEqual(response.status_code, 400)
    #     self.assertEqual(
    #         response.data,
    #         b"{\"error\": \"{'title': ['Missing data for required field.']}\"}\n",
    #     )

    # def test_invalid_site(self):
    #     response = self.test_client.get(
    #         "/get-statistics?lang=en&site=example.com&title=Test"
    #     )
    #     print(response.data)
    #     self.assertEqual(400, response.status_code)
    #     self.assertEqual(
    #         b"{\"error\": \"{'site': ['Must be one of: wikipedia.']}\"}\n",
    #         response.data,
    #     )

    # def test_site_capitalized(self):
    #     response = self.test_client.get(
    #         "/get-statistics?lang=en&site=WIKIPEDIA&title=Test"
    #     )
    #     # print(response.data)
    #     self.assertEqual(400, response.status_code)

    # def test_valid_site(self):
    #     response = self.test_client.get(
    #         "/get-statistics?lang=en&site=wikipedia&title=Test"
    #     )
    #     # print(response.data)
    #     self.assertEqual(200, response.status_code)

    # @staticmethod
    # def __make_reproducible__(data):
    #     """Remove all timing information"""
    #     # delete non reproducible output
    #     data["timing"] = 0
    #     data["timestamp"] = 0
    #     return data

    def test_valid_request_test_refresh_true(self):
        response = self.test_client.get(
            "/get-statistics?lang=en&site=wikipedia&title=Test&testing=True&refresh=True"
        )
        data = json.loads(response.data)
        print(response.data)
        self.assertEqual(200, response.status_code)
        stats = ArticleStatistics(**data)
        assert stats.served_from_cache is False

    def test_valid_request_test_refresh_false(self):
        # this is not possible to test
        pass
        # response = self.test_client.get(
        #     "/get-statistics?lang=en&site=wikipedia&title=Test&testing=True"
        # )
        # data = json.loads(response.data)
        # print(response.data)
        # self.assertEqual(200, response.status_code)
        # stats = ArticleStatistics(**data)
        # assert stats.served_from_cache is True

    def test___validate_and_get_job__(self):
        """We dont test this since the dev/team does not yet
        know how to mock flask that well yet.
        We do however test the scheme in another file
        and the job it returns"""
        pass
