from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8765"
FAKE = r"""
(() => {
  function q(table) {
    const st = {table, head:false, single:false, filters:{}};
    const api = {
      select(_c, o) { st.head=!!o?.head; return api; },
      eq(k,v){ st.filters[k]=v; return api; },
      maybeSingle(){ st.single=true; return api; },
      single(){ st.single=true; return api; },
      order(){ return api; }, limit(){ return api; },
      upsert(){ return Promise.resolve({error:null}); },
      update(){ return api; }, delete(){ return api; },
      then(resolve) {
        let data=[];
        if (table==='profiles') data=[{display_name:'Admin', preferred_language:'id', avatar_url:null}];
        let count=null;
        if (table==='bookmarks') count=3;
        if (table==='reading_progress') count=1;
        if (st.single) data=data[0]||null;
        resolve({data,error:null,count});
      }
    };
    return api;
  }
  window.supabase = { createClient: () => ({
    auth: {
      getSession: async () => ({data:{session:{user:{id:'11111111-1111-1111-1111-111111111111',email:'admin@hadeeth.id',last_sign_in_at:'2026-11-25T10:00:00Z',user_metadata:{full_name:'Admin',avatar_url:null}}}}}),
      onAuthStateChange: () => ({data:{subscription:{unsubscribe(){}}}}),
      signOut: async () => ({error:null})
    },
    rpc: async () => ({data:true,error:null}),
    from: q
  }) };
})();
"""
with sync_playwright() as pw:
    browser = pw.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page()
    errors=[]; page.on("pageerror", lambda e: errors.append(str(e)))
    page.route("https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2", lambda r: r.fulfill(status=200, content_type="application/javascript", body=FAKE))
    page.goto(f"{BASE}/profile.html", wait_until="domcontentloaded")
    page.wait_for_timeout(1800)
    print("url:", page.url)
    print("name:", page.locator("#profile-name").inner_text())
    print("pref:", page.locator("#pref-name").input_value(), page.locator("#pref-language").input_value())
    print("counts:", page.locator("#sync-bookmarks").inner_text(), page.locator("#sync-progress").inner_text())
    print("status:", page.locator("#sync-status").inner_text())
    print("admin link visible:", page.locator("#admin-link").is_visible())
    print("errors:", errors)
    assert page.url.endswith("profile.html")
    assert page.locator("#profile-name").inner_text() == "Admin"
    assert page.locator("#sync-bookmarks").inner_text() == "3"
    assert page.locator("#admin-link").is_visible()
    assert errors == []
    browser.close()
print("PASS")
