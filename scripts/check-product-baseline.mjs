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

const requiredDocs = [
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
  if (!fs.existsSync(absolutePath)) {
    failures.push(`missing: ${relativePath}`);
    return null;
  }
  return fs.readFileSync(absolutePath, "utf8");
};

const agents = read("AGENTS.md");
if (agents) {
  for (const url of [
    "https://github.com/vicy07/Guidelines",
    "https://github.com/vicy07/AI-Governance",
  ]) {
    if (!agents.includes(url)) failures.push(`AGENTS.md missing reference: ${url}`);
  }
}

const baselineText = read(".governance/baseline.yaml");
if (baselineText) {
  let baseline;
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

for (const relativePath of requiredDocs) read(relativePath);

if (failures.length) {
  const label = strict ? "ERROR" : "GAP";
  for (const failure of failures) console.error(`${label}: ${failure}`);
  process.exit(strict ? 1 : 0);
}

console.log(`OK: ${root} adopts both governance baselines and the docs structure.`);
