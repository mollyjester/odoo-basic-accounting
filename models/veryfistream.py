from veryfi import Client
import base64


class VeryfiClient(Client):
    def process_document_base64(
        self,
        document_b64,
        file_name: str,
        categories: list = None,
        delete_after_processing: bool = False,
        **kwargs: dict,
    ):
        """
        Process a document and extract all the fields from it
        :param document_b64: Contents of the file in BASE64 format
        :param file_name: Name of the file
        :param categories: List of categories Veryfi can use to categorize the document
        :param delete_after_processing: Delete this document from Veryfi after data has been extracted
        :param kwargs: Additional request parameters

        :return: Data extracted from the document
        """
        endpoint_name = "/documents/"
        if not categories:
            categories = self.CATEGORIES
        # base64_encoded_string = base64.b64encode(document).decode("utf-8")
        request_arguments = {
            "file_name": file_name,
            "file_data": document_b64,
            "categories": categories,
            "auto_delete": delete_after_processing,
        }
        request_arguments.update(kwargs)
        document_b64 = self._request("POST", endpoint_name, request_arguments)
        return document_b64
