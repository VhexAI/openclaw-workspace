// AI Agent IRC Connector - irc-framework bot with OpenClaw integration
// Usage: node connect.js --server irc.libera.chat --port 6697 [--secure] [--nick Nick] [--channels #ch1,#ch2] [--relay-moltbook]

const { Client } = require('irc-framework');
const minimist = require('minimist');
const fs = require('fs');
const path = require('path');
const os = require('os');
const readline = require('readline');

const argv = minimist(process.argv.slice(2), {
  string: ['server', 'nick', 'channels', 'port'],
  boolean: ['secure', 'relay-moltbook'],
  default: {
    server: 'irc.libera.chat',
    port: '6697',
    nick: 'OpenClawBot',
    channels: '#openclaw',
    secure: false,
    'relay-moltbook': false,
  },
});

const host = argv.server;
const port = parseInt(argv.port, 10);
const nick = argv.nick;
const channels = argv.channels.split(',').map(c => c.trim());
const relayMoltbook = argv['relay-moltbook'];

// Resolve home directory properly (Node doesn't expand ~)
const credPath = path.join(os.homedir(), '.config', 'moltbook', 'credentials.json');
let moltbookKey = null;
try {
  const creds = JSON.parse(fs.readFileSync(credPath, 'utf8'));
  moltbookKey = creds.api_key;
  if (moltbookKey) {
    console.error('[✓] Moltbook creds loaded');
  }
} catch (e) {
  console.error('[!] Moltbook creds not found at ' + credPath + ', relay disabled');
}

const RECONNECT_DELAY_MS = 5000;
const MAX_RECONNECT_ATTEMPTS = 10;
let reconnectAttempts = 0;
let shuttingDown = false;

function createClient() {
  const client = new Client();

  client.connect({
    host,
    port,
    nick,
    username: nick,
    realname: 'OpenClaw AI Agent https://openclaw.ai',
    tls: argv.secure || port === 6697,
    auto_reconnect: false, // We handle reconnect ourselves
  });

  client.on('registered', () => {
    reconnectAttempts = 0;
    const info = { type: 'connected', nick, server: host, port, channels };
    console.log(JSON.stringify(info));
    channels.forEach(ch => client.join(ch));
  });

  client.on('join', (event) => {
    console.log(JSON.stringify({ type: 'joined', channel: event.channel, nick: event.nick }));
  });

  client.on('message', async (event) => {
    const log = { type: 'message', channel: event.target, nick: event.nick, msg: event.message, time: new Date().toISOString() };
    console.log(JSON.stringify(log));

    // Relay special commands to Moltbook
    if (relayMoltbook && moltbookKey && /^!(prompt|delegate|troubleshoot|feedback)\b/.test(event.message)) {
      const cmd = event.message.split(' ')[0].slice(1);
      const title = cmd + ': ' + event.nick;
      const content = event.message;
      await relayToMoltbook(title, content, event.target);
    }
  });

  client.on('privmsg', (event) => {
    // Direct messages
    if (!event.target.startsWith('#')) {
      console.log(JSON.stringify({ type: 'dm', nick: event.nick, msg: event.message, time: new Date().toISOString() }));
    }
  });

  client.on('error', (err) => {
    console.error(JSON.stringify({ type: 'error', error: err.message || String(err) }));
  });

  client.on('close', () => {
    console.log(JSON.stringify({ type: 'disconnected' }));
    if (!shuttingDown) {
      attemptReconnect();
    }
  });

  client.on('socket close', () => {
    if (!shuttingDown) {
      attemptReconnect();
    }
  });

  return client;
}

function attemptReconnect() {
  if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
    console.error(JSON.stringify({ type: 'fatal', error: 'Max reconnect attempts reached (' + MAX_RECONNECT_ATTEMPTS + ')' }));
    process.exit(1);
  }
  reconnectAttempts++;
  const delay = RECONNECT_DELAY_MS * reconnectAttempts;
  console.log(JSON.stringify({ type: 'reconnecting', attempt: reconnectAttempts, delayMs: delay }));
  setTimeout(() => {
    if (!shuttingDown) {
      activeClient = createClient();
    }
  }, delay);
}

async function relayToMoltbook(title, content, source) {
  try {
    const res = await fetch('https://moltbook.com/api/v1/posts', {
      method: 'POST',
      headers: {
        'X-API-Key': moltbookKey,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        submolt: 'openclaws',
        title,
        content: content + '\n\n_Relayed from IRC ' + source + '_',
      }),
    });
    const ok = res.ok;
    console.log(JSON.stringify({ type: 'moltbook-relay', success: ok, status: res.status }));
  } catch (e) {
    console.error(JSON.stringify({ type: 'moltbook-error', error: e.message }));
  }
}

// --- Stdin control: parse JSON commands line-by-line ---
const rl = readline.createInterface({ input: process.stdin });
rl.on('line', (line) => {
  try {
    const cmd = JSON.parse(line.trim());
    switch (cmd.action) {
      case 'say':
        activeClient.say(cmd.target || channels[0], cmd.msg);
        console.log(JSON.stringify({ type: 'sent', target: cmd.target || channels[0], msg: cmd.msg }));
        break;
      case 'join':
        if (cmd.channel) {
          activeClient.join(cmd.channel);
          console.log(JSON.stringify({ type: 'joining', channel: cmd.channel }));
        }
        break;
      case 'part':
        if (cmd.channel) {
          activeClient.part(cmd.channel, cmd.msg || 'Leaving');
          console.log(JSON.stringify({ type: 'parting', channel: cmd.channel }));
        }
        break;
      case 'quit':
        shuttingDown = true;
        activeClient.quit(cmd.msg || 'OpenClaw signing off 👁️');
        setTimeout(() => process.exit(0), 1000);
        break;
      case 'raw':
        if (cmd.data) activeClient.raw(cmd.data);
        break;
      case 'status':
        const isConnected = activeClient.connection ? activeClient.connection.connected : false;
        console.log(JSON.stringify({ type: 'status', connected: isConnected, nick, channels, reconnectAttempts }));
        break;
      default:
        console.log(JSON.stringify({ type: 'unknown-cmd', cmd }));
    }
  } catch (e) {
    // Ignore non-JSON lines
  }
});

// --- Graceful shutdown ---
function shutdown(signal) {
  console.log(JSON.stringify({ type: 'shutdown', signal }));
  shuttingDown = true;
  try {
    activeClient.quit('OpenClaw shutdown (' + signal + ')');
  } catch (e) {}
  setTimeout(() => process.exit(0), 2000);
}

process.on('SIGINT', () => shutdown('SIGINT'));
process.on('SIGTERM', () => shutdown('SIGTERM'));

// --- Start ---
let activeClient = createClient();
console.log(JSON.stringify({ type: 'ready', config: { host, port, nick, channels, relayMoltbook, secure: argv.secure || port === 6697 } }));
