// Initialize Supabase Client immediately
if (typeof supabase !== "undefined" && window.SUPABASE_CONFIG && window.SUPABASE_CONFIG.URL !== "YOUR_SUPABASE_PROJECT_URL_HERE") {
    window.supabaseClient = supabase.createClient(
        window.SUPABASE_CONFIG.URL, 
        window.SUPABASE_CONFIG.ANON_KEY
    );
} else {
    console.warn("Supabase Config not set or supabase script not loaded! Auth functions will fail.");
}

document.addEventListener("DOMContentLoaded", () => {
    if (window.supabaseClient) {
        // Listen to auth state changes
        window.supabaseClient.auth.onAuthStateChange((event, session) => {
            updateAuthUI(session);
        });
        
        // Initial check
        window.supabaseClient.auth.getSession().then(async ({ data: { session } }) => {
            updateAuthUI(session);
            
            // Admin gate is advisory here; the real gate is RLS and the
            // admin.html console checks is_hadeeth_admin() itself.
            const path = window.location.pathname;
            if (path.includes("admin.html")) {
                if (!session) {
                    window.location.href = "login.html?redirect=admin";
                } else {
                    const { data, error } = await window.supabaseClient.rpc("is_hadeeth_admin");
                    const fallback = (window.ADMIN_EMAILS || []).includes(session.user.email);
                    const allowed = data === true || (error && fallback);
                    if (!allowed) {
                        alert("Access Denied: You do not have administrator privileges.");
                        window.location.href = "profile.html";
                    }
                }
            }
        });
    }
    
    function updateAuthUI(session) {
        const loginBtn = document.getElementById("auth-login-btn");
        const profileBtn = document.getElementById("auth-profile-btn");
        const usernameSpan = document.getElementById("auth-username");
        
        const mobLoginBtn = document.getElementById("mobile-auth-login-btn");
        const mobProfileBtn = document.getElementById("mobile-auth-profile-btn");
        const mobUsernameSpan = document.getElementById("mobile-auth-username");

        if (session && session.user) {
            const user = session.user;
            // Get best display name
            let displayName = (user.user_metadata && user.user_metadata.full_name) ? user.user_metadata.full_name : user.email.split("@")[0];
            
            if (loginBtn) loginBtn.classList.add("hidden");
            if (profileBtn) profileBtn.classList.remove("hidden");
            if (usernameSpan) usernameSpan.innerText = displayName;
            
            if (mobLoginBtn) mobLoginBtn.classList.add("hidden");
            if (mobProfileBtn) mobProfileBtn.classList.remove("hidden");
            if (mobUsernameSpan) mobUsernameSpan.innerText = displayName;
        } else {
            if (loginBtn) loginBtn.classList.remove("hidden");
            if (profileBtn) profileBtn.classList.add("hidden");
            
            if (mobLoginBtn) mobLoginBtn.classList.remove("hidden");
            if (mobProfileBtn) mobProfileBtn.classList.add("hidden");
        }
    }
});
