import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.project_bundle import validate_project
from scripts.writing_session import run_session

PNG = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+a6ioAAAAASUVORK5CYII='


class ProjectRecovery(unittest.TestCase):
    def setUp(self):
        self.source = json.loads((ROOT / 'examples/revision-input.json').read_text(encoding='utf-8'))
        self.proposal = json.loads((ROOT / 'examples/revision-proposal.json').read_text(encoding='utf-8'))
        self.project = dict(title='渡船草稿', task='revision', brief='', character='',
                            scene=self.source['scene'], notes=self.source['instructions'],
                            images=[dict(id='image1', name='原创色块.png', dataUrl=PNG)], reviews={
            'revision': dict(signature=json.dumps(self.source, ensure_ascii=False),
                             session=run_session({**self.source, 'proposal': self.proposal}),
                             choices={'E1': 'accepted', 'E2': 'rejected'},
                             history=[{}, {'E1': 'accepted'}])})

    def test_roundtrip_rebuilds_selected_manuscript_and_undo(self):
        before = copy.deepcopy(self.project)
        result = validate_project(self.project)
        record = result['reviews']['revision']
        expected = run_session({**self.source, 'proposal': self.proposal, 'accepted_edits': ['E1']})
        self.assertEqual(record['session']['revised_scene'].encode(), expected['revised_scene'].encode())
        self.assertEqual(record['choices'], before['reviews']['revision']['choices'])
        self.assertEqual(record['history'], before['reviews']['revision']['history'])
        undo = run_session({**self.source, 'proposal': self.proposal, 'accepted_edits': []})
        self.assertEqual(undo['revised_scene'], self.source['scene'])
        self.assertEqual(result['images'], self.project['images'])
        self.assertEqual(self.project, before)
        self.assertEqual(validate_project(result), result)

    def test_untrusted_cached_outputs_are_discarded(self):
        self.project['output'] = '伪造整稿'
        self.project['outputs'] = {'revision': '伪造整稿'}
        record = self.project['reviews']['revision']
        record['session'].update(revised_scene='伪造整稿', markdown='伪造整稿', edits=[])
        result = validate_project(self.project)
        self.assertNotIn('伪造整稿', result['output'])
        self.assertEqual(len(result['reviews']['revision']['session']['edits']), len(self.proposal['edits']))

    def test_changed_draft_retains_stale_record_without_exportable_output(self):
        self.project['scene'] += '\n作者新写的结尾。'
        result = validate_project(self.project)
        self.assertTrue(result['scene'].endswith('作者新写的结尾。'))
        self.assertEqual(result['output'], '')
        self.assertEqual(result['outputs'], {})
        self.assertEqual(json.loads(result['reviews']['revision']['signature']), self.source)

    def test_unknown_choice_or_undo_reference_rejected(self):
        for target in ['choices', 'history']:
            project = copy.deepcopy(self.project)
            record = project['reviews']['revision']
            if target == 'choices': record['choices']['E999'] = 'accepted'
            else: record['history'].append({'E999': 'rejected'})
            with self.subTest(target=target), self.assertRaises(ValueError): validate_project(project)

    def test_mismatched_hash_and_empty_proposal_rejected(self):
        for proposal in [{}, {**self.proposal, 'input_hash': '0' * 64}]:
            self.project['reviews']['revision']['session']['proposal'] = proposal
            with self.subTest(proposal=bool(proposal)), self.assertRaises(ValueError): validate_project(self.project)

    def test_broken_or_wrong_task_signature_rejected(self):
        for value in ['{bad', '[]', json.dumps({**self.source, 'task': 'outline'})]:
            self.project['reviews']['revision']['signature'] = value
            with self.subTest(value=value), self.assertRaises(ValueError): validate_project(self.project)

    def test_schema_version_and_enum_rejected(self):
        for change in [{'schema_version': '99'}, {'task': 'invented'}, {'notes': 'x' * 6001}]:
            with self.subTest(change=list(change)), self.assertRaises(ValueError):
                validate_project({**self.project, **change})

    def test_legacy_empty_draft_and_request_only_roundtrip(self):
        result = validate_project(dict(title='', task='revision', brief='', character='', scene='', notes=''))
        self.assertEqual(result['schema_version'], '1.0')
        self.assertEqual(result['reviews'], {})
        record = self.project['reviews']['revision']
        record.update(session=run_session(self.source), choices={}, history=[])
        result = validate_project(self.project)
        self.assertEqual(result['reviews']['revision']['session']['phase'], 'needs_proposal')

    def test_remote_svg_invalid_encoding_and_disguised_images_rejected(self):
        for url in ['https://example.com/image.png', 'data:image/svg+xml;base64,PHN2Zz4=',
                    'data:image/png;base64,a', 'data:image/png;base64,YmFk', PNG.replace('image/png', 'image/jpeg')]:
            self.project['images'][0]['dataUrl'] = url
            with self.subTest(url=url[:40]), self.assertRaises(ValueError): validate_project(self.project)

    def test_duplicate_images_rejected(self):
        self.project['images'] *= 2
        with self.assertRaises(ValueError): validate_project(self.project)

    def test_all_four_task_records_remain_independent(self):
        project = dict(title='原创练习集', task='revision', brief='', character='', scene='', notes='', reviews={})
        for prefix in ['outline', 'inspiration', 'revision', 'agency']:
            source = json.loads((ROOT / f'examples/{prefix}-input.json').read_text(encoding='utf-8'))
            proposal = json.loads((ROOT / f'examples/{prefix}-proposal.json').read_text(encoding='utf-8'))
            project['reviews'][source['task']] = dict(signature=json.dumps(source),
                session=run_session({**source, 'proposal': proposal}), choices={}, history=[])
        result = validate_project(project)
        self.assertEqual(set(result['reviews']), {'outline', 'inspiration', 'revision', 'male_gaze'})
        self.assertEqual(result['outputs'], {})
        for task, record in result['reviews'].items():
            self.assertEqual(record['session']['task'], task)
            self.assertEqual(record['session']['proposal']['task'], task)


if __name__ == '__main__': unittest.main()
