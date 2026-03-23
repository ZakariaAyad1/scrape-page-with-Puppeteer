const puppeteer = require('puppeteer@24.10.0');

(async () => {
  let browser;

  try {
    const url = msg.url || 'https://books.toscrape.com/catalogue/page-1.html';

    browser = await puppeteer.launch({
      headless: true
    });

    const page = await browser.newPage();

    await page.goto(url, {
      waitUntil: 'networkidle2',
      timeout: 60000
    });

    await page.waitForSelector('.product_pod', { timeout: 15000 });

    const books = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('.product_pod')).map(book => {
        const a = book.querySelector('h3 a');
        const price = book.querySelector('.price_color');
        const rating = book.querySelector('.star-rating');

        return {
          title: a ? a.getAttribute('title') : '',
          price: price ? price.textContent.trim() : '',
          rating: rating ? rating.className.split(' ')[1] : '',
          link: a
            ? new URL(a.getAttribute('href'), 'https://books.toscrape.com/catalogue/').href
            : ''
        };
      });
    });

    msg.payload = books;
    node.send(msg);
    node.done();
  } catch (err) {
    node.error(err.message, msg);
    node.done();
  } finally {
    if (browser) {
      await browser.close();
    }
  }
})();

return;
