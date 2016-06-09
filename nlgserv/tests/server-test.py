#!/usr/bin/python

import unittest
import subprocess
from time import sleep
import json
import os

try:
    # For Python 3.0 and later
    from urllib.request import urlopen
    from urllib.request import Request
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen
    from urllib2 import Request

nlgserv = None

def setUpModule():
    global nlgserv
    print("Starting up nlgserv...")
    nlgserv = subprocess.Popen(["java", "-jar",
                               os.path.join(os.path.dirname(__file__),"../jython.jar"), os.path.join(os.path.dirname(__file__), "../_server.py"), "localhost", "8080"],
                               stdin=subprocess.PIPE,
                               stdout=open(os.path.join(os.path.dirname(__file__), "nlgserv.stdout.log"), "w+"),
                               stderr=open(os.path.join(os.path.dirname(__file__), "nlgserv.stderr.log"), "w+"),
                               preexec_fn=os.setsid)
    # sleep(60) # It needs longer now it's loading from the standalone package...
    print("Commencing testing...")
    
def tearDownModule():
    global nlgserv
    print("Shutting down nlgserv...")
    os.killpg(nlgserv.pid, subprocess.signal.SIGTERM)
    nlgserv.wait()
    

def send_data(json_data):
    req = Request("http://localhost:8080/generateSentence",
                          data=json_data.encode('utf-8'),
                          headers={"Content-Type":"application/json"})
    return urlopen(req).read()

class TestCake(unittest.TestCase):
    def test(self):
        self.assertEqual(send_data(open(os.path.join(os.path.dirname(__file__), "fixtures/cake.json"),"r").read()), "John baked a cake from some ingredients.")
        
class TestIngredients(unittest.TestCase):
    def test(self):
        self.assertEqual(send_data(open(os.path.join(os.path.dirname(__file__), "fixtures/ingredients.json"),"r").read()), "The ingredients were flour, sugar, butter and eggs.")

class TestTense(unittest.TestCase):
    def test(self):
        sentence = {}
        sentence["subject"] = "John"
        sentence["verb"] = "kick"
        sentence["object"] = "Dave"

        sentence["features"] = {"tense":"past"}
        self.assertEqual(send_data(json.dumps({"sentence":sentence})), "John kicked Dave.")

        sentence["features"] = {"tense":"present"}
        self.assertEqual(send_data(json.dumps({"sentence":sentence})), "John kicks Dave.")
        
        sentence["features"] = {"tense":"future"}
        self.assertEqual(send_data(json.dumps({"sentence":sentence})), "John will kick Dave.")

class TestPassive(unittest.TestCase):
    def test_present(self):
        sentence = {}
        sentence["subject"] = "John"
        sentence["verb"] = "kick"
        sentence["object"] = "Dave"

        sentence["features"] = {"passive":"false"}
        self.assertEqual(send_data(json.dumps({"sentence":sentence})), "John kicks Dave.")

        sentence["features"] = {"passive":"true"}
        self.assertEqual(send_data(json.dumps({"sentence":sentence})), "Dave is kicked by John.")

class TestPerfect(unittest.TestCase):
    def test_present(self):
        sentence = {}
        sentence["subject"] = "John"
        sentence["verb"] = "kick"
        sentence["object"] = "Dave"

        sentence["features"] = {"perfect":"false"}
        self.assertEqual(send_data(json.dumps({"sentence":sentence})), "John kicks Dave.")

        sentence["features"] = {"perfect":"true"}
        self.assertEqual(send_data(json.dumps({"sentence":sentence})), "John has kicked Dave.")

        sentence["features"]["tense"] = "past"
        self.assertEqual(send_data(json.dumps({"sentence":sentence})), "John had kicked Dave.")

class TestCuePhrase(unittest.TestCase):
    def test_however(self):
        sentence = {}
        sentence["subject"] = "John"
        sentence["verb"] = "kick"
        sentence["object"] = "Dave"

        self.assertEqual(send_data(json.dumps({"sentence":sentence})), "John kicks Dave.")
        
        sentence["features"] = {"cue_phrase":"however"}
        self.assertEqual(send_data(json.dumps({"sentence":sentence})), "However John kicks Dave.")

class TestComplementClauses(unittest.TestCase):
    def test_clauses(self):
        sentence_a = {}
        sentence_a["subject"] = "Mary"
        sentence_a["verb"] = "love"
        sentence_a["object"] = "John"

        sentence_b = {}
        sentence_b["subject"] = "he"
        sentence_b["verb"] = "buy"
        sentence_b["indirect_object"] = "she"
        sentence_b["object"] = {"type": "noun_phrase",
                                "head": "flower",
                                "features": {"number": "plural"}}
        sentence_b["features"] = {"tense":"past",
                                  "complementiser":"because"}

        self.assertEqual(send_data(json.dumps({"sentence":sentence_a})), "Mary loves John.")
        self.assertEqual(send_data(json.dumps({"sentence":sentence_b})), "He bought her flowers.")

        sentence_a["complements"] = [{"type": "clause",
                                      "spec": sentence_b}]

        self.assertEqual(send_data(json.dumps({"sentence":sentence_a})), "Mary loves John because he bought her flowers.")
