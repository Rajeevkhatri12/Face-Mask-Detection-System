const debuggingPort = process.env.CHROME_DEBUG_PORT || '9222';
const targetUrl = process.env.CAMERA_TEST_URL || 'http://127.0.0.1:5173/live';

const sleep = (milliseconds) => new Promise((resolve) => setTimeout(resolve, milliseconds));

async function getPageTarget() {
  for (let attempt = 0; attempt < 30; attempt += 1) {
    try {
      const targets = await fetch(`http://127.0.0.1:${debuggingPort}/json/list`).then((response) => response.json());
      const target = targets.find((item) => item.type === 'page' && item.url.startsWith(targetUrl));
      if (target) return target;
    } catch {
      // Chrome may still be starting.
    }
    await sleep(500);
  }
  throw new Error('Chrome debugging target did not become available.');
}

const target = await getPageTarget();
const socket = new WebSocket(target.webSocketDebuggerUrl);
const pending = new Map();
const cameraResponses = [];
let commandId = 0;

socket.addEventListener('message', (event) => {
  const message = JSON.parse(event.data);
  if (message.id && pending.has(message.id)) {
    const { resolve, reject } = pending.get(message.id);
    pending.delete(message.id);
    if (message.error) reject(new Error(message.error.message));
    else resolve(message.result);
  }

  if (
    message.method === 'Network.responseReceived' &&
    message.params.response.url.includes('/predict-camera-frame')
  ) {
    cameraResponses.push({
      status: message.params.response.status,
      url: message.params.response.url
    });
  }
});

await new Promise((resolve, reject) => {
  socket.addEventListener('open', resolve, { once: true });
  socket.addEventListener('error', reject, { once: true });
});

const send = (method, params = {}) =>
  new Promise((resolve, reject) => {
    commandId += 1;
    pending.set(commandId, { resolve, reject });
    socket.send(JSON.stringify({ id: commandId, method, params }));
  });

const evaluate = async (expression) => {
  const result = await send('Runtime.evaluate', {
    expression,
    awaitPromise: true,
    returnByValue: true
  });
  if (result.exceptionDetails) {
    throw new Error(result.exceptionDetails.text);
  }
  return result.result.value;
};

await send('Runtime.enable');
await send('Network.enable');
await sleep(1000);

await evaluate(`
  (() => {
    const button = [...document.querySelectorAll('button')]
      .find((item) => item.textContent.includes('Start Camera'));
    if (!button) throw new Error('Start Camera button not found');
    button.click();
    return true;
  })()
`);

await sleep(15000);

const state = await evaluate(`
  (() => {
    const video = document.querySelector('video');
    const text = document.body.innerText;
    return {
      status: text.split('\\n').find((line) =>
        line.includes('Detected') ||
        line.includes('Unable') ||
        line.includes('denied') ||
        line.includes('not ready')
      ) || '',
      hasStopButton: [...document.querySelectorAll('button')]
        .some((item) => item.textContent.includes('Stop Camera')),
      video: video && {
        readyState: video.readyState,
        width: video.videoWidth,
        height: video.videoHeight,
        paused: video.paused,
        hidden: video.classList.contains('hidden')
      }
    };
  })()
`);

console.log(JSON.stringify({ state, cameraResponses }, null, 2));
socket.close();

if (
  !state.hasStopButton ||
  !state.video ||
  state.video.readyState < 2 ||
  state.video.paused ||
  state.video.hidden ||
  cameraResponses.every((response) => response.status !== 200)
) {
  process.exitCode = 1;
}
