const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

const notifyScript = path.join('C:', 'Users', 'parth', '.agents', 'skills', 'telegram-notifier', 'scripts', 'notify.js');
const phoneText = fs.readFileSync(path.join(__dirname, 'PHONE_MESSAGE_TONIGHT.txt'), 'utf8');

// Split cleanly into the 3 parts
const rawParts = phoneText.split(/Part [123]\/3 — /).filter(p => p.trim().length > 0);

const titles = [
  "Part 1/3 — Summary and Features",
  "Part 2/3 — Verification & Scenario Results",
  "Part 3/3 — Commit & File Locations"
];

for (let i = 0; i < rawParts.length; i++) {
  const partTitle = titles[i] || `Part ${i+1}`;
  let partBody = rawParts[i].trim();
  // Strip the redundant header line if present
  partBody = partBody.replace(/^Summary and Features\s*={5,}\s*/i, '');
  partBody = partBody.replace(/^Verification & Scenario Results\s*={5,}\s*/i, '');
  partBody = partBody.replace(/^Commit & File Locations\s*={5,}\s*/i, '');

  console.log(`Sending ${partTitle}...`);
  try {
    const out = execFileSync('node', [
      notifyScript,
      '--type=task_finished',
      `--title=${partTitle}`,
      `--message=${partBody}`
    ], { encoding: 'utf8' });
    console.log(`[SUCCESS] ${partTitle}:`, out.trim());
  } catch (err) {
    console.error(`[FAIL] ${partTitle}:`, err.message);
    process.exit(1);
  }
}
console.log("ALL_PARTS_SENT_SUCCESSFULLY");
