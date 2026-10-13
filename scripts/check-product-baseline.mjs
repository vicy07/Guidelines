#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { load } from "js-yaml";

const args = process.argv.slice(2);
const strict = args.includes("--strict");
const positional = args.filter((arg) => arg !== "--strict");
const root = path.resolve(positional[0] || ".");
const failures = [];

const productDocs = [
  "docs/requirements/mission.md",
  "docs/requirements/use-cases.md",
  "docs/requirements/user-flows.md",
  "docs/architecture.md",
  "docs/technical-architecture.md",
  "docs/architecture/code-intelligence.md",
  "docs/qa/test-strategy.md",
  "docs/sre/deployment-and-operations.md",
];

const read = (relativePath) => {
  const absolutePath = path.join(root, relativePath);
  if (!fs.existsSync(absolutePath) || !fs.statSync(absolutePath).isFile()) {
    failures.push(`missing: ${relativePath}`);
    return null;
  }
  return fs.readFileSync(absolutePath, "utf8");
};

const agents = read("AGENTS.md");
if (agents !== null) {
  for (const url of [
    "https://github.com/vicy07/Guidelines",
    "https://github.com/vicy07/AI-Governance",
  ]) {
    if (!agents.includes(url)) failures.push(`AGENTS.md missing reference: ${url}`);
  }
}

const baselineText = read(".governance/baseline.yaml");
let baseline;
if (baselineText !== null) {
  try {
    baseline = load(baselineText);
  } catch (error) {
    failures.push(`invalid .governance/baseline.yaml: ${error.message}`);
  }
  for (const key of ["guidelines", "ai_governance"]) {
    const revision = baseline?.[key]?.revision;
    if (!/^[0-9a-f]{40}$/i.test(String(revision || ""))) {
      failures.push(`${key}.revision must be a full 40-character commit SHA`);
    }
  }
}

const isRecord = (value) => value !== null && typeof value === "object" && !Array.isArray(value);
const profiles = new Set(["docs-only", "library-cli", "service-web", "critical-system"]);
const modes = new Set(["basic", "indexed"]);
let adoption = null;
if (isRecord(baseline) && Object.hasOwn(baseline, "adoption")) {
  const declared = baseline.adoption;
  if (!isRecord(declared)) {
    failures.push("adoption must be a mapping with profile, code_intelligence, owner and rationale");
  } else {
    if (!profiles.has(declared.profile)) {
      failures.push("adoption.profile must be docs-only, library-cli, service-web or critical-system");
    }
    if (!modes.has(declared.code_intelligence)) {
      failures.push("adoption.code_intelligence must be basic or indexed");
    }
    for (const key of ["owner", "rationale"]) {
      const value = declared[key];
      if (typeof value !== "string" || !value.trim() || value.trim().startsWith("REPLACE_WITH_")) {
        failures.push(`adoption.${key} must be a non-placeholder, non-empty string`);
      }
    }
    if (profiles.has(declared.profile) && modes.has(declared.code_intelligence)) {
      adoption = declared;
    }
  }
}

// Missing/invalid declarations never silently select a lighter document set.
const requiredDocs = new Set(adoption?.profile === "docs-only" ? ["README.md"] : productDocs);
if (adoption?.code_intelligence === "indexed") {
  requiredDocs.add("docs/architecture/code-intelligence.md");
  requiredDocs.add("code-intel.py");
  requiredDocs.add("code-intel/config/index.yaml");
}
for (const relativePath of requiredDocs) read(relativePath);

if (failures.length) {
  const label = strict ? "ERROR" : "GAP";
  for (const failure of failures) console.error(`${label}: ${failure}`);
  process.exit(strict ? 1 : 0);
}

const selection = adoption
  ? `${adoption.profile}/${adoption.code_intelligence}`
  : "legacy document set (no applicability profile selected)";
console.log(`OK: ${root} adopts both governance baselines and the static structure: ${selection}.`);
