import { WritingReview } from "./review.js";
const STORAGE_KEY = "literary-writing-agent.projects.v1";

const TASKS = {
  outline: {
    title: "小说大纲编撰",
    hint: "故事简述",
    fields: ["brief"],
    filename: "generated_outline.md",
  },
  inspiration: {
    title: "灵感生成",
    hint: "故事简述 + 人物种子",
    fields: ["brief", "character"],
    filename: "generated_inspirations.md",
  },
  revision: {
    title: "场景润色",
    hint: "场景草稿",
    fields: ["scene"],
    filename: "generated_revision.md",
  },
  male_gaze: {
    title: "去男性凝视改写",
    hint: "场景草稿",
    fields: ["scene"],
    filename: "generated_male_gaze_revision.md",
  },
};

const state = {
  task: "outline",
  examples: null,
  outputText: "",
  projectId: "",
  images: [],
  dirty: false,
  busy: false,
  outputs: {},
  outputTask: "outline",
};

const elements = {
  tabs: [...document.querySelectorAll(".task-tab")],
  title: document.querySelector("#task-title"),
  hint: document.querySelector("#task-hint"),
  status: document.querySelector("#status-line"),
  loadSample: document.querySelector("#load-sample"),
  generate: document.querySelector("#generate"),
  runAudit: document.querySelector("#run-audit"),
  copyOutput: document.querySelector("#copy-output"),
  downloadOutput: document.querySelector("#download-output"),
  newProject: document.querySelector("#new-project"),
  saveProject: document.querySelector("#save-project"),
  exportProject: document.querySelector("#export-project"),
  projectTitle: document.querySelector("#project-title"),
  projectList: document.querySelector("#project-list"),
  imageInput: document.querySelector("#image-input"),
  imageGallery: document.querySelector("#image-gallery"),
  notes: document.querySelector("#notes-input"),
  output: document.querySelector("#output"),
  fields: {
    brief: document.querySelector('[data-field="brief"]'),
    character: document.querySelector('[data-field="character"]'),
    scene: document.querySelector('[data-field="scene"]'),
  },
  inputs: {
    brief: document.querySelector("#brief-input"),
    character: document.querySelector("#character-input"),
    scene: document.querySelector("#scene-input"),
  },
};

function setStatus(message, type = "") {
  elements.status.textContent = message;
  elements.status.classList.toggle("is-error", type === "error");
  elements.status.classList.toggle("is-ok", type === "ok");
}

function escapeHtml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

async function requestJson(url, options = {}) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
    signal: AbortSignal.timeout(60000),
  });
  const data = await response.json();
  if (!response.ok || (data.ok === false && !data.output)) {
    throw new Error(data.error || "Request failed.");
  }
  return data;
}

function loadProjects() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    const projects = raw ? JSON.parse(raw) : [];
    return Array.isArray(projects) ? projects : [];
  } catch {
    return [];
  }
}

function saveProjects(projects) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(projects));
}

function currentProjectPayload() {
  return {
    id: state.projectId || crypto.randomUUID(),
    title: elements.projectTitle.value.trim() || "未命名作品",
    task: state.task,
    brief: elements.inputs.brief.value,
    character: elements.inputs.character.value,
    scene: elements.inputs.scene.value,
    notes: elements.notes.value,
    output: state.outputText,
    outputs: state.outputs,
    outputTask: state.outputTask,
    images: state.images,
    reviews: review.snapshot(),
    updatedAt: new Date().toISOString(),
  };
}

function refreshProjectList() {
  const projects = loadProjects().sort((a, b) => (b.updatedAt || "").localeCompare(a.updatedAt || ""));
  elements.projectList.innerHTML = "";

  const empty = document.createElement("option");
  empty.value = "";
  empty.textContent = projects.length ? "选择已保存作品" : "暂无已保存作品";
  elements.projectList.appendChild(empty);

  for (const project of projects) {
    const option = document.createElement("option");
    option.value = project.id;
    option.textContent = project.title || "未命名作品";
    elements.projectList.appendChild(option);
  }
}

function saveCurrentProject() {
  const project = currentProjectPayload();
  const projects = loadProjects().filter((item) => item.id !== project.id);
  projects.push(project);
  try { saveProjects(projects); }
  catch { setStatus("浏览器空间不足或禁止存储。草稿仍在，请先导出作品包再整理插图。", "error"); return false; }
  state.dirty = false;
  state.projectId = project.id;
  refreshProjectList();
  elements.projectList.value = project.id;
  setStatus("作品已保存到本机浏览器。", "ok");
}

function loadProject(id) {
  const project = loadProjects().find((item) => item.id === id);
  if (!project) {
    return;
  }

  if (!canReplaceDraft()) { elements.projectList.value = state.projectId; return; }
  state.dirty = false;
  state.projectId = project.id;
  state.outputs = project.outputs || { [project.outputTask || project.task || "outline"]: project.output || "" };
  state.outputText = project.output || "";
  state.images = Array.isArray(project.images) ? project.images : [];
  elements.projectTitle.value = project.title || "";
  elements.inputs.brief.value = project.brief || "";
  elements.inputs.character.value = project.character || "";
  elements.inputs.scene.value = project.scene || "";
  elements.notes.value = project.notes || "";
  review.restore(project.reviews);
  setTask(project.task || "outline", { preserveStatus: true });
  renderImages();
  renderOutput();
  setStatus("已打开本机保存的作品。", "ok");
}

function newProject() {
  if (!canReplaceDraft()) return;
  state.outputs = {};
  review.restore({});
  state.dirty = false;
  state.projectId = "";
  state.outputText = "";
  state.images = [];
  elements.projectTitle.value = "未命名作品";
  elements.inputs.brief.value = "";
  elements.inputs.character.value = "";
  elements.inputs.scene.value = "";
  elements.notes.value = "";
  elements.projectList.value = "";
  renderImages();
  renderOutput();
  setStatus("新的创作台已打开。", "ok");
}

function exportCurrentProject() {
  const project = currentProjectPayload();
  const content = JSON.stringify(project, null, 2);
  const blob = new Blob([content], { type: "application/json;charset=utf-8" });
  const safeTitle = project.title.replace(/[^\w\u4e00-\u9fa5-]+/g, "-").slice(0, 60) || "project";
  downloadBlob(blob, `${safeTitle}.json`);
  setStatus("作品包已导出。", "ok");
}

function setTask(task, options = {}) {
  if (state.busy || !TASKS[task]) return;
  state.task = task;
  state.outputTask = task;
  state.outputText = state.outputs[task] || "";
  renderOutput();
  const config = TASKS[task];
  elements.title.textContent = config.title;
  elements.hint.textContent = config.hint;

  elements.tabs.forEach((tab) => {
    tab.classList.toggle("is-active", tab.dataset.task === task);
    tab.setAttribute("aria-pressed", String(tab.dataset.task === task));
  });

  Object.entries(elements.fields).forEach(([name, field]) => {
    field.classList.toggle("is-hidden", !config.fields.includes(name));
  });

  if (!options.preserveStatus) {
    setStatus("本机创作台已就绪。");
  }
}

async function loadExamples() {
  if (!canReplaceDraft()) return;
  const oldVersion = draftVersion;
  if (!state.examples) {
    state.examples = await requestJson("/api/examples");
  }

  if (draftVersion !== oldVersion) { setStatus("已保留载入期间的新输入，请再次载入示例。"); return; }
  review.restore({});
  state.projectId = ""; state.outputs = {}; state.outputText = ""; state.images = [];
  state.dirty = true; renderOutput(); renderImages(); elements.projectList.value = "";
  elements.projectTitle.value = "雨图修复师";
  elements.inputs.brief.value = state.examples.storyBrief;
  elements.inputs.character.value = state.examples.characterSeed;
  elements.inputs.scene.value = state.examples.scene;
  elements.notes.value = "可以从地图、雨井、档案室和被延迟承认的记忆继续展开。";
  setStatus("已载入公开原创示例。", "ok");
}

function currentPayload() {
  return {
    task: state.task,
    ...Object.fromEntries(TASKS[state.task].fields.map(field => [field, elements.inputs[field].value])),
    instructions: elements.notes.value,
  };
}

async function reviewAction(callback) {
  if (state.busy) return;
  setBusy(true);
  setStatus("正在检查当前稿件…");
  try { await callback(); setStatus("已更新，原稿保持不变。", "ok"); }
  catch(error) { setStatus(error.message || "操作失败，原稿和已有建议已保留。", "error"); }
  finally { setBusy(false); }
}
async function generate() { await reviewAction(() => review.prepare()); }

async function runAudit() {
  setStatus("正在运行审计...");
  elements.runAudit.disabled = true;
  try {
    const data = await requestJson("/api/audit", {
      method: "POST",
      body: JSON.stringify({}),
    });
    const audit = document.querySelector("#audit-output");
    audit.textContent = data.output;
    document.querySelector("#audit-panel").open = true;
    setStatus(data.ok ? "审计通过。" : "审计未通过，请查看输出。", data.ok ? "ok" : "error");
  } catch (error) {
    setStatus(error.message, "error");
  } finally {
    elements.runAudit.disabled = false;
  }
}

function renderOutput() { review.render(); }

async function copyOutput() {
  if (!state.outputText) {
    setStatus("当前没有可复制的输出。", "error");
    return;
  }
  try { await navigator.clipboard.writeText(state.outputText); setStatus("输出已复制。", "ok"); }
  catch { setStatus("无法访问剪贴板，请使用下载保存生成稿。", "error"); }
}

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

function downloadOutput() {
  if (!state.outputText) {
    setStatus("当前没有可下载的输出。", "error");
    return;
  }
  const blob = new Blob([state.outputText], { type: "text/markdown;charset=utf-8" });
  downloadBlob(blob, TASKS[state.outputTask].filename);
  setStatus("输出已生成下载。", "ok");
}

function addImages(files) {
  const validFiles = [...files].filter((file) => file.type.startsWith("image/"));
  if (!validFiles.length) {
    return;
  }

  if (state.images.length + validFiles.length > 12) { setStatus("最多保留 12 张插图，请先导出或移除已有图片。", "error"); return; }
  if (JSON.stringify(state.images).length + validFiles.reduce((total, file) => total + file.size * 1.4, 0) > 2000000) { setStatus("插图总量超过 2MB，请压缩图片；现有插图已保留。", "error"); return; }
  const imageProject = state.projectId;
  const readers = validFiles.map((file) => {
    return new Promise((resolve, reject) => {
      if (file.size > 1_500_000) {
        reject(new Error(`${file.name} 超过本地保存大小限制。`));
        return;
      }
      const reader = new FileReader();
      reader.onload = () => resolve({ id: crypto.randomUUID(), name: file.name, dataUrl: reader.result });
      reader.onerror = () => reject(new Error(`${file.name} 读取失败。`));
      reader.readAsDataURL(file);
    });
  });

  Promise.all(readers)
    .then((images) => {
      if (state.projectId !== imageProject) return;
      state.images = [...state.images, ...images];
      state.dirty = true;
      renderImages();
      setStatus("插图已加入创作台。", "ok");
    })
    .catch((error) => setStatus(error.message, "error"));
}

function removeImage(id) {
  state.dirty = true;
  state.images = state.images.filter((image) => image.id !== id);
  renderImages();
  setStatus("插图已移除。", "ok");
}

function renderImages() {
  if (!state.images.length) {
    elements.imageGallery.innerHTML = '<div class="image-empty">插图板为空</div>';
    return;
  }

  elements.imageGallery.innerHTML = state.images
    .map(
      (image) => `
        <figure class="image-card">
          <img src="${image.dataUrl}" alt="${escapeHtml(image.name)}" />
          <button type="button" data-remove-image="${image.id}" title="移除插图">×</button>
        </figure>
      `,
    )
    .join("");
}

elements.tabs.forEach((tab) => tab.addEventListener("click", () => setTask(tab.dataset.task)));
elements.loadSample.addEventListener("click", () => loadExamples().catch(error => setStatus(error.message, "error")));
elements.generate.addEventListener("click", generate);
elements.runAudit.addEventListener("click", runAudit);
elements.copyOutput.addEventListener("click", copyOutput);
elements.downloadOutput.addEventListener("click", downloadOutput);
elements.saveProject.addEventListener("click", saveCurrentProject);
elements.newProject.addEventListener("click", newProject);
elements.exportProject.addEventListener("click", exportCurrentProject);
elements.projectList.addEventListener("change", (event) => loadProject(event.target.value));
elements.imageInput.addEventListener("change", (event) => {
  addImages(event.target.files || []);
  event.target.value = "";
});
elements.imageGallery.addEventListener("click", (event) => {
  const button = event.target.closest("[data-remove-image]");
  if (button) {
    removeImage(button.dataset.removeImage);
  }
});

const review = new WritingReview({
  root: elements.output, input: currentPayload, request: requestJson,
  action: reviewAction, changed: () => { state.dirty = true; },
  setOutput: value => { state.outputText = value; state.outputs[state.task] = value; }
});
document.getElementById('export-request').addEventListener('click', () => {
  if (!review.fresh()) return;
  downloadBlob(new Blob([JSON.stringify(review.current().session.request,null,2)], {type:'application/json'}),'writing-request.json');
  setStatus('请求已导出，请交给 AI 助手生成建议包。');
});
document.getElementById('download-manuscript').addEventListener('click', () => {
  if (!review.fresh() || !review.current().session.proposal) return;
  downloadBlob(new Blob([review.current().session.revised_scene],{type:'text/plain;charset=utf-8'}),'manuscript.txt');
  setStatus('当前稿件已下载。');
});
document.getElementById('import-proposal').addEventListener('change', event => {
  const file = event.target.files[0]; event.target.value = '';
  if (!file || state.busy) return;
  void reviewAction(async () => {
    if (file.size > 1000000) throw new Error('建议包超过 1 MB，请缩小后重试。');
    let data;
    try { data = JSON.parse(await file.text()); } catch { throw new Error('建议包不是有效 JSON，已有内容已保留。'); }
    await review.importProposal(data);
  });
});
document.getElementById('try-review').addEventListener('click', () => {
  if (!canReplaceDraft()) return;
  void reviewAction(async () => {
    const data = await requestJson('/api/examples');
    state.projectId = ''; state.outputs = {}; state.images = [];
    elements.projectTitle.value = '末班渡船'; elements.projectList.value = '';
    elements.inputs.brief.value = ''; elements.inputs.character.value = '';
    elements.inputs.scene.value = data.reviewExample.scene;
    elements.notes.value = data.reviewExample.instructions;
    state.task = 'revision'; state.outputTask = 'revision';
    review.restore({});
    await review.importProposal(data.reviewProposal);
    renderImages();
  }).then(() => setTask('revision',{preserveStatus:true}));
});
refreshProjectList();
renderImages();
setTask('revision');
setStatus("写下原稿，保留你的表达。也可以先试读一份修订示例。");

let draftVersion = 0;
function canReplaceDraft() {
  return !state.busy && (!state.dirty || window.confirm('这会替换未保存的草稿。确定放弃修改吗？选择取消可先保存或导出。'));
}
function setBusy(value) {
  state.busy = value;
  for (const control of [...elements.tabs, elements.generate, elements.loadSample, elements.newProject, elements.projectList, ...Object.values(elements.inputs), elements.projectTitle, elements.notes, elements.imageInput, elements.saveProject, elements.exportProject, document.getElementById('try-review'), document.getElementById('import-proposal')]) control.disabled = value;
  for (const control of elements.output.querySelectorAll('button')) control.disabled = value || (control.textContent === '撤销上一步' && !review.current()?.history.length);
  elements.output.setAttribute('aria-busy', String(value));
}
for (const input of [...Object.values(elements.inputs), elements.projectTitle, elements.notes]) input.addEventListener('input', () => { state.dirty = true; draftVersion += 1; review.render(); });
window.addEventListener('beforeunload', event => { if (state.dirty) { event.preventDefault(); event.returnValue = ''; } });
document.addEventListener('keydown', event => { if ((event.ctrlKey || event.metaKey) && event.key === 'Enter' && !event.isComposing) { event.preventDefault(); void generate(); } });

const libraryDisclosure = document.querySelector('.project-panel');
if (libraryDisclosure) libraryDisclosure.open = !window.matchMedia('(max-width:760px)').matches;
