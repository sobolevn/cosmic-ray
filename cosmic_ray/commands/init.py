"Implementation of the 'init' command."
import logging
import uuid

from cosmic_ray.ast import get_ast, OperatorVisitor
import cosmic_ray.modules
from cosmic_ray.plugins import get_interceptor, interceptor_names, get_operator
from cosmic_ray.util import get_col_offset, get_line_number
from cosmic_ray.work_item import WorkItem


log = logging.getLogger()

class WorkDBInitVisitor(OperatorVisitor):
    """An AST visitor that initializes a WorkDB for a specific module and operator.

    The idea is to walk the AST looking for nodes that the operator can mutate.
    As they're found, `activate` is called and this core adds new
    WorkItems to the WorkDB. Use this core to populate a WorkDB by creating one
    for each operator-module pair and running it over the module's AST.
    """

    def __init__(self, module_path, op_name, work_db, operator):
        super().__init__(operator)

        self.module_path = module_path
        self.op_name = op_name
        self.work_db = work_db
        self.occurrence = 0

    def activate(self, node, num_mutations):
        self.work_db.add_work_items(
            WorkItem(
                job_id=uuid.uuid4().hex,
                module_path=str(self.module_path),
                operator=self.op_name,
                occurrence=self.occurrence + c,
                line_number=node.start_pos[0],
                col_offset=node.start_pos[1])
            for c in range(num_mutations))

        self.occurrence += num_mutations

        return node


def init(module_paths,
         work_db,
         config,
         timeout):
    """Clear and initialize a work-db with work items.

    Any existing data in the work-db will be cleared and replaced with entirely
    new work orders. In particular, this means that any results in the db are
    removed.

    Args:
      module_paths: iterable of pathlib.Paths of modules to mutate.
      work_db: A `WorkDB` instance into which the work orders will be saved.
      config: The configuration for the new session.
      timeout: The timeout to apply to the work in the session.
    """
    operator_names = cosmic_ray.plugins.operator_names()
    work_db.set_config(
        config=config,
        timeout=timeout)

    work_db.clear_work_items()

    for module_path in module_paths:
        for op_name in operator_names:
            operator = get_operator(op_name)()
            visitor = WorkDBInitVisitor(module_path, op_name, work_db, operator)
            # TODO: How do we get python version in here?
            module_ast = get_ast(module_path, python_version="3.6")

            visitor.walk(module_ast)

    # apply_interceptors(work_db)


def apply_interceptors(work_db):
    """Apply each registered interceptor to the WorkDB."""
    for name in interceptor_names():
        interceptor = get_interceptor(name)
        interceptor(work_db)
