"""Rebuild portable projects from original inputs and explicit author choices."""
import base64
import copy
import json
import re

from scripts.writing_session import FIELDS, run_session, validate_schema


def validate_project(data):
    validate_schema(data, 'project.schema.json')
    project = copy.deepcopy(data)
    project['schema_version'] = '1.0'
    images = project.get('images', [])
    if sum(len(image['dataUrl']) for image in images) > 2_000_000:
        raise ValueError('插图总量超过 2 MB，请移除部分图片后重试。')
    ids = set()
    for image in images:
        if image['id'] in ids:
            raise ValueError('插图编号重复。')
        ids.add(image['id'])
        match = re.fullmatch(r'data:image/(png|jpeg|webp|gif);base64,([A-Za-z0-9+/]*={0,2})', image['dataUrl'])
        if not match:
            raise ValueError('插图必须是作品包内的 PNG、JPEG、WebP 或 GIF，不能引用网址。')
        try:
            raw = base64.b64decode(match[2], validate=True)
        except ValueError:
            raise ValueError('插图编码损坏，请检查作品包。') from None
        signatures = {'png': raw.startswith(b'\x89PNG\r\n\x1a\n'), 'jpeg': raw.startswith(b'\xff\xd8\xff'),
                      'gif': raw.startswith((b'GIF87a', b'GIF89a')), 'webp': raw.startswith(b'RIFF') and raw[8:12] == b'WEBP'}
        if not signatures[match[1]]:
            raise ValueError('插图格式与内容不符，请检查作品包。')
    records, outputs = {}, {}
    for task, record in project.get('reviews', {}).items():
        try:
            source = json.loads(record['signature'])
        except (ValueError, TypeError):
            raise ValueError('评审记录的原始输入无法读取。') from None
        expected = {'task', *FIELDS[task], 'instructions'}
        if not isinstance(source, dict) or set(source) != expected or source['task'] != task:
            raise ValueError('评审记录的任务或原始输入字段不匹配。')
        proposal = record['session'].get('proposal')
        session = run_session({**source, **({'proposal': proposal} if proposal is not None else {})})
        known = {edit['id'] for edit in session['edits']}
        for choices in [record['choices'], *record['history']]:
            if not set(choices) <= known:
                raise ValueError('评审选择包含未知的修改编号。')
        choices = record['choices']
        accepted = [key for key, value in choices.items() if value == 'accepted']
        if proposal:
            session = run_session({**source, 'proposal': proposal, 'accepted_edits': accepted})
        signature = json.dumps({'task': task, **{field: source[field] for field in FIELDS[task]}, 'instructions': source['instructions']}, ensure_ascii=False, separators=(',', ':'))
        records[task] = {'signature': signature, 'session': session, 'choices': choices, 'history': record['history']}
        current = {'task': task, **{field: project[field] for field in FIELDS[task]}, 'instructions': project['notes']}
        if source == current and proposal:
            outputs[task] = session['markdown']
    project.update(reviews=records, outputs=outputs, outputTask=project['task'], output=outputs.get(project['task'], ''), images=images)
    return project
