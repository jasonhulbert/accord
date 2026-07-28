import mermaid from "__ASSET_BASE__/mermaid/mermaid.js";

const EVENTS = __DATA__;
const DOCUMENTS = __DOCUMENTS__;
mermaid.initialize({
  startOnLoad: false,
  securityLevel: "strict",
  secure: [
    "secure",
    "securityLevel",
    "startOnLoad",
    "maxTextSize",
    "maxEdges",
    "theme",
    "themeVariables",
    "themeCSS",
    "fontFamily",
    "look",
    "htmlLabels"
  ],
  maxTextSize: 50000,
  maxEdges: 500,
  deterministicIds: true,
  look: "classic",
  theme: "base",
  darkMode: true,
  htmlLabels: false,
  fontFamily: '"IBM Plex Sans", sans-serif',
  themeVariables: {
    darkMode: true,
    background: "#000000",
    fontFamily: '"IBM Plex Sans", sans-serif',
    fontSize: "14px",
    primaryColor: "#111110",
    primaryTextColor: "#f4f4ef",
    primaryBorderColor: "#8c8c88",
    secondaryColor: "#1c1c1a",
    secondaryTextColor: "#f4f4ef",
    secondaryBorderColor: "#5e5e5a",
    tertiaryColor: "#050505",
    tertiaryTextColor: "#f4f4ef",
    tertiaryBorderColor: "#383836",
    lineColor: "#8c8c88",
    textColor: "#f4f4ef",
    mainBkg: "#111110",
    nodeBorder: "#8c8c88",
    clusterBkg: "#050505",
    clusterBorder: "#383836",
    edgeLabelBackground: "#000000",
    noteBkgColor: "#1c1c1a",
    noteTextColor: "#f4f4ef",
    noteBorderColor: "#5e5e5a",
    actorBkg: "#111110",
    actorBorder: "#8c8c88",
    actorTextColor: "#f4f4ef",
    actorLineColor: "#383836",
    signalColor: "#8c8c88",
    signalTextColor: "#f4f4ef",
    labelBoxBkgColor: "#000000",
    labelBoxBorderColor: "#383836",
    labelTextColor: "#f4f4ef",
    loopTextColor: "#f4f4ef",
    activationBkgColor: "#1c1c1a",
    activationBorderColor: "#8c8c88"
  },
  themeCSS: [
    ".node rect, .node polygon, .node circle, .actor, .labelBox { stroke-width: 1px; }",
    ".node rect, .actor, .labelBox { rx: 0; ry: 0; }",
    ".cluster rect { rx: 0; ry: 0; }",
    ".edgeLabel rect { fill: #000000; opacity: 1; }"
  ].join(" "),
  flowchart: {
    curve: "linear",
    nodeSpacing: 36,
    rankSpacing: 48,
    padding: 12
  },
  sequence: {
    diagramMarginX: 24,
    diagramMarginY: 24,
    actorMargin: 56,
    width: 120,
    height: 48,
    boxMargin: 10,
    messageMargin: 28,
    noteMargin: 10
  }
});
const tasks = new Map();
for (const event of EVENTS) {
  if (!tasks.has(event.task)) tasks.set(event.task, []);
  tasks.get(event.task).push(event);
}
const documentsByTask = new Map();
for (const documentItem of DOCUMENTS) {
  if (!tasks.has(documentItem.task)) tasks.set(documentItem.task, []);
  if (!documentsByTask.has(documentItem.task)) {
    documentsByTask.set(documentItem.task, []);
  }
  documentsByTask.get(documentItem.task).push(documentItem);
}

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function label(value) {
  return String(value).replaceAll("-", " ");
}

function addDetail(card, event) {
  const details = [];
  if (event.outcome) details.push(["Outcome", event.outcome]);
  if (event.subject) details.push(["Question", event.subject]);
  if (event.decision) details.push(["Direction", event.decision]);
  for (const [name, value] of details) {
    const line = element("p", "detail");
    const strong = element("strong", "", name + ": ");
    line.append(strong, document.createTextNode(value));
    card.appendChild(line);
  }
  if (event.refs && event.refs.length) {
    const list = element("ul", "refs");
    for (const ref of event.refs) {
      list.appendChild(element("li", "", ref));
    }
    card.appendChild(list);
  }
}

function renderMarkdown(content, container) {
  container.replaceChildren();
  const lines = String(content).replaceAll("\r", "").split("\n");
  let paragraph = [];
  let list = null;
  let quote = [];
  let code = [];
  let codeLanguage = "";
  let inCode = false;

  function appendParagraph() {
    if (!paragraph.length) return;
    container.appendChild(element("p", "", paragraph.join(" ")));
    paragraph = [];
  }

  function appendQuote() {
    if (!quote.length) return;
    container.appendChild(element("blockquote", "", quote.join("\n")));
    quote = [];
  }

  function endList() {
    list = null;
  }

  function appendCode() {
    if (codeLanguage === "mermaid") {
      const figure = element("figure", "diagram");
      const canvas = element("div", "diagram-canvas");
      const output = element("div", "diagram-output");
      const status = element("p", "diagram-status", "Rendering diagram…");
      canvas.append(output, status);
      const source = element("details", "diagram-source");
      source.appendChild(element("summary", "", "Mermaid source"));
      const pre = element("pre");
      pre.appendChild(element("code", "", code.join("\n")));
      source.appendChild(pre);
      figure.append(canvas, source);
      figure.dataset.mermaidSource = code.join("\n");
      container.appendChild(figure);
    } else {
      const pre = element("pre");
      pre.appendChild(element("code", "", code.join("\n")));
      container.appendChild(pre);
    }
    code = [];
    codeLanguage = "";
  }

  for (const line of lines) {
    if (line.startsWith("```")) {
      appendParagraph();
      appendQuote();
      endList();
      if (inCode) {
        appendCode();
      } else {
        codeLanguage = line.slice(3).trim().toLowerCase();
      }
      inCode = !inCode;
      continue;
    }
    if (inCode) {
      code.push(line);
      continue;
    }

    const heading = line.match(/^(#{1,6})\s+(.+)$/);
    const unordered = line.match(/^\s*[-*]\s+(.+)$/);
    const ordered = line.match(/^\s*\d+\.\s+(.+)$/);
    if (heading) {
      appendParagraph();
      appendQuote();
      endList();
      container.appendChild(
        element("h" + heading[1].length, "", heading[2])
      );
    } else if (unordered || ordered) {
      appendParagraph();
      appendQuote();
      const tag = unordered ? "ul" : "ol";
      if (!list || list.tagName.toLowerCase() !== tag) {
        list = element(tag);
        container.appendChild(list);
      }
      list.appendChild(element("li", "", (unordered || ordered)[1]));
    } else if (line.startsWith(">")) {
      appendParagraph();
      endList();
      quote.push(line.replace(/^>\s?/, ""));
    } else if (!line.trim()) {
      appendParagraph();
      appendQuote();
      endList();
    } else {
      appendQuote();
      endList();
      paragraph.push(line.trim());
    }
  }
  if (inCode && code.length) {
    appendCode();
  }
  appendParagraph();
  appendQuote();
}

async function renderDiagrams(container) {
  const diagrams = container.querySelectorAll(".diagram");
  for (const [index, diagram] of diagrams.entries()) {
    const output = diagram.querySelector(".diagram-output");
    const status = diagram.querySelector(".diagram-status");
    try {
      const id = "accord-diagram-" + Date.now() + "-" + index;
      const rendered = await mermaid.render(id, diagram.dataset.mermaidSource);
      output.innerHTML = rendered.svg;
      const svg = output.querySelector("svg");
      const intrinsicWidth = svg && svg.viewBox && svg.viewBox.baseVal.width;
      if (intrinsicWidth) {
        svg.style.width = Math.max(intrinsicWidth, 640) + "px";
      }
      status.remove();
    } catch (error) {
      output.replaceChildren();
      const message = String(error && error.message ? error.message : error);
      const parseLine = message.match(/Parse error on line (\d+)/);
      status.textContent = "Accord could not render this diagram." +
        (parseLine ? " Mermaid reported a parse error near line " +
          parseLine[1] + "." : "");
    }
  }
}

const documentDialog = document.getElementById("document-dialog");
const documentMeta = document.getElementById("document-meta");
const documentBody = document.getElementById("document-body");

async function openDocument(documentItem) {
  documentMeta.textContent = label(documentItem.kind) + " · " + documentItem.ref;
  renderMarkdown(documentItem.content, documentBody);
  documentDialog.showModal();
  await renderDiagrams(documentBody);
}

function documentRow(documentItem) {
  const row = element("article", "event document");
  row.dataset.type = "document";
  row.dataset.kind = documentItem.kind;
  if (documentItem.error) row.dataset.error = "true";
  row.appendChild(element("span", "dot"));

  const card = element("div", "card");
  const meta = element("div", "meta");
  meta.append(
    element("span", "type", "document"),
    element("span", "", label(documentItem.kind))
  );
  const button = element("button", "document-open", documentItem.title);
  button.type = "button";
  button.addEventListener("click", () => openDocument(documentItem));
  card.append(meta, button, element("p", "detail", documentItem.ref));
  row.appendChild(card);
  return row;
}

const root = document.getElementById("tasks");
for (const [taskName, events] of tasks) {
  const documents = documentsByTask.get(taskName) || [];
  const section = element("section", "task");
  const head = element("div", "task-head");
  const itemCount = events.length + " " + (events.length === 1 ? "event" : "events");
  const documentCount = documents.length
    ? " · " + documents.length + " " + (documents.length === 1 ? "document" : "documents")
    : "";
  head.append(
    element("h2", "", taskName),
    element("span", "count", itemCount + documentCount)
  );
  section.appendChild(head);

  const timeline = element("div", "timeline");
  for (const [eventIndex, event] of events.entries()) {
    const row = element("article", "event");
    row.dataset.actor = event.actor;
    row.dataset.type = event.type;
    if (event.outcome) row.dataset.outcome = event.outcome;
    row.appendChild(element("span", "dot"));

    const card = element("div", "card");
    const meta = element("div", "meta");
    meta.append(
      element("span", "type", label(event.type)),
      element("span", "", label(event.actor)),
      element("time", "", event.ts)
    );
    card.append(
      meta,
      element("p", "summary", event.summary)
    );
    addDetail(card, event);
    row.appendChild(card);
    timeline.appendChild(row);
    for (const documentItem of documents.filter(
      item => item.after === eventIndex
    )) {
      timeline.appendChild(documentRow(documentItem));
    }
  }
  for (const documentItem of documents.filter(item => item.after === null)) {
    timeline.appendChild(documentRow(documentItem));
  }
  section.appendChild(timeline);
  root.appendChild(section);
}
