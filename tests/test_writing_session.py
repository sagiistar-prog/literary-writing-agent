import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from writing_session import prepare, run_session
from plugin_run import run


class WritingSessions(unittest.TestCase):
    def setUp(self):
        self.data = {'task': 'revision', 'scene': '  月亮🌒。\r\n不要走。\r\n不要走。  ', 'instructions': '保留第二次重复。'}
        self.proposal = {'schema_version': '1.0', 'task': 'revision', 'input_hash': prepare(self.data)['input_hash'],
                         'summary': '缩短第一处停顿。', 'questions': [], 'edits': [
                             {'id': 'E1', 'before': '不要走。', 'occurrence': 1, 'after': '等等。', 'rationale': '第一次改成短促请求。'},
                             {'id': 'E2', 'before': '月亮🌒', 'occurrence': 1, 'after': '残月🌒', 'rationale': '压缩月形。'}]}

    def result(self, **kwargs):
        return run_session({**self.data, 'proposal': self.proposal, **kwargs})

    def test_without_proposal_keeps_original(self):
        result = run_session(self.data)
        self.assertEqual(result['phase'], 'needs_proposal')
        self.assertEqual(result['revised_scene'], self.data['scene'])
        self.assertFalse(result['edits'])
        self.assertNotIn('Lin Qiao', result['markdown'])

    def test_no_automatic_acceptance(self):
        self.assertEqual(self.result()['revised_scene'], self.data['scene'])

    def test_select_only_one_preserves_all_other_bytes(self):
        self.assertEqual(self.result(accepted_edits=['E1'])['revised_scene'], '  月亮🌒。\r\n等等。\r\n不要走。  ')

    def test_undo_is_original_even_after_multiple_selections(self):
        self.result(accepted_edits=['E1', 'E2'])
        self.assertEqual(self.result(accepted_edits=[])['revised_scene'].encode(), self.data['scene'].encode())

    def test_selection_order_independent(self):
        self.assertEqual(self.result(accepted_edits=['E2', 'E1'])['revised_scene'], self.result(accepted_edits=['E1', 'E2'])['revised_scene'])

    def test_occurrence_addresses_second_duplicate(self):
        self.proposal['edits'][0]['occurrence'] = 2
        self.assertEqual(self.result(accepted_edits=['E1'])['revised_scene'], '  月亮🌒。\r\n不要走。\r\n等等。  ')

    def test_deletion_only_removes_selected_span(self):
        self.proposal['edits'][0]['after'] = ''
        self.assertEqual(self.result(accepted_edits=['E1'])['revised_scene'], '  月亮🌒。\r\n\r\n不要走。  ')

    def test_insertion_uses_anchor_without_losing_original(self):
        self.proposal['edits'][0]['after'] = '不要走。她停了下来。'
        self.assertIn('不要走。她停了下来。\r\n不要走。',self.result(accepted_edits=['E1'])['revised_scene'])

    def test_stale_scene_and_instructions_rejected(self):
        for key in ['scene','instructions']:
            with self.subTest(key=key), self.assertRaises(ValueError): self.result(**{key:self.data[key]+' '})

    def test_wrong_task_rejected(self):
        self.proposal['task']='male_gaze'
        with self.assertRaises(ValueError): self.result()

    def test_overlapping_edits_rejected(self):
        self.proposal['edits'][1]['before']='不要走'
        with self.assertRaises(ValueError): self.result()

    def test_missing_quote_and_occurrence_rejected(self):
        for changes in [{'before':'不存在'}, {'occurrence':3}, {'occurrence':0}, {'occurrence':True}]:
            with self.subTest(changes=changes):
                data=copy.deepcopy(self.proposal); data['edits'][0].update(changes)
                with self.assertRaises(ValueError): self.result(proposal=data)

    def test_duplicate_ids_rejected(self):
        self.proposal['edits'][1]['id']='E1'
        with self.assertRaises(ValueError): self.result()

    def test_unknown_or_duplicate_acceptance_rejected(self):
        for accepted in [['E9'], ['E1','E1']]:
            with self.subTest(accepted=accepted), self.assertRaises(ValueError): self.result(accepted_edits=accepted)

    def test_acceptance_requires_proposal(self):
        with self.assertRaises(ValueError): run_session({**self.data, 'accepted_edits':['E1']})

    def test_empty_edits_valid(self):
        self.proposal['edits']=[]
        self.assertEqual(self.result()['revised_scene'],self.data['scene'])

    def test_identity_and_whitespace_only_edits_rejected(self):
        for before,after in [('不要走。','不要走。'),('  ','')]:
            with self.subTest(before=before):
                data=copy.deepcopy(self.proposal);data['edits'][0].update(before=before,after=after)
                with self.assertRaises(ValueError): self.result(proposal=data)

    def test_blank_required_input_rejected(self):
        for task,field in [('outline','brief'),('revision','scene'),('male_gaze','scene')]:
            with self.subTest(task=task), self.assertRaises(ValueError): run_session({'task':task,field:' \n'})

    def test_all_four_fictional_examples(self):
        for stem in ['revision','agency','outline','inspiration']:
            with self.subTest(stem=stem):
                data=json.loads((ROOT/f'examples/{stem}-input.json').read_text(encoding='utf-8'))
                data['proposal']=json.loads((ROOT/f'examples/{stem}-proposal.json').read_text(encoding='utf-8'))
                result=run(data)
                self.assertEqual(result['result']['phase'],'review_ready')
                self.assertEqual(result['mode'],'author_review')

    def test_arbitrary_brief_not_replaced_by_sample(self):
        for task in ['outline','inspiration']:
            data={'task':task,'brief':'火山邮局，收件人是一只猫。','character':'一只不识字的猫'}
            result=run_session(data)
            self.assertEqual(result['source']['brief'], data['brief'])
            self.assertIsNone(result['proposal'])
            self.assertNotIn('Lin Qiao',result['markdown'])

    def test_fresh_directory_preserves_previous_artifacts(self):
        output=ROOT/'output';output.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=output) as temp:
            destination=Path(temp)/'run'
            command=[sys.executable,str(ROOT/'scripts/plugin_run.py'),'--input','examples/revision-input.json','--proposal','examples/revision-proposal.json','--output-dir',str(destination)]
            first=subprocess.run(command,cwd=ROOT,capture_output=True)
            self.assertEqual(first.returncode,0,first.stderr)
            previous=(destination/'manuscript.txt').read_bytes()
            second=subprocess.run(command,cwd=ROOT,capture_output=True)
            self.assertEqual(second.returncode,2)
            self.assertEqual(previous,(destination/'manuscript.txt').read_bytes())

    def test_independent_fixture_partial_acceptance(self):
        data=json.loads((ROOT/'examples/forward-input.json').read_text(encoding='utf-8'))
        proposal=json.loads((ROOT/'examples/forward-proposal.json').read_text(encoding='utf-8'))
        result=run_session({**data,'proposal':proposal,'accepted_edits':['E1']})
        edit=proposal['edits'][0]
        self.assertEqual(result['revised_scene'],data['scene'].replace(edit['before'],edit['after'],1))
        self.assertEqual(result['revised_scene'].count('明天再说'),2)
        self.assertIn('我没有开门。',result['revised_scene'])


if __name__ == '__main__': unittest.main()
