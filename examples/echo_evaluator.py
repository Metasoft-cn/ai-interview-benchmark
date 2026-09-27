"""Example evaluator adapter.

A real evaluator reads {question, answer} and returns {score, feedback, cited_evidence}.
This echo adapter returns a neutral score for demonstration. Run it as a subprocess
or import and call `evaluate`.
"""
import json
import sys


def evaluate(question, answer):
    return {"score": 60.0, "feedback": "echo adapter", "cited_evidence": []}


if __name__ == "__main__":
    for line in sys.stdin:
        req = json.loads(line)
        resp = evaluate(req["question"], req["answer"])
        sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
        sys.stdout.flush()
