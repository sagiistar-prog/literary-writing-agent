const node = (tag, text, className) => {
  const element = document.createElement(tag);
  if (text !== undefined) element.textContent = text;
  if (className) element.className = className;
  return element;
};

export class WritingReview {
  constructor(options) { Object.assign(this, options); this.records = {}; }
  signature() { return JSON.stringify(this.input()); }
  current() { return this.records[this.input().task]; }
  fresh() { const record = this.current(); return record && record.signature === this.signature(); }
  snapshot() { return this.records; }
  restore(records) { this.records = records || {}; this.render(); }
  reveal() {
    this.root.scrollTop = 0;
    document.getElementById('review-board').scrollIntoView({block:'start'});
    document.getElementById('review-title').focus({preventScroll:true});
  }
  async call(proposal, choices = {}) {
    return (await this.request('/api/session', {method: 'POST', body: JSON.stringify({
      ...this.input(), ...(proposal ? {proposal, accepted_edits: Object.keys(choices).filter(id => choices[id] === 'accepted')} : {})
    })})).session;
  }
  async prepare() {
    const record = this.current();
    const session = await this.call(this.fresh() ? record.session.proposal : null, this.fresh() ? record.choices : {});
    this.records[session.task] = {signature: this.signature(), session,
      choices: this.fresh() ? record.choices : {}, history: this.fresh() ? record.history : []};
    this.render(); this.changed(); this.reveal();
  }
  async importProposal(proposal) {
    const session = await this.call(proposal);
    this.records[session.task] = {signature: this.signature(), session, choices: {}, history: []};
    this.render(); this.changed(); this.reveal();
  }
  async decide(id, value) {
    if (!this.fresh()) return;
    const record = this.current();
    const next = {...record.choices, [id]: value};
    const session = await this.call(record.session.proposal, next);
    record.history.push({...record.choices});
    record.choices = next; record.session = session;
    this.render(); this.changed();
    document.getElementById('edit-' + id)?.querySelector(`[data-choice="${value}"]`)?.focus({preventScroll: true});
  }
  async undo() {
    if (!this.fresh()) return;
    const record = this.current();
    if (!record.history.length) return;
    const previous = record.history[record.history.length - 1];
    const session = await this.call(record.session.proposal, previous);
    record.choices = record.history.pop(); record.session = session;
    this.render(); this.changed();
    document.getElementById('review-count').focus({preventScroll: true});
  }
  button(label, callback, className = 'secondary-button') {
    const button = node('button', label, className); button.type = 'button';
    button.addEventListener('click', () => this.action(callback));
    return button;
  }
  render() {
    const record = this.current(), fresh = this.fresh(), session = record?.session;
    this.root.replaceChildren();
    this.setOutput(fresh && session?.proposal ? session.markdown : '');
    document.getElementById('copy-output').disabled = !fresh || !session?.proposal;
    document.getElementById('download-output').disabled = !fresh || !session?.proposal;
    document.getElementById('download-manuscript').disabled = !fresh || !session?.proposal || !['revision','male_gaze'].includes(session.task);
    document.getElementById('export-request').disabled = !fresh;
    if (!record) {
      this.root.append(node('p', '先写下原稿和这次想调整的地方，再准备写作请求。', 'empty-state'));
      return;
    }
    if (!fresh) {
      this.root.append(node('p', '输入已改变。请重新准备写作请求，旧建议和选择仍保留。', 'stale-note'));
      return;
    }
    if (!session.proposal) {
      this.root.append(node('h4', '写作请求已准备'), node('p', '导出请求交给已安装本插件的 AI 助手，完成后导入建议包，在这里逐条审阅。'));
      return;
    }
    this.root.append(node('p', session.proposal.summary, 'review-summary'));
    if (['outline','inspiration'].includes(session.task)) {
      this.root.append(node('div', session.proposal.content, 'manuscript-text'));
      for (const [label, key] of [['创作取舍','notes'],['新增设定','assumptions'],['待确认','questions']]) {
        if (!session.proposal[key].length) continue;
        const details = node('details'), summary = node('summary', label);
        details.append(summary, ...session.proposal[key].map(text => node('p',text)));
        this.root.append(details);
      }
      return;
    }
    const toolbar = node('div', undefined, 'review-toolbar');
    const accepted = Object.values(record.choices).filter(v => v === 'accepted').length;
    const pending = session.edits.filter(e => !record.choices[e.id]).length;
    const count = node('p', `${accepted} 处已采纳，${pending} 处待审阅`); count.id = 'review-count'; count.tabIndex = -1;
    const undo = this.button('撤销上一步', () => this.undo()); undo.disabled = !record.history.length;
    toolbar.append(count, undo); this.root.append(toolbar);
    if (!session.edits.length) this.root.append(node('p', '本轮没有局部修改建议，原稿保持不变。'));
    for (const edit of session.edits) {
      const item = node('section', undefined, 'edit-item'); item.id = 'edit-' + edit.id;
      item.setAttribute('aria-label', `修改 ${edit.id}`);
      const heading = node('h4', `${edit.id} / ${record.choices[edit.id] === 'accepted' ? '已采纳' : record.choices[edit.id] === 'rejected' ? '已保留原文' : '待审阅'}`);
      const comparison = node('div', undefined, 'edit-comparison');
      for (const [label,text] of [['原文',edit.before],['建议',edit.after || '（删除此段）']]) {
        const pane = node('div'); pane.append(node('h5',label),node('p',text,'manuscript-text')); comparison.append(pane);
      }
      const actions = node('div', undefined, 'edit-actions');
      for (const [label,value] of [['采纳','accepted'],['保留原文','rejected']]) {
        const button = this.button(label, () => this.decide(edit.id,value)); button.dataset.choice = value;
        button.setAttribute('aria-pressed', String(record.choices[edit.id] === value)); actions.append(button);
      }
      item.append(heading, comparison, node('p',edit.rationale,'edit-rationale'),actions); this.root.append(item);
    }
    if (session.proposal.questions.length) {
      const details = node('details'); details.append(node('summary','待确认'), ...session.proposal.questions.map(q=>node('p',q))); this.root.append(details);
    }
    const preview = node('section', undefined, 'review-preview');
    preview.append(node('h4','当前稿件'), node('p',session.revised_scene,'manuscript-text'));
    this.root.append(preview);
  }
}
