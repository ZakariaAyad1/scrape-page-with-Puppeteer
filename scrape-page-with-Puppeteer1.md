
This code:

👉 Opens a browser
👉 Loads a webpage
👉 Extracts book data from DOM
👉 Sends result back to aXet.flows
👉 Closes browser safely

---

# 🔹 1. Import Puppeteer

```javascript
const puppeteer = require('puppeteer@24.10.0');
```

### 👉 What’s happening

* `require()` loads the library
* `@24.10.0` = specific version (good practice)

### 🧠 In aXet.flows

* Function node supports `require(...)`
* This loads Puppeteer into your flow runtime

---

# 🔹 2. Async wrapper

```javascript
(async () => {
```

### 👉 Why?

Puppeteer is async (everything returns promises)

So we wrap logic inside an **async function**

---

# 🔹 3. Declare browser variable

```javascript
let browser;
```

### 👉 Why outside try?

So we can access it in `finally` and close it safely

---

# 🔹 4. Try block (main logic)

```javascript
try {
```

This is your **main scraping logic**

---

# 🔹 5. Read input

```javascript
const url = msg.url || 'https://books.toscrape.com/catalogue/page-1.html';
```

### 👉 What this means

* If user passes `msg.url` → use it
* Otherwise → use default URL

### 🧠 Example

Inject node:

```javascript
msg.url = "https://example.com";
return msg;
```

---

# 🔹 6. Launch browser

```javascript
browser = await puppeteer.launch({
  headless: true
});
```

### 👉 What happens

* Starts Chromium
* `headless: true` → no UI (faster)

### 🧠 Debug tip

```javascript
headless: false
```

👉 shows browser visually

---

# 🔹 7. Create page (tab)

```javascript
const page = await browser.newPage();
```

Think:

```text
browser = Chrome
page = tab
```

---

# 🔹 8. Open URL

```javascript
await page.goto(url, {
  waitUntil: 'networkidle2',
  timeout: 60000
});
```

### 🔍 Breakdown

* `goto(url)` → loads page
* `networkidle2` → wait until page is mostly loaded
* `timeout: 60000` → max 60 seconds

### 🧠 Why important?

Without this:
👉 scraping may run before content loads

---

# 🔹 9. Wait for elements

```javascript
await page.waitForSelector('.product_pod', { timeout: 15000 });
```

### 👉 What it does

* waits until `.product_pod` exists
* prevents scraping empty page

### 🧠 Best practice

Always wait for selector before scraping

---

# 🔹 10. Extract data (MOST IMPORTANT PART)

```javascript
const books = await page.evaluate(() => {
```

---

## 🔥 KEY CONCEPT

👉 `page.evaluate()` runs **inside the browser**

Inside this block:

* ✅ `document` works
* ❌ `require()` does NOT work
* ❌ Node.js code does NOT work

---

## 🔹 Select all books

```javascript
document.querySelectorAll('.product_pod')
```

👉 Gets all book cards

---

## 🔹 Convert NodeList → Array

```javascript
Array.from(...)
```

👉 Needed because NodeList ≠ array

---

## 🔹 Loop through each book

```javascript
.map(book => {
```

---

## 🔹 Extract elements

```javascript
const a = book.querySelector('h3 a');
const price = book.querySelector('.price_color');
const rating = book.querySelector('.star-rating');
```

---

## 🔹 Extract data safely

### Title

```javascript
title: a ? a.getAttribute('title') : ''
```

👉 If element exists → get value
👉 Else → empty string

---

### Price

```javascript
price: price ? price.textContent.trim() : ''
```

👉 `.textContent` = visible text
👉 `.trim()` removes spaces

---

### Rating

```javascript
rating: rating ? rating.className.split(' ')[1] : ''
```

### 🔍 Example HTML:

```html
<p class="star-rating Three"></p>
```

### Process:

```javascript
"star-rating Three".split(' ')
→ ["star-rating", "Three"]
```

👉 rating = `"Three"`

---

### Link (IMPORTANT)

```javascript
new URL(a.getAttribute('href'), 'https://books.toscrape.com/catalogue/').href
```

### 👉 Why needed?

Because site gives **relative URL**

Example:

```text
"../../book_1/index.html"
```

👉 Converted to full URL:

```text
https://books.toscrape.com/catalogue/book_1/index.html
```

---

## 🔹 Final return

```javascript
return {
  title,
  price,
  rating,
  link
};
```

👉 Each book becomes an object

---

# 🔹 11. Return to Node-RED

```javascript
msg.payload = books;
```

### 👉 Important

* This sends scraped data into flow
* `msg.payload` is standard output field

---

# 🔹 12. Send message

```javascript
node.send(msg);
node.done();
```

### 🔥 CRITICAL (Node-RED rule)

Because this is async:

* ❌ don’t just `return msg`
* ✅ use `node.send()`

---

# 🔹 13. Error handling

```javascript
catch (err) {
  node.error(err.message, msg);
  node.done();
}
```

### 👉 What happens

* logs error in debug panel
* prevents crash

---

# 🔹 14. Always close browser

```javascript
finally {
  if (browser) {
    await browser.close();
  }
}
```

### 👉 Why critical

If you don’t:

* memory leak
* zombie Chrome processes

---

# 🔹 15. End function

```javascript
})();
return;
```

👉 Required for async Function node pattern

---

# 🚀 Full Flow Summary

```text
Inject
   ↓
Function
   ↓
Debug
```

Inside Function:

```text
Launch browser
   ↓
Open page
   ↓
Wait for DOM
   ↓
Extract data
   ↓
Send msg.payload
   ↓
Close browser
```

---

# 🧠 Key Concepts You Learned

## 1. Two environments

| Where         | What works  |
| ------------- | ----------- |
| Function node | Node.js     |
| page.evaluate | Browser DOM |

---

## 2. Async pattern (VERY important)

```javascript
node.send(msg);
node.done();
return;
```

---

## 3. Safe scraping

* wait for page
* wait for selector
* handle missing elements

---

## 4. Data flow

```javascript
msg.payload → Debug → next node
```

---

# 🔥 Common mistakes

❌ Using `document` outside `evaluate()`
❌ Forgetting `await`
❌ Using `return msg` for async
❌ Not closing browser
❌ Not waiting for selector

---

# 👍 What to try next

Now that you understand this, try:

### 1. Add pagination

Loop pages 1–5

### 2. Add stock field

```javascript
const stock = book.querySelector('.instock.availability').textContent;
```

### 3. Add screenshot

```javascript
await page.screenshot({ path: 'page.png' });
```

### 4. Convert to UI app

```text
App → Form → Function → View-action
```

---
