"""Implementation of the replace-break-with-continue and
replace-continue-with-break operators.
"""

from .keyword_replacer import KeywordReplacementOperator


class ReplaceBreakWithContinue(KeywordReplacementOperator):
    "Operator which replaces 'break' with 'continue'."
    def __init__(self, *args, **kwargs):
        super().__init__('break', 'continue', *args, **kwargs)


class ReplaceContinueWithBreak(KeywordReplacementOperator):
    "Operator which replaces 'continue' with 'break'."
    def __init__(self, *args, **kwargs):
        super().__init__('continue', 'break', *args, **kwargs)
