import argparse
import sys
from functools import partial

from codealmanac.cli.syntax.catalog import CommandCatalog
from codealmanac.cli.syntax.classify import classify_syntax_problem
from codealmanac.cli.syntax.models import CliSyntaxError


class CodeAlmanacArgumentParser(argparse.ArgumentParser):
    current_argv: tuple[str, ...] = ()

    def __init__(
        self,
        *args,
        command_catalog: CommandCatalog,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.command_catalog = command_catalog

    def parse_args(self, args=None, namespace=None):
        raw_args = tuple(sys.argv[1:] if args is None else args)
        CodeAlmanacArgumentParser.current_argv = raw_args
        return super().parse_args(args, namespace)

    def add_subparsers(self, **kwargs):
        kwargs.setdefault(
            "parser_class",
            partial(
                CodeAlmanacArgumentParser,
                command_catalog=self.command_catalog,
            ),
        )
        return super().add_subparsers(**kwargs)

    def error(self, message: str) -> None:
        problem = classify_syntax_problem(
            CodeAlmanacArgumentParser.current_argv,
            message,
            self.command_catalog,
        )
        raise CliSyntaxError(problem)
