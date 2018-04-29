from unittest import TestCase
from VSMSimilarityCalculator import VSMSimilarityCalculator

class TestVSMSimilarityCalculator(TestCase):
    def test_calculate(self):
        documents = [
            "This is a test for VSM similarity",
            "This is a for ",
            "This is a test for VSM ",
            "This is a test for VSM similarity",
            "This is a test for VSM similarity. This is a test for VSM similarity.",
            "test VSM similarity. test VSM similarity.",
            "I'm trying to create a completely different string",
            "This result should be different",
            "similarity"
        ]
        vsm_similarity_calculator = VSMSimilarityCalculator()
        result = vsm_similarity_calculator.calculate(documents[0],documents[1:])
        self.assertEqual([0.0, 0.816496580927726, 1.0, 1.0, 1.0, 0.0, 0.0, 0.5773502691896257],result)


