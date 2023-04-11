from typing import List

from cript.exceptions import CRIPTException


class CRIPTConnectionError(CRIPTException):
    """
    Raised when the API object cannot connect to CRIPT with the given host and token
    """

    def __init__(self, host, token):
        self.host = host
        # Do not store full token in stack trace for security reasons
        uncovered_chars = len(token) // 4
        self.token = token[:uncovered_chars]
        self.token += "*" * (len(token) - 2 * uncovered_chars)
        self.token += token[-uncovered_chars:]

    def __str__(self) -> str:
        """

        Returns
        -------
        str
            Explanation of the error
        """

        ret_str = f"Could not connect to CRIPT with the given host ({self.host}) and token ({self.token})."
        ret_str += " Please be sure both host and token are entered correctly."
        return ret_str


class InvalidVocabulary(CRIPTException):
    """
    Raised when the CRIPT controlled vocabulary is invalid
    """

    def __init__(self, vocab: str, possible_vocab: List[str]):
        self.vocab
        self.possible_vocab

    def __str__(self) -> str:
        ret_str = f"The vocabulary '{self.vocab}' entered does not exist within the CRIPT controlled vocabulary."
        ret_str += f" Please pick a valid CRIPT vocabulary from {self.possible_vocab}"
        return ret_str


class InvalidVocabularyCategory(CRIPTException):
    """
    Raised when the CRIPT controlled vocabulary category is unknow
    """

    def __init__(self, vocab_category: str, valid_vocab_category: List[str]):
        self.vocab_category = vocab_category
        self.valid_vocab_category = valid_vocab_category

    def __str__(self) -> str:
        ret_str = f"The vocabulary category '{self.vocab_category}' does not exist within the CRIPT controlled vocabulary."
        ret_str += f" Please pick a valid CRIPT vocabulary category from {self.valid_vocab_category}."
        return ret_str


class CRIPTAPIAccessError(CRIPTException):
    """
    Exception to be raise when the cached API object is requested, but no cached API exists yet.
    """

    def __init__(self):
        pass

    def __str__(self) -> str:
        ret_str = "An operation you requested (see stack trace) requires that you "
        ret_str += " connect to a CRIPT host via an cript.API object first.\n"
        ret_str += "This is common for node creation, validation and modification.\n"
        ret_str += "It is necessary that you connect with the API via a context manager like this:\n"
        ret_str += "`with cript.API('https://criptapp.org/', secret_token) as api:\n"
        ret_str += "\t# code that use the API object explicitly (`api.save(..)`) or implicitly (`cript.Experiment(...)`)."
        ret_str += "See documentation of cript.API for more details."
        return ret_str