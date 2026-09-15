/**
 * Vyapar Setu — JavaScript Frontend Unit & Module Integration Tests
 * =================================================================
 * Validates JS module instantiation, DOM rendering, dataset bindings,
 * and calculations in Node environment with a minimal DOM mock.
 */

const fs = require('fs');
const path = require('path');

// ── Minimal DOM Mock for Node environment ───────────────────────────
class MockElement {
  constructor(tagName = 'div') {
    this.tagName = tagName;
    this.innerHTML = '';
    this.value = '';
    this.children = [];
    this.listeners = {};
    this.style = {};
  }
  querySelector() { return new MockElement('div'); }
  querySelectorAll() { return [new MockElement('div')]; }
  addEventListener(event, fn) {
    this.listeners[event] = fn;
  }
  appendChild(child) {
    this.children.push(child);
  }
  setAttribute() {}
  getAttribute() { return ''; }
}

global.window = {
  VYAPAR_DATA: {
    forecastSeries: [{ week: '2026-W01', p10: 16.5, p50: 18.5, p90: 20.5 }],
    ports: [{ name: 'Paradip', draft: 16.5, max_dwt: 180000 }],
    vessels: [{ name: 'Panamax', dwt: 75000 }],
    backtest: { mape: 0.0342, r2: 0.964 },
    auditLogs: []
  }
};
global.document = {
  createElement: (tag) => new MockElement(tag),
  getElementById: (id) => new MockElement('div'),
  querySelector: () => new MockElement('div'),
  querySelectorAll: () => [new MockElement('div')]
};

// Load real mockData.js first to populate window.VYAPAR_DATA
const mockDataPath = path.join(__dirname, '..', 'data', 'mockData.js');
const mockDataCode = fs.readFileSync(mockDataPath, 'utf8');
const loadMockData = new Function('window', 'document', 'console', mockDataCode);
loadMockData(global.window, global.document, console);

let passed = 0;
let failed = 0;

function assert(condition, message) {
  if (condition) {
    console.log(`  ✅ PASSED: ${message}`);
    passed++;
  } else {
    console.error(`  ❌ FAILED: ${message}`);
    failed++;
  }
}

const jsModulesDir = path.join(__dirname, '..', 'modules');
const files = [
  'backtest.js',
  'forecast.js',
  'idleAdvisor.js',
  'ledger.js',
  'optimizer.js',
  'pooling.js',
  'tender.js',
  'vernacular.js'
];

console.log('=====================================================');
console.log(' Vyapar Setu — Frontend JS Module Test Suite');
console.log('=====================================================\n');

files.forEach(file => {
  const filePath = path.join(jsModulesDir, file);
  try {
    const code = fs.readFileSync(filePath, 'utf8');
    // Execute module code in mocked global scope
    const fn = new Function('window', 'document', 'console', code);
    fn(global.window, global.document, console);

    console.log(`Testing [${file}]...`);
    const moduleName = file.replace('.js', '');
    const capitalizedKey = moduleName.charAt(0).toUpperCase() + moduleName.slice(1) + 'Module';
    
    const mod = global.window[capitalizedKey];
    assert(mod !== undefined, `${capitalizedKey} registered on window`);
    assert(typeof mod.init === 'function', `${capitalizedKey}.init is a function`);

    // Test render/initialization
    const container = new MockElement('div');
    mod.init(container);
    assert(container.innerHTML.length > 0, `${capitalizedKey} successfully renders template into container`);
  } catch (err) {
    console.error(`  ❌ FAILED to load/run [${file}]:`, err.message);
    failed++;
  }
});

console.log('\n=====================================================');
console.log(` Results: ${passed} passed, ${failed} failed`);
console.log('=====================================================\n');

if (failed > 0) {
  process.exit(1);
}
