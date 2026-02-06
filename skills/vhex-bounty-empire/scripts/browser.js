/* 
vhex-bounty-empire Browser Scanner
Run: node scripts/browser.js scan
Requires: npm i puppeteer
*/

const puppeteer = require('puppeteer');

async function scanHighBounties() {
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();
  
  await page.goto('https://immunefi.com/bounties/?maxBounty=50000&minBounty=50000');
  
  // Wait for bounties list
  await page.waitForSelector('[data-testid=\"bounty-card\"]');
  
  const bounties = await page.evaluate(() => {
    const cards = Array.from(document.querySelectorAll('[data-testid=\"bounty-card\"]'));
    return cards.map(card => {
      const title = card.querySelector('h3')?.textContent?.trim();
      const reward = card.querySelector('[data-testid=\"max-reward\"]')?.textContent?.trim();
      const link = card.querySelector('a')?.href;
      return { title, reward, link };
    }).filter(b => b.title && b.reward.includes('$'));
  });
  
  console.log('High Bounties ($50k+):', bounties.slice(0, 10));
  
  await browser.close();
  return bounties;
}

if (require.main === module) {
  scanHighBounties().catch(console.error);
}

module.exports = { scanHighBounties };