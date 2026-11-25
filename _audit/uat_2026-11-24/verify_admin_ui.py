from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8765"

FAKE = r"""
(() => {
  const books = [
    {id:'bukhari', title_en:'Sahih al-Bukhari', title_id:'Shahih Bukhari', order_index:1},
    {id:'muslim', title_en:'Sahih Muslim', title_id:'Shahih Muslim', order_index:2}
  ];
  const overrides = [{day:'2026-11-26', book_id:'muslim', hadith_number:'7', note:'test', created_at:'2026-11-25'}];
  const runs = [{scope:'meta', status:'ok', counts:{books:28, chapters:6974}, started_at:'2026-11-25T10:00:00Z', finished_at:'2026-11-25T10:00:05Z', error:''}];
  function q(table) {
    const st = {table, head:false, count:null, filters:{}, limit:null, single:false};
    const api = {
      select(_cols, opts) { st.head = !!opts?.head; st.count = opts?.count || null; return api; },
      eq(k,v) { st.filters[k]=v; return api; },
      gte(k,v) { st.filters[k]=v; return api; },
      or() { return api; },
      order() { return api; },
      limit(n) { st.limit=n; return api; },
      maybeSingle() { st.single=true; return api; },
      single() { st.single=true; return api; },
      upsert() { return Promise.resolve({error:null}); },
      update() { return api; },
      delete() { return api; },
      then(resolve) {
        let data = [];
        if (table==='content_books') data = books;
        if (table==='content_hadiths') data = [{book_id:'bukhari',hadith_number:'8',text_ar:'arabic',text_id:'indo',text_en:'',grade:'Shahih'}];
        if (table==='hotd_overrides') data = overrides;
        if (table==='hotd_settings') data = [{auto_rotate:true}];
        if (table==='content_sync_runs') data = runs;
        if (st.single) data = data[0] || null;
        let count = null;
        if (table==='content_hadiths') count = st.filters.tier === 'sahih' ? 96000 : 118397;
        if (table==='hotd_overrides') count = 1;
        if (table==='content_books') count = 2;
        resolve({data, error:null, count});
      }
    };
    return api;
  }
  window.supabase = { createClient: () => ({
    auth: {
      getSession: async () => ({data:{session:{user:{id:'11111111-1111-1111-1111-111111111111',email:'admin@hadeeth.id',user_metadata:{full_name:'Admin'}}}}}),
      onAuthStateChange: () => ({data:{subscription:{unsubscribe(){}}}}),
      signOut: async () => ({error:null}),
      signInWithOAuth: async () => ({error:null}),
      signInWithPassword: async () => ({error:null})
    },
    rpc: async (name) => name === 'get_hotd'
      ? ({data:[{book_id:'bukhari',hadith_number:'8',source:'auto',title_id:'Shahih Bukhari'}], error:null})
      : ({data:true, error:null}),
    from: q
  }) };
})();
"""

with sync_playwright() as pw:
    browser = pw.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.route("https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2", lambda route: route.fulfill(
        status=200, content_type="application/javascript", body=FAKE))
    page.goto(f"{BASE}/admin.html", wait_until="domcontentloaded")
    page.wait_for_timeout(1800)
    print("dash:", page.locator("#dash").is_visible(), "gate:", page.locator("#gate").is_visible())
    print("books stat:", page.locator("#stat-books").inner_text())
    print("auto stat:", page.locator("#stat-auto").inner_text())
    print("source:", page.locator("#stat-overrides").inner_text())
    print("resolution:", page.locator("#today-resolution").inner_text())
    print("overrides:", page.locator("#override-list").inner_text().replace("\n"," | "))
    print("setup warning visible:", page.locator("#setup-warning").is_visible())
    page.fill("#hotd-number", "8")
    page.click("#hotd-preview")
    page.wait_for_timeout(3500)
    print("preview:", page.locator("#hotd-preview-box").inner_text().replace("\n"," | ")[:160])
    page.click("#toggle-auto")
    page.wait_for_timeout(300)
    print("toggle aria:", page.locator("#toggle-auto").get_attribute("aria-checked"))
    print("errors:", errors)
    assert errors == []
    assert page.locator("#dash").is_visible()
    browser.close()
print("PASS")
