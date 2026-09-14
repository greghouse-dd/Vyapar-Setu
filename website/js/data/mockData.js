/* =========================================================
   VYAPAR SETU — Platform Mock Data Store
   ========================================================= */

window.VYAPAR_DATA = {
  // Ports Metadata (Origins & Destination Ports across East Coast & Global Suppliers)
  PORTS: {
    INKAN: { name: 'Kandla', code: 'INKAN', lat: 23.03, lon: 70.22, draft: 14.5, maxDwt: 75000, type: 'Dest' },
    INMUN: { name: 'Mundra', code: 'INMUN', lat: 22.84, lon: 69.72, draft: 17.5, maxDwt: 150000, type: 'Dest' },
    INNSA: { name: 'Nhava Sheva (JNPT)', code: 'INNSA', lat: 18.95, lon: 72.95, draft: 15.0, maxDwt: 90000, type: 'Dest' },
    INDAH: { name: 'Dahej LNG Terminal', code: 'INDAH', lat: 21.70, lon: 72.55, draft: 15.2, maxDwt: 100000, type: 'Dest' },
    
    // Named East Coast Destination Ports in PS SIH2026006
    INPPP: { name: 'Paradip (WD-1)', code: 'INPPP', lat: 20.32, lon: 86.61, draft: 16.5, maxDwt: 180000, maxDraftTarget: 18.5, handlingRate: 25000, type: 'Dest', region: 'Odisha', lang: 'Odia' },
    INDHM: { name: 'Dhamra Port', code: 'INDHM', lat: 20.80, lon: 86.96, draft: 18.4, maxDwt: 186000, handlingRate: 30000, type: 'Dest', region: 'Odisha', lang: 'Odia' },
    INVTZ: { name: 'Visakhapatnam (Vizag)', code: 'INVTZ', lat: 17.68, lon: 83.22, draft: 16.0, maxDwt: 150000, handlingRate: 22000, type: 'Dest', region: 'Andhra Pradesh', lang: 'Telugu' },
    INGGV: { name: 'Gangavaram Port', code: 'INGGV', lat: 17.62, lon: 83.24, draft: 18.0, maxDwt: 200000, handlingRate: 35000, type: 'Dest', region: 'Andhra Pradesh', lang: 'Telugu' },
    INGPL: { name: 'Gopalpur Port', code: 'INGPL', lat: 19.30, lon: 84.96, draft: 13.0, maxDwt: 65000, handlingRate: 15000, type: 'Dest', region: 'Odisha', lang: 'Odia' },
    INHLD: { name: 'Haldia Dock Complex', code: 'INHLD', lat: 22.02, lon: 88.06, draft: 8.5, maxDwt: 45000, handlingRate: 12000, type: 'Dest', region: 'West Bengal', lang: 'Bengali' },
    INSGR: { name: 'Sagar-Sandheads Lightering', code: 'INSGR', lat: 21.60, lon: 88.10, draft: 15.5, maxDwt: 120000, handlingRate: 18000, type: 'Anchor', region: 'West Bengal', lang: 'Bengali' },

    INVAD: { name: 'Vadinar', code: 'INVAD', lat: 22.47, lon: 69.65, draft: 19.0, maxDwt: 300000, type: 'Dest' },
    INCCU: { name: 'Kolkata', code: 'INCCU', lat: 22.57, lon: 88.31, draft: 7.5, maxDwt: 35000, type: 'Dest' },

    // Named Origins in PS SIH2026006
    AUNTL: { name: 'Newcastle (Australia)', code: 'AUNTL', lat: -32.93, lon: 151.78, type: 'Origin' },
    AUHPT: { name: 'Hay Point (Australia)', code: 'AUHPT', lat: -21.27, lon: 149.30, type: 'Origin' },
    IDTAB: { name: 'Tanjung Bara (Indonesia)', code: 'IDTAB', lat: -0.52, lon: 117.57, type: 'Origin' },
    USBAL: { name: 'Baltimore (United States)', code: 'USBAL', lat: 39.29, lon: -76.61, type: 'Origin' },
    MZMAP: { name: 'Maputo (Mozambique)', code: 'MZMAP', lat: -25.96, lon: 32.57, type: 'Origin' },
    RUVOST:{ name: 'Vostochny (Russia)', code: 'RUVOST', lat: 42.74, lon: 133.08, type: 'Origin' },

    AEJEA: { name: 'Jebel Ali', code: 'AEJEA', lat: 24.99, lon: 55.06, type: 'Origin' },
    AEFJR: { name: 'Fujairah', code: 'AEFJR', lat: 25.11, lon: 56.34, type: 'Origin' },
    QAMFF: { name: 'Ras Laffan', code: 'QAMFF', lat: 25.91, lon: 51.55, type: 'Origin' },
    NLRTM: { name: 'Port of Rotterdam', code: 'NLRTM', lat: 51.92, lon: 4.48, type: 'Dest' },
    GBFXT: { name: 'Felixstowe', code: 'GBFXT', lat: 51.96, lon: 1.35, type: 'Dest' },
  },

  COMMODITIES: [
    'Basmati Rice', 'Liquefied Natural Gas', 'Iron Ore Pellets', 'Crude Oil (Brent)',
    'Assam Tea', 'Thermal Coal', 'Coking Coal (HCC)', 'Coking Coal (SSCC)', 'Cotton Yarn', 'Cardamom'
  ],

  OFFICERS: [
    'Priya Nair · Mumbai Desk', 'Arjun Mehta · Delhi Desk', 'Kavya Suresh · Chennai Desk',
    'Rohit Bhatia · Gujarat Desk', 'Ishaan Roy · Kolkata Desk', 'Meera Iyer · Vizag Desk', 'Sunil Swain · Paradip Desk'
  ],

  CONTRACTS: [
    { id: 'CNT-2026-001', title: 'Kandla Basmati Rice Export — UAE', category: 'SINGLE_SPOT',
      commodityName: 'Basmati Rice', commodityCode: 'COMM-AGR-101', quantity: 18000, unit: 'Metric Tons',
      startDate: '2026-09-02', endDate: '2026-09-20', originPortCode: 'INKAN', destPortCode: 'AEJEA',
      vesselImo: 9788452, vesselName: 'MV Konkan Prince', maxBudget: 950000000, committedSpend: 780000000,
      officer: 'Rohit Bhatia · Gujarat Desk', note: 'Buyer has asked for early delivery ahead of festival demand.' },
    { id: 'CNT-2026-002', title: 'Ras Laffan LNG Import — Dahej Terminal', category: 'SHORT_TERM',
      commodityName: 'Liquefied Natural Gas', commodityCode: 'COMM-LNG-004', quantity: 45000, unit: 'Metric Tons',
      startDate: '2026-08-10', endDate: '2026-11-10', originPortCode: 'QAMFF', destPortCode: 'INDAH',
      vesselImo: 9712344, vesselName: 'LNG Sagar Ratna', maxBudget: 6800000000, committedSpend: 6550000000,
      officer: 'Rohit Bhatia · Gujarat Desk', note: 'Spot LNG prices have firmed up this month — check before next fixture.' },
    { id: 'CNT-2026-003', title: 'Paradip Iron Ore Export Framework — Rotterdam', category: 'LONG_TERM',
      commodityName: 'Iron Ore Pellets', commodityCode: 'COMM-IRN-009', quantity: 500000, unit: 'Metric Tons',
      startDate: '2026-01-01', endDate: '2027-12-31', originPortCode: 'INPPP', destPortCode: 'NLRTM',
      vesselImo: 9634112, vesselName: 'MV Odisha Titan', maxBudget: 5400000000, committedSpend: 1850000000,
      officer: 'Meera Iyer · Vizag Desk', note: 'Quarterly fixture tracking on plan.' },
    { id: 'CNT-2026-004', title: 'Fujairah Crude Oil Import — Vadinar Refinery', category: 'SINGLE_SPOT',
      commodityName: 'Crude Oil (Brent)', commodityCode: 'COMM-OIL-001', quantity: 120000, unit: 'Metric Tons',
      startDate: '2026-09-01', endDate: '2026-09-25', originPortCode: 'AEFJR', destPortCode: 'INVAD',
      vesselImo: 9845123, vesselName: 'MT Gulf Setu', maxBudget: 4300000000, committedSpend: 4250000000,
      officer: 'Arjun Mehta · Delhi Desk', note: 'Near budget ceiling — seek sign-off for additional demurrage.' },
    { id: 'CNT-2026-005', title: 'Kolkata Assam Tea Export — Felixstowe', category: 'SHORT_TERM',
      commodityName: 'Assam Tea', commodityCode: 'COMM-AGR-045', quantity: 3200, unit: 'Metric Tons',
      startDate: '2026-07-15', endDate: '2026-10-05', originPortCode: 'INCCU', destPortCode: 'GBFXT',
      vesselImo: 9598211, vesselName: 'MV Brahmaputra Grace', maxBudget: 180000000, committedSpend: 95000000,
      officer: 'Ishaan Roy · Kolkata Desk', note: 'Second-flush teas loading ahead of schedule.' },
    { id: 'CNT-2026-006', title: 'Newcastle Coking Coal — SAIL Paradip WD-1', category: 'LONG_TERM',
      commodityName: 'Coking Coal (HCC)', commodityCode: 'COMM-COL-018', quantity: 180500, unit: 'Metric Tons',
      startDate: '2026-08-20', endDate: '2026-10-15', originPortCode: 'AUHPT', destPortCode: 'INPPP',
      vesselImo: 9912044, vesselName: 'MV Mineral Kwangyang', maxBudget: 2950000000, committedSpend: 2480000000,
      officer: 'Sunil Swain · Paradip Desk', note: 'First Capesize vessel berthed at Western Dock-1 on 6 Sept 2026 (16.5m draft).' }
  ],

  // 12-Week Forward Freight Forecasts (Prophet + XGBoost Ensemble outputs)
  FORECASTS: {
    'AUHPT_INPPP': {
      route: 'Australia (Hay Point) → Paradip',
      vesselClass: 'Capesize (180k DWT)',
      currentSpot: 14.85, // $/tonne
      historicalAvg: 16.20,
      weeks: [
        { week: 'Wk 1 (Sep 14)', p10: 13.90, p50: 14.50, p90: 15.40, spot: 14.85 },
        { week: 'Wk 2 (Sep 21)', p10: 13.70, p50: 14.30, p90: 15.60, spot: null },
        { week: 'Wk 3 (Sep 28)', p10: 13.50, p50: 14.10, p90: 15.80, spot: null },
        { week: 'Wk 4 (Oct 05)', p10: 13.80, p50: 14.60, p90: 16.20, spot: null },
        { week: 'Wk 5 (Oct 12)', p10: 14.20, p50: 15.20, p90: 17.00, spot: null },
        { week: 'Wk 6 (Oct 19)', p10: 14.90, p50: 16.10, p90: 18.10, spot: null },
        { week: 'Wk 7 (Oct 26)', p10: 15.40, p50: 16.80, p90: 19.00, spot: null },
        { week: 'Wk 8 (Nov 02)', p10: 15.80, p50: 17.40, p90: 19.80, spot: null },
        { week: 'Wk 9 (Nov 09)', p10: 15.50, p50: 17.00, p90: 19.20, spot: null },
        { week: 'Wk 10 (Nov 16)',p10: 15.00, p50: 16.40, p90: 18.50, spot: null },
        { week: 'Wk 11 (Nov 23)',p10: 14.50, p50: 15.80, p90: 17.80, spot: null },
        { week: 'Wk 12 (Nov 30)',p10: 14.10, p50: 15.30, p90: 17.20, spot: null },
      ]
    },
    'AUNTL_INVTZ': {
      route: 'Australia (Newcastle) → Visakhapatnam',
      vesselClass: 'Panamax (75k DWT)',
      currentSpot: 17.40,
      weeks: [
        { week: 'Wk 1 (Sep 14)', p10: 16.50, p50: 17.20, p90: 18.10 },
        { week: 'Wk 2 (Sep 21)', p10: 16.80, p50: 17.60, p90: 18.70 },
        { week: 'Wk 3 (Sep 28)', p10: 17.10, p50: 18.00, p90: 19.30 },
        { week: 'Wk 4 (Oct 05)', p10: 17.60, p50: 18.70, p90: 20.20 },
        { week: 'Wk 5 (Oct 12)', p10: 18.20, p50: 19.50, p90: 21.40 },
        { week: 'Wk 6 (Oct 19)', p10: 18.90, p50: 20.40, p90: 22.60 },
        { week: 'Wk 7 (Oct 26)', p10: 19.20, p50: 20.90, p90: 23.10 },
        { week: 'Wk 8 (Nov 02)', p10: 19.00, p50: 20.60, p90: 22.80 },
        { week: 'Wk 9 (Nov 09)', p10: 18.40, p50: 19.80, p90: 21.90 },
        { week: 'Wk 10 (Nov 16)',p10: 17.80, p50: 19.00, p90: 20.90 },
        { week: 'Wk 11 (Nov 23)',p10: 17.20, p50: 18.30, p90: 20.00 },
        { week: 'Wk 12 (Nov 30)',p10: 16.80, p50: 17.80, p90: 19.30 },
      ]
    }
  },

  // SHAP Feature Attribution Drivers
  SHAP_DRIVERS: [
    { feature: 'IMD Bay of Bengal Cyclone Advisory (Oct-Nov)', impact: +12.4, direction: 'pos', description: 'Monsoon withdrawal disruption increases route delay risk' },
    { feature: 'Singapore VLSFO Bunker Fuel Momentum (+8.2%)', impact: +8.1, direction: 'pos', description: 'Marine fuel price increases direct voyage cost' },
    { feature: 'China Crude Steel Output Recovery Target', impact: +6.5, direction: 'pos', description: 'Surge in Australian iron ore/coal Capesize liftings' },
    { feature: 'Paradip WD-1 Deepening (16.5m -> 18.5m Draft Clearance)', impact: -7.8, direction: 'neg', description: 'Capesize berthing feasibility reduces $/tonne freight cost' },
    { feature: 'Panama Canal Transit Restrictions Spread', impact: +3.2, direction: 'pos', description: 'Re-routing US Atlantic coal via Cape of Good Hope' }
  ],

  // Cross-PSU Pooling Preset Datasets
  PSU_DEMAND_PRESETS: {
    SAIL: [
      { id: 'LOT-SAIL-01', plant: 'Bhilai Steel Plant', port: 'Paradip', commodity: 'HCC Coking Coal', tonnage: 65000, window: '2026-10-05 to 2026-10-15', specCoke: 'Ash 9.5%, CSN 8.5' },
      { id: 'LOT-SAIL-02', plant: 'Rourkela Steel Plant', port: 'Dhamra', commodity: 'HCC Coking Coal', tonnage: 55000, window: '2026-10-08 to 2026-10-18', specCoke: 'Ash 9.2%, CSN 8.0' },
      { id: 'LOT-SAIL-03', plant: 'Bokaro Steel Plant', port: 'Haldia/Sagar', commodity: 'SSCC Coal', tonnage: 40000, window: '2026-10-20 to 2026-10-30', specCoke: 'Ash 10.0%, CSN 7.5' }
    ],
    RINL: [
      { id: 'LOT-RINL-01', plant: 'Visakhapatnam Steel Plant', port: 'Gangavaram', commodity: 'HCC Coking Coal', tonnage: 70000, window: '2026-10-06 to 2026-10-16', specCoke: 'Ash 9.4%, CSN 8.5' },
      { id: 'LOT-RINL-02', plant: 'Visakhapatnam Steel Plant', port: 'Vizag Port', commodity: 'PCI Coal', tonnage: 45000, window: '2026-10-12 to 2026-10-22', specCoke: 'Ash 11.0%, CSN 6.0' }
    ]
  },

  // Sarvam AI Vernacular Voice Samples
  SARVAM_VOICE_SAMPLES: {
    hi: {
      lang: 'Hindi',
      flag: '🇮🇳',
      audioText: 'Paradip port ke liye coking coal ka agla hafta ka freight rate kaisa rahega?',
      transcription: 'Paradip port ke liye coking coal ka agla hafta ka freight rate kaisa rahega?',
      translatedEn: 'What will be the coking coal freight rate for Paradip port next week?',
      responseHi: 'Paradip ke liye Capesize rate agle hafte $14.10 se $14.50 per tonne ke beech rehne ka anuman hai. Oct ke doosre hafte mein cyclone risk ke karan rate 12% badh sakta hai. Abhi charter fix karna sabse accha vikalp hai.',
      responseEn: 'Capesize rates to Paradip are forecasted between $14.10-$14.50/tonne next week. Rates may rise 12% by mid-October due to cyclone risk. Fixing charter now is recommended.',
      shapSummary: 'IMD Cyclone Risk (+12.4%), Bunker Price (+8.1%), Port Draft (-7.8%)'
    },
    or: {
      lang: 'Odia',
      flag: '🇮🇳',
      audioText: 'Paradip dock-1 re Capesize jahaja berthing miliba ki nahi?',
      transcription: 'Paradip dock-1 re Capesize jahaja berthing miliba ki nahi?',
      translatedEn: 'Will Capesize vessel berthing be available at Paradip dock-1?',
      responseOr: 'Haan, Paradip Western Dock-1 re 16.5m draft samarthya hetu MV Mineral Kwangyang bhalia Capesize vessel 180,000 DWT sahita berthing samphala hoichi. Wk 3 re berthing satebale miliba.',
      responseEn: 'Yes, with Western Dock-1 at 16.5m draft, Capesize vessels up to 180,000 DWT can berth at Paradip. Berthing is feasible in Wk 3.',
      shapSummary: 'Berth Draft Feasibility: Clear (16.5m), Turnaround: 2.1 Days'
    },
    te: {
      lang: 'Telugu',
      flag: '🇮🇳',
      audioText: 'Gangavaram mariyu Vizag portulaku freight rate mein ye differance undi?',
      transcription: 'Gangavaram mariyu Vizag portulaku freight rate mein ye differance undi?',
      translatedEn: 'What is the freight rate difference between Gangavaram and Vizag ports?',
      responseTe: 'Gangavaram deep draft 18.0m undatam valla Capesize vessels $14.80/tonne sadhyam autundi. Vizag Panamax limit valla $17.20/tonne padutundi. Pooling dvara $2.40/tonne aada cheyyavachu.',
      responseEn: 'Gangavaram 18.0m draft allows Capesize at $14.80/t. Vizag Panamax costs $17.20/t. Pooling via Gangavaram saves $2.40/tonne.',
      shapSummary: 'Vessel Size Advantage: Capesize vs Panamax ($2.40/t savings)'
    },
    bn: {
      lang: 'Bengali',
      flag: '🇮🇳',
      audioText: 'Haldia port e boro jahaj anar jonno Sagar Sandheads lightering koto khorch hobe?',
      transcription: 'Haldia port e boro jahaj anar jonno Sagar Sandheads lightering koto khorch hobe?',
      translatedEn: 'How much will Sagar Sandheads lightering cost for bringing large ships to Haldia port?',
      responseBn: 'Haldia river draft 8.5m hobar karone Sagar-Sandheads e lightering cost $3.50/tonne jukto hobe. Supramax direct vessel charter kora subidhajonok hobe.',
      responseEn: 'Due to Haldia river draft limit (8.5m), Sagar-Sandheads lightering adds $3.50/t. Supramax direct chartering is recommended.',
      shapSummary: 'Haldia River Draft Constraint: Lightering cost +$3.50/tonne'
    }
  },

  // 9-Model Accuracy Benchmarking Matrix (Su, Bae & Park 2025 precedent)
  BACKTEST_BENCHMARK: [
    { model: 'Prophet + XGBoost Ensemble (Vyapar Setu)', mape: '3.42%', r2: '0.964', rmse: '0.48', strategy: 'Fix/Wait/Hedge Multi-layer', status: 'Active Champion' },
    { model: 'RBF Neural Network (Su et al. 2025)', mape: '4.10%', r2: '0.932', rmse: '0.56', strategy: 'Port-congestion RBF', status: 'Academic Baseline' },
    { model: 'Standalone XGBoost Residuals', mape: '4.85%', r2: '0.915', rmse: '0.64', strategy: 'Boosted Trees', status: 'Benchmark' },
    { model: 'Random Forest Regressor', mape: '5.60%', r2: '0.880', rmse: '0.75', strategy: 'Ensemble Trees', status: 'Benchmark' },
    { model: 'Support Vector Regression (SVR)', mape: '6.20%', r2: '0.854', rmse: '0.84', strategy: 'RBF Kernel SVR', status: 'Benchmark' },
    { model: 'Multi-Layer Perceptron (MLP)', mape: '6.85%', r2: '0.820', rmse: '0.92', strategy: 'Deep Feedforward', status: 'Benchmark' },
    { model: 'Linear Regression (BDI Only)', mape: '8.40%', r2: '0.740', rmse: '1.15', strategy: 'OLS Baseline', status: 'Benchmark' },
    { model: 'Simple Moving Average (4-Wk)', mape: '10.50%', r2: '0.650', rmse: '1.42', strategy: 'Technical Baseline', status: 'Naive Baseline' },
    { model: 'Last Value Carried Forward', mape: '12.80%', r2: '0.520', rmse: '1.78', strategy: 'Naive Persistence', status: 'Naive Baseline' }
  ]
};
