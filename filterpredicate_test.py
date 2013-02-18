import unittest
from filterpredicate import Item, Lexer, Parser, ParsingError


def test_predicate(predicate, text, project=None):
    lexer = Lexer(predicate)
    parser = Parser(lexer)
    predicate = parser.parse()
    return predicate.test(Item(text, project))


def test_parse(predicate):
    Parser(Lexer("@done @wone")).parse()


class FilterPredicateTest(unittest.TestCase):
    def test_parsing_error(self):
        self.assertRaises(ParsingError, test_parse, "@done @wone")
        self.assertRaises(ParsingError, test_parse, "not")

    def test_word_search(self):
        self.assertTrue(test_predicate("test", "dsftest fdsf"))
        self.assertTrue(test_predicate("test test2", "dsftest test2fdsf"))

        self.assertFalse(test_predicate("test", "dsf tet fdsf"))

    def test_simple_tag_search(self):
        self.assertTrue(test_predicate("@test", "dsf @test fdsf"))
        self.assertTrue(test_predicate("@test", "@test fdsf"))
        self.assertTrue(test_predicate("@test", " f f fdsf @test"))

        self.assertFalse(test_predicate("@test", "dsf tet fdsf"))
        self.assertFalse(test_predicate("@test", "dsf@test fdsf"))

    def test_tag_search_with_parameters_eq(self):
        self.assertTrue(test_predicate("@test=1", "dsf @test(1) fdsf"))

        self.assertFalse(test_predicate("@test = 1", "dsf @test(2) fdsf"))
        self.assertFalse(test_predicate("@test = 1", "- dsf @test fdsf"))
        self.assertFalse(test_predicate("@test = 1", "- dsf @test(1)fdsf"))

    def test_tag_search_with_parameters_neq(self):
        self.assertTrue(test_predicate("@test!=1", "dsf @test(2) fdsf"))
        self.assertTrue(test_predicate("@test != 1", "- dsf @test fdsf"))

        self.assertFalse(test_predicate("@test != 1", "dsf @test(1) fdsf"))

    def test_tag_search_with_parameters_lt(self):
        self.assertTrue(test_predicate("@test<3", "dsf @test(2) fdsf"))
        self.assertTrue(test_predicate("@test < 1", "- dsf @test fdsf"))

        self.assertFalse(test_predicate("@test < 1", "dsf @test(3) fdsf"))

    def test_tag_search_with_parameters_lte(self):
        self.assertTrue(test_predicate("@test<=3", "dsf @test(3) fdsf"))
        self.assertTrue(test_predicate("@test <= 1", "- dsf @test fdsf"))

        self.assertFalse(test_predicate("@test <= 1", "dsf @test(2) fdsf"))

    def test_tag_search_with_parameters_gt(self):
        self.assertTrue(test_predicate("@test>1", "dsf @test(3) fdsf"))

        self.assertFalse(test_predicate("@test > 3", "dsf @test(2) fdsf"))
        self.assertFalse(test_predicate("@test > 1", "- dsf @test fdsf"))

    def test_tag_search_with_parameters_gte(self):
        self.assertTrue(test_predicate("@test>=1", "dsf @test(1) fdsf"))

        self.assertFalse(test_predicate("@test >= 3", "dsf @test(2) fdsf"))
        self.assertFalse(test_predicate("@test >= 1", "- dsf @test fdsf"))

    def test_predicate_with_and(self):
        self.assertTrue(test_predicate("test and unit", "dsf test fdsfunit"))
        self.assertTrue(test_predicate("@test and unit", "dsf @test fdsfunit"))

        self.assertFalse(test_predicate("test and unit", "dsf test fdsf"))
        self.assertFalse(test_predicate("test and unit", "dsf fds unit f"))

    def test_predicate_with_or(self):
        self.assertTrue(test_predicate("test or unit", "dsf fdsfunit"))
        self.assertTrue(test_predicate("@test or unit", "dsf @test fdsf"))

        self.assertFalse(test_predicate("test and unit", "dsf rtrest fdsf"))

    def test_predicate_with_not(self):
        self.assertTrue(test_predicate("not test", "dsf fdsfunit"))
        self.assertTrue(test_predicate("not @test", "dsf fdsfunit"))

        self.assertFalse(test_predicate("not @test", "dsf @test rtrest fdsf"))

    def test_project_search(self):
        self.assertTrue(test_predicate(
            "project = proj", "dsf fdsfunit", "proj")
            )
        self.assertTrue(test_predicate(
            "project != proj2", "dsf fdsfunit", "proj")
            )

        self.assertFalse(test_predicate(
            "project != proj", "dsf fdsfunit", "proj")
            )

        self.assertFalse(test_predicate(
            "project = proj", "dsf fdsfunit", "proj2")
            )

    def test_complex_predicates(self):
        self.assertTrue(test_predicate(
            "(@test or kest) and @west", "kest @west asb")
            )
        self.assertTrue(test_predicate(
            "(@test or kest) and @west", "@test @west asb")
            )
        self.assertTrue(test_predicate(
            "@today and not @done", "- fm s,d @today")
            )
        self.assertTrue(test_predicate(
            "(@test and kest) or not @west", "fsd asb")
            )
        self.assertTrue(test_predicate(
            "(@test and kest) or @west", "@test kest asb")
            )
        self.assertFalse(test_predicate(
            "@today and not @done", "- fm s,d @today @done(2013-11-01)")
            )

    def test_quoted_text_search(self):
        self.assertTrue(test_predicate(
            '"@test < 1"', "awefds@test < 1mfkld")
            )
        self.assertTrue(test_predicate(
            '"@test < 1', "awefds@test < 1mfkld")
            )
        self.assertTrue(test_predicate(
            '"@test < 1" and @d', "awefds@test < 1mfkld @d")
            )

        self.assertFalse(test_predicate(
            '"@test < 1"', "@test(0)")
            )
# run
unittest.main()
