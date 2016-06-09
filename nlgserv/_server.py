# First we add simple nlg to the path
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "simplenlg.jar"))

# Bottle will handle the HTTP side of things
from bottle import route, run, request, response

# SimpleNLG will do the NLG generation
from simplenlg.framework import NLGFactory, CoordinatedPhraseElement, ListElement, PhraseElement
from simplenlg.lexicon import Lexicon
from simplenlg.realiser.english import Realiser
from simplenlg.features import Feature, Tense, NumberAgreement
from simplenlg.phrasespec import NPPhraseSpec

from java.lang import Boolean

# We only need one instance of these, so we'll create them globally.
lexicon = Lexicon.getDefaultLexicon()
nlgFactory = NLGFactory(lexicon)
realiser = Realiser(lexicon)

bools = {"true": Boolean(True), "false": Boolean(False)}
tense_values = {"past": Tense.PAST, "present": Tense.PRESENT, "future": Tense.FUTURE}
number_values = {"singular": NumberAgreement.SINGULAR, "plural": NumberAgreement.PLURAL}

features = {
    "tense": {"feature": Feature.TENSE, "values": tense_values},
    "number": {"feature": Feature.NUMBER, "values": number_values},
    "passive": {"feature": Feature.PASSIVE, "values": bools},
    "perfect": {"feature": Feature.PERFECT, "values": bools},
    "cue_phrase": {"feature": Feature.CUE_PHRASE},
    "complementiser": {"feature": Feature.COMPLEMENTISER},
    "conjunction": {"feature": Feature.CONJUNCTION}
}

def process_features(element, f_spec):
    for feature, value in f_spec.items():
        if feature in ['tense', 'number', 'passive', 'perfect']:
            try:
                feature_value = features[feature]["values"][value]
            except AttributeError as e:
                valid_values = list(features[feature]["values"].values())
                raise Exception("Unrecognised %s: %s. Can only be %s" % (feature, value, valid_values))
        elif feature in ['cue_phrase', 'complementiser']:
            feature_value = value
        else:
            raise Exception("Unrecognised feature: %s" % (feature,))
        element.setFeature(features[feature]["feature"], feature_value)

generic_processor = lambda func, parent, item_or_list: [func(expand_element(item)) for item in item_or_list] if isinstance(item_or_list, collections.Iterable) else func(expand_element(item_or_list))

function_mapping = {
    "determiner": "setDeterminer",
    "subject": "setSubject",
    "object": "setObject",
    "indirect_object": "setIndirectObject",
    "verb": "setVerb",
    "preposition": "setPreposition",
    "coordinates": "addCoordinate",
    "complements": "addComplement",
    "modifiers": "addModifier",
    "pre-modifiers": "addPreModifier",
    "post-modifiers": "addPostModifier"
}

generic_processor = lambda func, parent, item_or_list: [func(expand_element(item)) for item in item_or_list] if type(item_or_list) is list else func(expand_element(item_or_list))

processors = {
    "determiner": lambda parent, item_or_list: generic_processor(getattr(parent, function_mapping["determiner"]), parent, item_or_list),
    "subject": lambda parent, item_or_list: generic_processor(getattr(parent, function_mapping["subject"]), parent, item_or_list),
    "object": lambda parent, item_or_list: generic_processor(getattr(parent, function_mapping["object"]), parent, item_or_list),
    "indirect_object": lambda parent, item_or_list: generic_processor(getattr(parent, function_mapping["indirect_object"]), parent, item_or_list),
    "verb": lambda parent, item_or_list: generic_processor(getattr(parent, function_mapping["verb"]), parent, item_or_list),
    "preposition": lambda parent, item_or_list: generic_processor(getattr(parent, function_mapping["preposition"]), parent, item_or_list),
    "coordinates": lambda parent, item_or_list: generic_processor(getattr(parent, function_mapping["coordinates"]), parent, item_or_list),
    "complements": lambda parent, item_or_list: generic_processor(getattr(parent, function_mapping["complements"]), parent, item_or_list),
    "modifiers": lambda parent, item_or_list: generic_processor(getattr(parent, function_mapping["modifiers"]), parent, item_or_list),
    "pre-modifiers": lambda parent, item_or_list: generic_processor(getattr(parent, function_mapping["pre-modifiers"]), parent, item_or_list),
    "post-modifiers": lambda parent, item_or_list: generic_processor(getattr(parent, function_mapping["post-modifiers"]), parent, item_or_list),

    "features": process_features,
}

# processors = {
#     "determiner": lambda parent, x: parent.setDeterminer(expand_element(x)),
#     "subject": lambda parent, x: parent.setSubject(expand_element(x)),
#     "object": lambda parent, x: parent.setObject(expand_element(x)),
#     "indirect_object": lambda parent, x: parent.setIndirectObject(expand_element(x)),
#     "verb": lambda parent, x: [parent.setVerb(expand_element(i)) for i in x] if type(x) is list else parent.setVerb(expand_element(x)),
#     "preposition": lambda parent, x: [parent.setPreposition(expand_element(i)) for i in x] if type(x) is list else parent.setPreposition(expand_element(x)),
#     "coordinates": lambda parent, x: [parent.addCoordinate(expand_element(i)) for i in x] if type(x) is list else parent.addCoordinate(expand_element(x)),
#     "complements": lambda parent, x: [parent.addComplement(expand_element(i)) for i in x] if type(x) is list else parent.addComplement(expand_element(x)),
#     "modifiers": lambda parent, x: [parent.addModifier(expand_element(i)) for i in x] if type(x) is list else parent.addModifier(expand_element(x)),
#     "pre-modifiers": lambda parent, x: [parent.addPreModifier(expand_element(i)) for i in x] if type(x) is list else parent.addPreModifier(expand_element(x)),
#     "post-modifiers": lambda parent, x: [parent.addPostModifier(expand_element(i)) for i in x] if type(x) is list else parent.addPostModifier(expand_element(x)),

#     "features": process_features,
# }


@route('/generateSentence', method="POST")
def process_generate_sentence_request():
    # try:
    return realiser.realiseSentence(generate_sentence(request.json))
    # except Exception as e:
    #     print(e)
    #     response.status = 500
    #     return str(e)

def generate_sentence(json_request):
    sentence = nlgFactory.createClause() # All sentences have at least one clause.

    if "sentence" not in json_request:
        raise Exception("Request must contain a 'sentence' object.")

    s_spec = json_request["sentence"]

    for keyword in ['subject', 'object', 'indirect_object', 'verb', 'complements', 'modifiers', 'features']:
        if keyword not in s_spec: continue
        process = processors[keyword]
        process(sentence, s_spec[keyword])

    return sentence # We need to realise as a sentence to get punctuation

def expand_element(elem):
    if type(elem)==unicode or type(elem) == NPPhraseSpec:
        # If the element is a unicode string, then it is as expanded as possible.
        return elem
    else:
        if "type" not in elem:

            raise Exception("Elements must have a type.")

        elif elem["type"] == "clause":

            return generate_sentence({"sentence":elem["spec"]})

        elif elem["type"] == "noun_phrase":

            element = nlgFactory.createNounPhrase()
            element.setNoun(elem["head"])
            for keyword in ['determiner', 'modifiers', 'pre-modifiers', 'post-modifiers', 'complements']:
                if keyword not in elem: continue
                processors[keyword](element, elem[keyword])
            
            return element

        elif elem["type"] == "verb_phrase":

            element = nlgFactory.createVerbPhrase()
            element.setVerb(elem["head"])
            for keyword in ['features', 'modifiers', 'pre-modifiers', 'post-modifiers']:
                if keyword not in elem: continue
                processors[keyword](element, elem[keyword])
            return element

        elif elem["type"] == "preposition_phrase":

            prepPhrase = nlgFactory.createPrepositionPhrase()
            if "noun" not in elem:
                raise Exception("Preposition phrases must have a noun.")
            nounPhrase = expand_element(elem["noun"])
            if "preposition" not in elem:
                raise Exception("Preposition phrases must have a preposition.")
            processors['complements'](prepPhrase, nounPhrase)
            processors['preposition'](prepPhrase, elem["preposition"])
            return prepPhrase

        elif elem["type"] == "coordinated_phrase":

            coordPhrase = nlgFactory.createCoordinatedPhrase()
            if "coordinates" not in elem:
                raise Exception("Coordinated phrases must have coordinates.")
            for coord in elem["coordinates"]:
                processors['coordinates'](coordPhrase, coord)
            if "conjunction" in elem:
                coordPhrase.setFeature(features["conjunction"]["feature"], elem["conjunction"])
            return coordPhrase

        else:
            raise Exception("The type is unrecognised: %s" % (elem["type"],))

if __name__=="__main__":
    host = sys.argv[1]
    port = int(sys.argv[2])
    print("Starting to run on %s, port %s" % (host, port))
    run(host=host, port=port)
