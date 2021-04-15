from gingerit.gingerit import GingerIt
import urllib.parse

parser = GingerIt()


def ginger_check_sentence(sentence):
    """Corrects spelling and grammar mistakes based on the context of complete sentences.

    Args:
        sentence ([string]): Sentence with a possible mistake 

    Returns:
        [(bool, string)]: True/False and corrected sentence
    """
    sentence = urllib.parse.unquote_plus(sentence)
    result = parser.parse(sentence)
    result_change = result["result"]
    changed = bool(len(result["corrections"])) and (
        sentence.lower() != result_change.lower())
    return {"need_change": changed, "result": result_change}
