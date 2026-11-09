#!/usr/bin/env node
// Stop hook: 매 턴이 끝날 때 이 세션의 transcript를 두 군데에 남긴다.
//   1) prompt_backup/auto/raw/<session_id>.jsonl — 원본 그대로(생각 과정 포함). .gitignore로 로컬 전용.
//   2) prompt_backup/auto/<session_id>.md — 사람이 읽을 프롬프트+최종 응답만 추린 요약. git으로 공유.
//
// 5minuate_study / node_trade의 동일 hook을 Auto_BIM 경로에 맞게 옮긴 것.
// prompt_backup/ 루트는 사람이 토픽 단위로 정리하는 세션 기록용이고, 이 hook은 auto/ 아래에만 쓴다.
// 원칙(LLM_wiki/repo-conventions.md): 세션 백업 원본과 RAG용 정제 지식(LLM_wiki/)을 섞지 않는다.
const fs = require('fs');
const path = require('path');

function readStdin() {
  return new Promise((resolve) => {
    let data = '';
    process.stdin.on('data', (c) => (data += c));
    process.stdin.on('end', () => resolve(data));
  });
}

function extractText(blocks) {
  if (typeof blocks === 'string') return blocks.trim();
  return (blocks || [])
    .filter((b) => b && b.type === 'text' && typeof b.text === 'string')
    .map((b) => b.text.trim())
    .filter(Boolean)
    .join('\n\n');
}

function buildSummary(transcriptPath) {
  const lines = fs.readFileSync(transcriptPath, 'utf8').split('\n').filter(Boolean);
  const turns = [];
  for (const line of lines) {
    let entry;
    try {
      entry = JSON.parse(line);
    } catch {
      continue;
    }
    if (entry.isSidechain) continue; // 서브에이전트 대화는 메인 흐름이 아니므로 제외

    if (entry.type === 'user' && !entry.toolUseResult) {
      const text = extractText(entry.message && entry.message.content);
      if (text) turns.push({ role: 'user', text, ts: entry.timestamp });
    } else if (entry.type === 'assistant') {
      const text = extractText(entry.message && entry.message.content);
      if (text) turns.push({ role: 'assistant', text, ts: entry.timestamp });
    }
  }

  const parts = turns.map((t) => {
    const label = t.role === 'user' ? '## 사용자' : '## Claude';
    const ts = t.ts ? ` (${t.ts})` : '';
    return `${label}${ts}\n\n${t.text}`;
  });

  const header =
    `# 세션 자동 백업 (프롬프트/최종 응답만, 도구 호출·생각 과정은 제외)\n\n` +
    `전체 기록은 로컬의 \`prompt_backup/auto/raw/\` 아래 같은 세션 id 파일에 있습니다.\n\n` +
    `재사용 가치가 높은 교훈은 이 파일을 그대로 두지 말고 \`LLM_wiki/\` 또는 \`prompt_backup/<날짜>_<주제>.md\`로 승격하세요.\n\n---\n\n`;

  return header + parts.join('\n\n---\n\n') + '\n';
}

(async () => {
  try {
    const input = JSON.parse(await readStdin());
    const sessionId = input.session_id;
    const transcriptPath = input.transcript_path;
    if (!sessionId || !transcriptPath || !fs.existsSync(transcriptPath)) return;

    const root = process.env.CLAUDE_PROJECT_DIR || process.cwd();
    const summaryDir = path.join(root, 'prompt_backup', 'auto');
    const rawDir = path.join(summaryDir, 'raw');
    fs.mkdirSync(rawDir, { recursive: true });

    fs.copyFileSync(transcriptPath, path.join(rawDir, `${sessionId}.jsonl`));
    fs.writeFileSync(path.join(summaryDir, `${sessionId}.md`), buildSummary(transcriptPath), 'utf8');
  } catch {
    // 백업 실패가 세션 진행을 막으면 안 되므로 조용히 무시한다.
  }
})();
