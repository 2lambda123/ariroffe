import unittest

from logics.classes.predicate import PredicateFormula as Formula
from logics.utils.parsers.predicate_parser import classical_predicate_parser as parser
from logics.instances.predicate.natural_deduction import predicate_classical_natural_deduction_system as nd_system
from logics.classes.predicate.proof_theories.natural_deduction import NaturalDeductionStep, PredicateNaturalDeductionRule
from logics.classes.errors import ErrorCode, CorrectionError

class TestPredicateNaturalDeduction(unittest.TestCase):
    def setUp(self):
        pass

    def test_substitute_rule_intro_rules(self):
        # Existential intro (unary)
        deriv = parser.parse_derivation("""
            P(a); premise; []; []
            ∃x P(x); I∃; [0]; []
        """, natural_deduction=True)
        rule = nd_system.rules['I∃']
        new_rule = nd_system.substitute_rule(deriv, 1, rule)
        # New rule should be Pα / ∃x Px
        self.assertEqual(new_rule, PredicateNaturalDeductionRule([
            '(...)',
            NaturalDeductionStep(Formula(['P', 'α']), open_suppositions=[]),
            '(...)',
            NaturalDeductionStep(Formula(['∃', 'x', ['P', 'x']]), 'I∃', [0], open_suppositions=[])
        ]))

        # Existential intro (binary)
        deriv = parser.parse_derivation("""
            R(b, b); premise; []; []
            ∃x R(x, x); I∃; [0]; []
        """, natural_deduction=True)
        rule = nd_system.rules['I∃']
        new_rule = nd_system.substitute_rule(deriv, 1, rule)
        # New rule should be Rαα / ∃x Rxx
        self.assertEqual(new_rule, PredicateNaturalDeductionRule([
            '(...)',
            NaturalDeductionStep(Formula(['R', 'α', 'α']), open_suppositions=[]),
            '(...)',
            NaturalDeductionStep(Formula(['∃', 'x', ['R', 'x', 'x']]), 'I∃', [0], open_suppositions=[])
        ]))

        # Existential intro (nested)
        deriv = parser.parse_derivation("""
                ∃x R(x, a); premise; []; []
                ∃y ∃x R(x, y); I∃; [0]; []
            """, natural_deduction=True)
        rule = nd_system.rules['I∃']
        new_rule = nd_system.substitute_rule(deriv, 1, rule)
        self.assertEqual(new_rule, PredicateNaturalDeductionRule([
            '(...)',
            NaturalDeductionStep(Formula(['∃', 'x', ['R', 'x', 'α']]), open_suppositions=[]),
            '(...)',
            NaturalDeductionStep(Formula(['∃', 'y', ['∃', 'x', ['R', 'x', 'y']]]), 'I∃', [0], open_suppositions=[])
        ]))

        # Universal intro
        deriv = parser.parse_derivation("""
            R(b, a); premise; []; []
            ∀y R(y, a); I∃; [0]; []
        """, natural_deduction=True)
        rule = nd_system.rules['I∀']
        new_rule = nd_system.substitute_rule(deriv, 1, rule)
        # New rule should be Rαa / ∀y Rya
        self.assertEqual(new_rule, PredicateNaturalDeductionRule([
            '(...)',
            NaturalDeductionStep(Formula(['R', 'α', 'a']), open_suppositions=[]),
            '(...)',
            NaturalDeductionStep(Formula(['∀', 'y', ['R', 'y', 'a']]), 'I∀', [0], open_suppositions=[])
        ], arbitrary_cts=['α']))

    def test_substitute_rule_univ_elim(self):
        # Universal elimination (unary)
        deriv = parser.parse_derivation("""
            ∀x P(x); premise; []; []
            P(a); E∀; [0]; []
        """, natural_deduction=True)
        rule = nd_system.rules['E∀']
        new_rule = nd_system.substitute_rule(deriv, 1, rule)
        # New rule should be ∀x Px / Pα
        self.assertEqual(new_rule, PredicateNaturalDeductionRule([
            '(...)',
            NaturalDeductionStep(Formula(['∀', 'x', ['P', 'x']]), open_suppositions=[]),
            '(...)',
            NaturalDeductionStep(Formula(['P', 'α']), 'E∀', [0], open_suppositions=[]),
        ]))

        # Universal elimination (binary)
        deriv = parser.parse_derivation("""
                ∀x R(x, a); premise; []; []
                R(a, a); E∀; [0]; []
            """, natural_deduction=True)
        rule = nd_system.rules['E∀']
        new_rule = nd_system.substitute_rule(deriv, 1, rule)
        # New rule should be ∀x Rxa / Rαa
        self.assertEqual(new_rule, PredicateNaturalDeductionRule([
            '(...)',
            NaturalDeductionStep(Formula(['∀', 'x', ['R', 'x', 'a']]), open_suppositions=[]),
            '(...)',
            NaturalDeductionStep(Formula(['R', 'α', 'a']), 'E∀', [0], open_suppositions=[]),
        ]))

        deriv = parser.parse_derivation("""
                ∀x R(x, x); premise; []; []
                R(a, a); E∀; [0]; []
            """, natural_deduction=True)
        rule = nd_system.rules['E∀']
        new_rule = nd_system.substitute_rule(deriv, 1, rule)
        # New rule should be ∀x Rxx / Rαα
        self.assertEqual(new_rule, PredicateNaturalDeductionRule([
            '(...)',
            NaturalDeductionStep(Formula(['∀', 'x', ['R', 'x', 'x']]), open_suppositions=[]),
            '(...)',
            NaturalDeductionStep(Formula(['R', 'α', 'α']), 'E∀', [0], open_suppositions=[]),
        ]))

    def test_substitute_rule_exist_elim(self):
        # Existential elimination (unary)
        deriv = parser.parse_derivation("""
            ∃x P(x); premise; []; []
            P(a) → R(b,b); premise; []; []
            R(b, b); E∃; [0, 1]; []
        """, natural_deduction=True)
        rule = nd_system.rules['E∃']
        new_rule = nd_system.substitute_rule(deriv, 2, rule)
        # New rule should be ∃x Px, P(α) → B / B
        self.assertEqual(new_rule, PredicateNaturalDeductionRule([
            '(...)',
            NaturalDeductionStep(Formula(['∃', 'x', ['P', 'x']]), open_suppositions=[]),
            '(...)',
            NaturalDeductionStep(Formula(['→', ['P', 'α'], ['B']]), open_suppositions=[]),
            '(...)',
            NaturalDeductionStep(Formula(['B']), 'E∃', [0, 1], open_suppositions=[]),
        ], arbitrary_cts=['α']))

        # Existential elimination (binary)
        deriv = parser.parse_derivation("""
                ∃x R(x, b); premise; []; []
                R(a, b) → P(c); premise; []; []
                P(c); E∃; [0, 1]; []
            """, natural_deduction=True)
        rule = nd_system.rules['E∃']
        new_rule = nd_system.substitute_rule(deriv, 2, rule)
        # New rule should be ∃x Rxb, R(α,b) → B / B
        self.assertEqual(new_rule, PredicateNaturalDeductionRule([
            '(...)',
            NaturalDeductionStep(Formula(['∃', 'x', ['R', 'x', 'b']]), open_suppositions=[]),
            '(...)',
            NaturalDeductionStep(Formula(['→', ['R', 'α', 'b'], ['B']]), open_suppositions=[]),
            '(...)',
            NaturalDeductionStep(Formula(['B']), 'E∃', [0, 1], open_suppositions=[]),
        ], arbitrary_cts=['α']))

        deriv = parser.parse_derivation("""
                ∃x R(x, x); premise; []; []
                R(a, a) → P(b); premise; []; []
                P(b); E∃; [0, 1]; []
            """, natural_deduction=True)
        rule = nd_system.rules['E∃']
        new_rule = nd_system.substitute_rule(deriv, 2, rule)
        # New rule should be ∃x Rxx, R(α,α) → B / B
        self.assertEqual(new_rule, PredicateNaturalDeductionRule([
            '(...)',
            NaturalDeductionStep(Formula(['∃', 'x', ['R', 'x', 'x']]), open_suppositions=[]),
            '(...)',
            NaturalDeductionStep(Formula(['→', ['R', 'α', 'α'], ['B']]), open_suppositions=[]),
            '(...)',
            NaturalDeductionStep(Formula(['B']), 'E∃', [0, 1], open_suppositions=[]),
        ], arbitrary_cts=['α']))

    def test_is_correct_application_exist_intro(self):
        # Existential intro (unary)
        deriv = parser.parse_derivation("""
                P(a); premise; []; []
                ∃x P(x); I∃; [0]; []
            """, natural_deduction=True)
        self.assertTrue(nd_system.is_correct_application(deriv, 1, nd_system.rules['I∃']))

        # Existential intro (binary)
        deriv = parser.parse_derivation("""
                R(a, b); premise; []; []
                ∃y R(a, y); I∃; [0]; []
            """, natural_deduction=True)
        self.assertTrue(nd_system.is_correct_application(deriv, 1, nd_system.rules['I∃']))

        deriv = parser.parse_derivation("""
                R(a, b); premise; []; []
                ∃x R(x, b); I∃; [0]; []
            """, natural_deduction=True)
        self.assertTrue(nd_system.is_correct_application(deriv, 1, nd_system.rules['I∃']))

        deriv = parser.parse_derivation("""
                R(a, a); premise; []; []
                ∃x R(x, x); I∃; [0]; []
            """, natural_deduction=True)
        self.assertTrue(nd_system.is_correct_application(deriv, 1, nd_system.rules['I∃']))

        deriv = parser.parse_derivation("""
                R(a, b); premise; []; []
                ∃y R(a, x); I∃; [0]; []
            """, natural_deduction=True)
        self.assertFalse(nd_system.is_correct_application(deriv, 1, nd_system.rules['I∃']))

        deriv = parser.parse_derivation("""
                R(a, a); premise; []; []
                ∃x R(x, a); I∃; [0]; []
            """, natural_deduction=True)
        self.assertTrue(nd_system.is_correct_application(deriv, 1, nd_system.rules['I∃']))

        # Nested quantifiers
        deriv = parser.parse_derivation("""
                ∃x R(x, a); premise; []; []
                ∃y ∃x R(x, y); I∃; [0]; []
            """, natural_deduction=True)
        self.assertTrue(nd_system.is_correct_application(deriv, 1, nd_system.rules['I∃']))

    def test_is_correct_application_univ_elim(self):
        deriv = parser.parse_derivation("""
                ∀x P(x); premise; []; []
                P(a); E∀; [0]; []
            """, natural_deduction=True)
        self.assertTrue(nd_system.is_correct_application(deriv, 1, nd_system.rules['E∀']))

        deriv = parser.parse_derivation("""
                ∀x R(x, b); premise; []; []
                R(a, b); E∀; [0]; []
            """, natural_deduction=True)
        self.assertTrue(nd_system.is_correct_application(deriv, 1, nd_system.rules['E∀']))

        deriv = parser.parse_derivation("""
                ∀x R(x, x); premise; []; []
                R(a, a); E∀; [0]; []
            """, natural_deduction=True)
        self.assertTrue(nd_system.is_correct_application(deriv, 1, nd_system.rules['E∀']))

        deriv = parser.parse_derivation("""
                ∀x R(x, x); premise; []; []
                R(a, b); E∀; [0]; []
            """, natural_deduction=True)
        self.assertFalse(nd_system.is_correct_application(deriv, 1, nd_system.rules['E∀']))

    def test_arbitrary_constants_univ_intro(self):
        deriv = parser.parse_derivation("""
                P(a); premise; []; []
                ∀x P(x); I∀; [0]; []
            """, natural_deduction=True)
        rule = nd_system.substitute_rule(deriv, 1, nd_system.rules['I∀'])
        arbitrary, error = nd_system.check_arbitrary_constants(deriv, 1, rule)
        self.assertFalse(arbitrary)
        self.assertEqual(error, CorrectionError(code=ErrorCode.ND_NONARBITRARY_CONSTANT, index=1,
                                                description="Constant 'a' is not arbitrary"))

        deriv = parser.parse_derivation("""
                P(a); DN; []; []
                ∀x P(x); I∀; [0]; []
            """, natural_deduction=True)
        rule = nd_system.substitute_rule(deriv, 1, nd_system.rules['I∀'])
        arbitrary, error = nd_system.check_arbitrary_constants(deriv, 1, rule)
        self.assertTrue(arbitrary)

        deriv = parser.parse_derivation("""
                R(a, a); DN; []; []
                ∀x R(x, x); I∀; [0]; []
            """, natural_deduction=True)
        rule = nd_system.substitute_rule(deriv, 1, nd_system.rules['I∀'])
        arbitrary, error = nd_system.check_arbitrary_constants(deriv, 1, rule)
        self.assertTrue(arbitrary)

        deriv = parser.parse_derivation("""
                R(a, a); DN; []; []
                ∀x R(x, a); I∀; [0]; []
            """, natural_deduction=True)
        rule = nd_system.substitute_rule(deriv, 1, nd_system.rules['I∀'])
        arbitrary, error = nd_system.check_arbitrary_constants(deriv, 1, rule)
        self.assertFalse(arbitrary)
        self.assertEqual(error, CorrectionError(code=ErrorCode.ND_NONARBITRARY_CONSTANT, index=1,
                                                description="Constant 'a' is not arbitrary"))

        deriv = parser.parse_derivation("""
                P(a); supposition; []; [0]
                ∀x P(x); I∀; [0]; [0]
            """, natural_deduction=True)
        rule = nd_system.substitute_rule(deriv, 1, nd_system.rules['I∀'])
        arbitrary, error = nd_system.check_arbitrary_constants(deriv, 1, rule)
        self.assertFalse(arbitrary)
        self.assertEqual(error, CorrectionError(code=ErrorCode.ND_NONARBITRARY_CONSTANT, index=1,
                                                description="Constant 'a' is not arbitrary"))

        deriv = parser.parse_derivation("""
                P(a); supposition; []; [0]
                ∀x P(x); I∀; [0]; []
            """, natural_deduction=True)
        rule = nd_system.substitute_rule(deriv, 1, nd_system.rules['I∀'])
        arbitrary, error = nd_system.check_arbitrary_constants(deriv, 1, rule)
        self.assertTrue(arbitrary)  # because the supposition is closed (incorrectly, but that doesn't matter here)

        # A longer derivation
        deriv = parser.parse_derivation("""
            P(a); premise; []; []
            ∀x R(x, x); premise; []; []
            R(a, a); E∀; [1]; []
            ∀y R(y, y); I∀; [2]; []
        """, natural_deduction=True)
        rule = nd_system.substitute_rule(deriv, 3, nd_system.rules['I∀'])
        arbitrary, error = nd_system.check_arbitrary_constants(deriv, 3, rule)
        self.assertFalse(arbitrary)
        self.assertEqual(error, CorrectionError(code=ErrorCode.ND_NONARBITRARY_CONSTANT, index=3,
                                                description="Constant 'a' is not arbitrary"))

    def test_arbitrary_constants_exist_elim(self):
        deriv = parser.parse_derivation("""
                ∃x P(x); premise; []; []
                P(a) → R(b, b); premise; []; []
                R(b, b); E∃; [0, 1]; []
            """, natural_deduction=True)
        rule = nd_system.substitute_rule(deriv, 2, nd_system.rules['E∃'])
        arbitrary, error = nd_system.check_arbitrary_constants(deriv, 2, rule)
        self.assertFalse(arbitrary)
        self.assertEqual(error, CorrectionError(code=ErrorCode.ND_NONARBITRARY_CONSTANT, index=2,
                                                description="Constant 'a' is not arbitrary"))

        deriv = parser.parse_derivation("""
                ∃x P(x); premise; []; []
                P(a) → R(b, b); DN; []; []
                R(b, b); E∃; [0, 1]; []
            """, natural_deduction=True)
        rule = nd_system.substitute_rule(deriv, 2, nd_system.rules['E∃'])
        arbitrary, error = nd_system.check_arbitrary_constants(deriv, 2, rule)
        self.assertTrue(arbitrary)

        deriv = parser.parse_derivation("""
                ∃x P(x); premise; []; []
                P(a) → R(a, b); DN; []; []
                R(a, b); E∃; [0, 1]; []
            """, natural_deduction=True)
        rule = nd_system.substitute_rule(deriv, 2, nd_system.rules['E∃'])
        arbitrary, error = nd_system.check_arbitrary_constants(deriv, 2, rule)
        self.assertFalse(arbitrary)
        self.assertEqual(error, CorrectionError(code=ErrorCode.ND_NONARBITRARY_CONSTANT, index=2,
                                                description="Constant 'a' is not arbitrary"))

        deriv = parser.parse_derivation("""
                ∃x P(x); premise; []; []
                P(a) → R(a, b); DN; []; []
                R(a, b); E∃; [0, 1]; []
            """, natural_deduction=True)
        rule = nd_system.substitute_rule(deriv, 2, nd_system.rules['E∃'])
        arbitrary, error = nd_system.check_arbitrary_constants(deriv, 2, rule)
        self.assertFalse(arbitrary)
        self.assertEqual(error, CorrectionError(code=ErrorCode.ND_NONARBITRARY_CONSTANT, index=2,
                                                description="Constant 'a' is not arbitrary"))

        deriv = parser.parse_derivation("""
                ∃x R(x, a); DN; []; []
                R(a, a) → P(b); DN; []; []
                P(b); E∃; [0, 1]; []
            """, natural_deduction=True)
        rule = nd_system.substitute_rule(deriv, 2, nd_system.rules['E∃'])
        arbitrary, error = nd_system.check_arbitrary_constants(deriv, 2, rule)
        self.assertFalse(arbitrary)
        self.assertEqual(error, CorrectionError(code=ErrorCode.ND_NONARBITRARY_CONSTANT, index=2,
                                                description="Constant 'a' is not arbitrary"))

    def test_is_correct_derivation(self):
        # Let's try one with the easy rules first
        deriv = parser.parse_derivation("""
                ∀x R(x, x); premise; []; []
                R(a, a); E∀; [0]; []
                ∃x R(x, a); I∃; [1]; []
                ∃y ∃x R(x, y); I∃; [2]; []
            """, natural_deduction=True)
        self.assertTrue(nd_system.is_correct_derivation(deriv))

        # Now a couple of incorrect ones
        deriv = parser.parse_derivation("""
                ∀x R(x, x); premise; []; []
                R(a, b); E∀; [0]; []
                ∃x R(x, b); I∃; [1]; []
                ∃y ∃x R(x, y); I∃; [2]; []
            """, natural_deduction=True)
        correct, error = nd_system.is_correct_derivation(deriv, return_error_list=True)
        self.assertFalse(correct)

        deriv = parser.parse_derivation("""
                ∀x R(x, x); premise; []; []
                R(a, a); E∀; [0]; []
                ∃x R(x, a); I∃; [1]; []
                ∃y ∃x R(y, x); I∃; [2]; []
            """, natural_deduction=True)
        correct, error = nd_system.is_correct_derivation(deriv, return_error_list=True)
        self.assertFalse(correct)

        # A couple with univ intro
        deriv = parser.parse_derivation("""
            ∀x R(x, x); premise; []; []
            R(a, a); E∀; [0]; []
            ∀y R(y, y); I∀; [1]; []
        """, natural_deduction=True)
        self.assertTrue(nd_system.is_correct_derivation(deriv))

        deriv = parser.parse_derivation("""
            P(a); premise; []; []
            ∀x R(x, x); premise; []; []
            R(a, a); E∀; [1]; []
            ∀y R(y, y); I∀; [2]; []
        """, natural_deduction=True)
        correct, error = nd_system.is_correct_derivation(deriv, return_error_list=True)
        self.assertFalse(correct)
        self.assertEqual(error, [CorrectionError(code=ErrorCode.ND_NONARBITRARY_CONSTANT, index=3,
                                                description="Constant 'a' is not arbitrary")])

        deriv = parser.parse_derivation("""
                ∀x R(x, a); premise; []; []
                R(a, a); E∀; [0]; []
                ∀y R(y, y); I∀; [1]; []
            """, natural_deduction=True)
        correct, error = nd_system.is_correct_derivation(deriv, return_error_list=True)
        self.assertFalse(correct)
        self.assertEqual(error, [CorrectionError(code=ErrorCode.ND_NONARBITRARY_CONSTANT, index=2,
                                                description="Constant 'a' is not arbitrary")])

        deriv = parser.parse_derivation("""
                ∀x R(x, a); premise; []; []
                R(b, a); E∀; [0]; []
                ∀y R(y, a); I∀; [1]; []
            """, natural_deduction=True)
        self.assertTrue(nd_system.is_correct_derivation(deriv))

        # A couple with exist elim
        deriv = parser.parse_derivation("""
                ∃x R(x, x); premise; []; []
                R(a, a); supposition; []; [1]
                ∃y R(y, y); I∃; [1]; [1]
                R(a, a) → ∃y R(y, y); I→; [1,2]; []
                ∃y R(y, y); E∃; [0, 3]; []
            """, natural_deduction=True)
        self.assertTrue(nd_system.is_correct_derivation(deriv))

        deriv = parser.parse_derivation("""
                ∃x R(x, x); premise; []; []
                R(a, a); supposition; []; [1]
                ∃y R(y, a); I∃; [1]; [1]
                R(a, a) → ∃y R(y, a); I→; [1,2]; []
                ∃y R(y, a); E∃; [0, 3]; []
            """, natural_deduction=True)
        correct, error = nd_system.is_correct_derivation(deriv, return_error_list=True)
        self.assertFalse(correct)
        self.assertEqual(error, [CorrectionError(code=ErrorCode.ND_NONARBITRARY_CONSTANT, index=4,
                                                description="Constant 'a' is not arbitrary")])
