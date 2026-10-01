// Small TensorFlow.js model trained in the browser on the last 7 days of hourly
// observations to predict the temperature one hour ahead.

const FEATURES = ['temperature_2m', 'relative_humidity_2m', 'surface_pressure', 'wind_speed_10m'];

function stats(rows) {
  const n = rows.length;
  return FEATURES.map((_, j) => {
    const mean = rows.reduce((s, r) => s + r[j], 0) / n;
    const sd = Math.sqrt(rows.reduce((s, r) => s + (r[j] - mean) ** 2, 0) / n) || 1;
    return { mean, sd };
  });
}

export async function predictNextHour(data) {
  const tf = await import('@tensorflow/tfjs');
  const h = data.hourly;
  const now = Date.parse(data.current.time);

  // Observed history only (hours up to now), dropping rows with missing values.
  const rows = [];
  for (let i = 0; i < h.time.length; i++) {
    if (Date.parse(h.time[i]) > now) break;
    const r = FEATURES.map((f) => h[f][i]);
    if (r.every((v) => typeof v === 'number' && Number.isFinite(v))) rows.push(r);
  }
  if (rows.length < 24) throw new Error('Not enough history to train the model');

  const s = stats(rows);
  const norm = (r) => r.map((v, j) => (v - s[j].mean) / s[j].sd);
  const xs = rows.slice(0, -1).map(norm);
  const ys = rows.slice(1).map((r) => [(r[0] - s[0].mean) / s[0].sd]);

  const model = tf.sequential();
  model.add(tf.layers.dense({ inputShape: [FEATURES.length], units: 8, activation: 'relu' }));
  model.add(tf.layers.dense({ units: 1 }));
  model.compile({ optimizer: tf.train.adam(0.03), loss: 'meanSquaredError' });

  const x = tf.tensor2d(xs);
  const y = tf.tensor2d(ys);
  const hist = await model.fit(x, y, { epochs: 80, batchSize: 32, shuffle: true, verbose: 0 });

  const c = data.current;
  const input = tf.tensor2d([norm([c.temperature_2m, c.relative_humidity_2m, c.surface_pressure, c.wind_speed_10m])]);
  const out = model.predict(input);
  const value = (await out.data())[0] * s[0].sd + s[0].mean;
  const loss = hist.history.loss.at(-1);

  tf.dispose([x, y, input, out]);
  model.dispose();

  return { temperature: value, rmse: Math.sqrt(loss) * s[0].sd, samples: xs.length };
}
