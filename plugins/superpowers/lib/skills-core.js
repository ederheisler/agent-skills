// Lightweight core utilities for Superpowers plugin
// ESM module
import fs from 'fs';
import path from 'path';

// Strip leading YAML frontmatter delimited by --- ... ---
export function stripFrontmatter(text) {
  if (!text) return '';
  const lines = text.split(/\r?\n/);
  if (lines[0]?.trim() !== '---') return text;
  let endIndex = -1;
  for (let i = 1; i < lines.length; i++) {
    if (lines[i].trim() === '---') { endIndex = i; break; }
  }
  if (endIndex === -1) return text;
  return lines.slice(endIndex + 1).join('\n');
}

// Extract frontmatter (name, description) from a SKILL.md file
export function extractFrontmatter(skillFile) {
  try {
    const raw = fs.readFileSync(skillFile, 'utf8');
    const lines = raw.split(/\r?\n/);
    if (lines[0]?.trim() !== '---') return { name: null, description: null };
    let endIndex = -1;
    for (let i = 1; i < lines.length; i++) {
      if (lines[i].trim() === '---') { endIndex = i; break; }
    }
    if (endIndex === -1) return { name: null, description: null };
    const fm = lines.slice(1, endIndex).join('\n');
    const nameMatch = fm.match(/^name:\s*(.+)$/m);
    const descMatch = fm.match(/^description:\s*(.+)$/m);
    return {
      name: nameMatch ? nameMatch[1].trim() : null,
      description: descMatch ? descMatch[1].trim() : null
    };
  } catch {
    return { name: null, description: null };
  }
}

function skillDirsIn(dir) {
  try {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    return entries
      .filter((e) => e.isDirectory())
      .map((e) => path.join(dir, e.name))
      .filter((p) => fs.existsSync(path.join(p, 'SKILL.md')));
  } catch {
    return [];
  }
}

// Find all skills in a directory; returns metadata list
export function findSkillsInDir(dir, sourceType = 'superpowers', depthLimit = 1) {
  const results = [];
  const queue = [{ d: dir, depth: 0 }];
  while (queue.length) {
    const { d, depth } = queue.shift();
    if (!d || depth > depthLimit) continue;
    for (const sd of skillDirsIn(d)) {
      const skillFile = path.join(sd, 'SKILL.md');
      const { name, description } = extractFrontmatter(skillFile);
      results.push({ path: sd, sourceType, name, description });
    }
    // Explore immediate subdirectories for nested skills, but keep it bounded
    if (depth < depthLimit) {
      try {
        const children = fs.readdirSync(d, { withFileTypes: true })
          .filter((e) => e.isDirectory())
          .map((e) => path.join(d, e.name));
        for (const child of children) queue.push({ d: child, depth: depth + 1 });
      } catch { /* ignore */ }
    }
  }
  return results;
}

// Resolve a skill path considering prefixes and personal directory
export function resolveSkillPath(skillName, superpowersSkillsDir, personalSkillsDir) {
  const isSuperpowersPrefixed = skillName.startsWith('superpowers:');
  const bareName = isSuperpowersPrefixed ? skillName.replace(/^superpowers:/, '') : skillName;

  const candidates = [];
  if (!isSuperpowersPrefixed && personalSkillsDir) {
    candidates.push(path.join(personalSkillsDir, bareName));
  }
  // Superpowers skills live under the provided skills dir
  candidates.push(path.join(superpowersSkillsDir, bareName));

  for (const base of candidates) {
    const skillFile = path.join(base, 'SKILL.md');
    if (fs.existsSync(skillFile)) {
      return { skillFile, sourceType: base.startsWith(superpowersSkillsDir) ? 'superpowers' : 'personal', skillPath: bareName };
    }
  }

  // Fallback: scan directories by frontmatter name match
  const dirsToScan = [];
  if (!isSuperpowersPrefixed && personalSkillsDir) dirsToScan.push(personalSkillsDir);
  dirsToScan.push(superpowersSkillsDir);

  for (const dir of dirsToScan) {
    for (const sd of skillDirsIn(dir)) {
      const skillFile = path.join(sd, 'SKILL.md');
      const { name } = extractFrontmatter(skillFile);
      if (name === bareName) {
        return { skillFile, sourceType: dir === superpowersSkillsDir ? 'superpowers' : 'personal', skillPath: bareName };
      }
    }
  }

  return null;
}
