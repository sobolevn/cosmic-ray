"A tool for creating XML reports."

import sys
import xml.etree.ElementTree

import docopt

from cosmic_ray.work_db import use_db, WorkDB
from cosmic_ray.work_item import TestOutcome, WorkerOutcome


def report_xml():
    """cr-xml

Usage: cr-xml <session-file>

Print an XML formatted report of test results for continuos integration systems
"""
    arguments = docopt.docopt(report_xml.__doc__, version='cr-rate 1.0')
    with use_db(arguments['<session-file>'], WorkDB.Mode.open) as db:
        xml_elem = _create_xml_report(db)
        xml_elem.write(
            sys.stdout.buffer, encoding='utf-8', xml_declaration=True)


def _create_xml_report(db):
    errors = 0
    failed = 0
    skipped = 0
    root_elem = xml.etree.ElementTree.Element('testsuite')

    for work_item, result in db.completed_work_items:
        if result.worker_outcome in {
                WorkerOutcome.EXCEPTION, WorkerOutcome.ABNORMAL
        }:
            errors += 1
        if result.is_killed:
            failed += 1
        if result.worker_outcome == WorkerOutcome.SKIPPED:
            skipped += 1

        subelement = _create_element_from_work_item(work_item)
        subelement = _update_element_with_result(subelement, result)
        root_elem.append(subelement)

    for work_item in db.pending_work_items:
        subelement = _create_element_from_work_item(work_item)
        root_elem.append(subelement)

    root_elem.set('errors', str(errors))
    root_elem.set('failures', str(failed))
    root_elem.set('skips', str(skipped))
    root_elem.set('tests', str(db.num_work_items))
    return xml.etree.ElementTree.ElementTree(root_elem)


def _create_element_from_work_item(work_item):
    sub_elem = xml.etree.ElementTree.Element('testcase')

    sub_elem.set('classname', work_item.job_id)
    sub_elem.set('line', str(work_item.line_number))
    sub_elem.set('file', str(work_item.module_path))

    return sub_elem


def _update_element_with_result(sub_elem, result):
    data = result.output
    outcome = result.worker_outcome

    if outcome == WorkerOutcome.EXCEPTION:
        error_elem = xml.etree.ElementTree.SubElement(sub_elem, 'error')
        error_elem.set('message', "Worker has encountered exception")
        error_elem.text = str(data) + "\n".join(result.diff)
    elif _evaluation_success(result):
        failure_elem = xml.etree.ElementTree.SubElement(sub_elem, 'failure')
        failure_elem.set('message', "Mutant has survived your unit tests")
        failure_elem.text = str(data) + result.diff

    return sub_elem


def _evaluation_success(result):
    return result.worker_outcome == WorkerOutcome.NORMAL and \
        result.test_outcome in {TestOutcome.SURVIVED,
                                TestOutcome.INCOMPETENT}
