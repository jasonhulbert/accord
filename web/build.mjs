import {
  cpSync,
  existsSync,
  mkdtempSync,
  readFileSync,
  readdirSync,
  rmSync,
  statSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { build } from "esbuild";

const webRoot = dirname(fileURLToPath(import.meta.url));
const repositoryRoot = dirname(webRoot);
const outputRoot = join(repositoryRoot, "plugins", "accord", "assets", "web");
const checkOnly = process.argv.includes("--check");
const mermaidVersion = "11.16.0";
const corePath = resolve(
  repositoryRoot,
  "node_modules",
  "mermaid",
  "dist",
  "mermaid.core.mjs"
);
const packagePath = resolve(
  repositoryRoot,
  "node_modules",
  "mermaid",
  "package.json"
);

function fail(message) {
  throw new Error(`web build: ${message}`);
}

if (!existsSync(corePath)) {
  fail("dependencies are missing; run npm ci");
}
const mermaidPackage = JSON.parse(readFileSync(packagePath, "utf8"));
if (mermaidPackage.version !== mermaidVersion) {
  fail(
    `expected Mermaid ${mermaidVersion}, found ${mermaidPackage.version}`
  );
}

const source = readFileSync(corePath, "utf8");
const orchestrationMarker = "// src/diagram-api/diagram-orchestration.ts";
const firstOrchestration = source.indexOf(orchestrationMarker);
if (firstOrchestration < 0) {
  fail("Mermaid diagram orchestration changed");
}

const sectionPattern = /(^\/\/ src\/[^\n]+\n)([\s\S]*?)(?=^\/\/ src\/|$(?![\s\S]))/gm;
const keptDiagramSections = new Set([
  "src/diagrams/flowchart/flowDetector-v2.ts",
  "src/diagrams/sequence/sequenceDetector.ts",
  "src/diagrams/error/errorRenderer.ts",
  "src/diagrams/error/errorDiagram.ts",
]);
let narrowed = source.replace(
  sectionPattern,
  (section, heading, _body, offset) => {
    if (
      offset >= firstOrchestration ||
      !heading.includes("src/diagrams/")
    ) {
      return section;
    }
    const path = heading.slice(3).trim();
    return keptDiagramSections.has(path) ? section : "";
  }
);

const registrationPattern =
  /  if \(true\) \{\n    registerLazyLoadedDiagrams\(detector_default2, detector_default4, architectureDetector_default\);\n  \}\n  registerLazyLoadedDiagrams\(\n[\s\S]*?\n  \);/;
const registrationMatches = narrowed.match(
  new RegExp(registrationPattern.source, "g")
);
if (registrationMatches?.length !== 1) {
  fail("Mermaid diagram registration changed");
}
narrowed = narrowed.replace(
  registrationPattern,
  "  registerLazyLoadedDiagrams(\n" +
    "    sequenceDetector_default,\n" +
    "    flowDetector_v2_default\n" +
    "  );"
);

const temporaryRoot = mkdtempSync(join(tmpdir(), "accord-web-"));
const generatedRoot = join(temporaryRoot, "web");
try {
  await build({
    entryPoints: [corePath],
    bundle: true,
    splitting: true,
    format: "esm",
    minify: true,
    treeShaking: true,
    outdir: join(generatedRoot, "mermaid"),
    entryNames: "mermaid",
    chunkNames: "chunks/[name]-[hash]",
    logLevel: "silent",
    plugins: [
      {
        name: "accord-narrow-mermaid",
        setup(buildContext) {
          buildContext.onLoad({ filter: /mermaid\.core\.mjs$/ }, () => ({
            contents: narrowed,
            loader: "js",
            resolveDir: dirname(corePath),
          }));
        },
      },
    ],
  });

  const css = readFileSync(join(webRoot, "record.css"), "utf8");
  const javascript = readFileSync(join(webRoot, "record.js"), "utf8");
  const htmlSource = readFileSync(join(webRoot, "record.html"), "utf8");
  if (
    !htmlSource.includes("<!-- ACCORD_CSS -->") ||
    !htmlSource.includes("<!-- ACCORD_JS -->")
  ) {
    fail("record.html is missing its CSS or JavaScript insertion point");
  }
  const html = htmlSource
    .replace("<!-- ACCORD_CSS -->", `<style>${css.trim()}</style>`)
    .replace(
      "<!-- ACCORD_JS -->",
      `<script type="module">${javascript.trim()}</script>`
    );
  writeFileSync(join(generatedRoot, "record.html"), html);
  cpSync(
    resolve(repositoryRoot, "node_modules", "mermaid", "LICENSE"),
    join(generatedRoot, "LICENSE.txt")
  );
  writeFileSync(
    join(generatedRoot, "README.md"),
    `# Generated Accord web view\n\n` +
      `Built from Mermaid ${mermaidVersion} with only flowchart and sequence ` +
      `diagram registration retained. Run \`npm run build:web\` from the ` +
      `repository root to regenerate these files.\n`
  );

  if (checkOnly) {
    const differences = compareTrees(generatedRoot, outputRoot);
    if (differences.length) {
      fail(`generated distribution differs: ${differences.join(", ")}`);
    }
  } else {
    rmSync(outputRoot, { recursive: true, force: true });
    cpSync(generatedRoot, outputRoot, { recursive: true });
  }
} finally {
  rmSync(temporaryRoot, { recursive: true, force: true });
}

function filesUnder(root) {
  if (!existsSync(root)) return [];
  const files = [];
  for (const entry of readdirSync(root, { withFileTypes: true })) {
    const path = join(root, entry.name);
    if (entry.isDirectory()) {
      files.push(...filesUnder(path));
    } else {
      files.push(path);
    }
  }
  return files;
}

function compareTrees(expectedRoot, actualRoot) {
  const expected = new Map(
    filesUnder(expectedRoot).map((path) => [
      relative(expectedRoot, path),
      readFileSync(path),
    ])
  );
  const actual = new Map(
    filesUnder(actualRoot).map((path) => [
      relative(actualRoot, path),
      readFileSync(path),
    ])
  );
  const names = new Set([...expected.keys(), ...actual.keys()]);
  return [...names]
    .filter((name) => {
      const left = expected.get(name);
      const right = actual.get(name);
      return !left || !right || !left.equals(right);
    })
    .sort();
}

if (!checkOnly) {
  const bytes = filesUnder(outputRoot).reduce(
    (total, path) => total + statSync(path).size,
    0
  );
  console.log(`built Accord web view (${bytes} bytes)`);
}
