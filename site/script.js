/**
 * stock-fetcher showcase interactivity
 * Pure Vanilla JS, zero dependencies, accessible WCAG compliant.
 */

document.addEventListener("DOMContentLoaded", () => {
  // 1. Install Tabs Logic
  const installCommands = {
    homebrew: "brew tap AtaCanYmc/tap && brew install stock-fetcher",
    pip: "pip install stock-fetcher[cli]",
    "pip-all": "pip install stock-fetcher[all]",
  };

  const installTabBtns = document.querySelectorAll(".install-tab-btn");
  const installCode = document.getElementById("install-code");
  const heroCopyBtn = document.getElementById("hero-copy-btn");

  installTabBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      installTabBtns.forEach((b) => b.setAttribute("aria-selected", "false"));
      btn.setAttribute("aria-selected", "true");
      const key = btn.getAttribute("data-tab");
      if (installCommands[key] && installCode) {
        installCode.textContent = installCommands[key];
      }
    });
  });

  // 2. Generic Clipboard Copy Handlers
  document.querySelectorAll("[data-copy-target]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const targetId = btn.getAttribute("data-copy-target");
      const el = document.getElementById(targetId);
      if (!el) return;

      const text = el.textContent || el.innerText;
      try {
        await navigator.clipboard.writeText(text.trim());
        const originalText = btn.innerHTML;
        btn.classList.add("copied");
        btn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg> Copied`;

        setTimeout(() => {
          btn.classList.remove("copied");
          btn.innerHTML = originalText;
        }, 2200);
      } catch (err) {
        console.error("Clipboard copy failed", err);
      }
    });
  });

  // 3. Interactive Terminal Simulation
  const terminalOutputs = {
    find: `[dim]# Concurrent multi-provider query (httpx + asyncio.gather)[/dim]
[bold cyan]Querying Pexels, Pixabay, Unsplash, and Flickr simultaneously...[/bold cyan]

[bold green]✓ Pixabay[/bold green] (3 results in 0.28s)
  • ID 841291  "Cyberpunk neon street Tokyo"   (1920x1080)
  • ID 941022  "Futuristic cyberpunk alley"    (2560x1440)
  • ID 731109  "Neon lights and wet pavement"  (3840x2160)

[bold green]✓ Flickr[/bold green] (3 results in 0.34s) - [dim]Zero-Config Scraper[/dim]
  • ID 408765  "Hong Kong neon skyline"        (Original CC)
  • ID 426852  "Cyberpunk street reflection"   (Original CC)
  • ID 152237  "Night cyberpunk rain passage"  (Original CC)

[bold green]✓ Pexels[/bold green] (3 results in 0.31s)
  • ID 210984  "Cyberpunk arcade corridor"     (High-Res)
  • ID 339102  "Hologram street signage"       (High-Res)

[bold magenta]Success:[/bold magenta] Retrieved 9 validated StockImage models across 3 active engines in 0.35s total.`,

    flickr: `[dim]# Zero-config Creative Commons scrape without API keys[/dim]
[bold cyan]Scraping Flickr CC media for 'alpine lake'...[/bold cyan]

┏━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┓
┃ ID         ┃ Source ┃ Title / Theme                                  ┃ License Status   ┃
┡━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━┩
│ 1391306974 │ flickr │ Alpine Lake at Sunrise (Mirror Reflection)     │ Creative Commons │
│ 2671298992 │ flickr │ Dolomite Range above Emerald Water            │ Creative Commons │
│ 2901639703 │ flickr │ Glacial Alpine Basin Mist                     │ Creative Commons │
│ 2589805804 │ flickr │ Swiss High Altitude Lake Panorama              │ Creative Commons │
└────────────┴────────┴────────────────────────────────────────────────┴──────────────────┘

[green]✓ Cached in MemoryCache (TTL: 3600s)[/green]
[dim]Saved 4 items to ./downloads/alpine_lake_*.jpg[/dim]`,

    keys: `                           Environment API Key Status
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Provider  ┃ Variable          ┃ Status                                 ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ pixabay   │ PIXABAY_API_KEY   │ [bold green]Configured (9481...e2)[/bold green]                 │
│ pexels    │ PEXELS_API_KEY    │ [bold green]Configured (56a1...8f)[/bold green]                 │
│ unsplash  │ UNSPLASH_API_KEY  │ [bold green]Configured (gh78...z1)[/bold green]                 │
│ flickr    │ -                 │ [dim]Not Required (HTML Scraper)[/dim]      │
│ wikimedia │ -                 │ [dim]Not Required (MediaWiki API)[/dim]     │
│ openverse │ OPENVERSE_API_KEY │ [green]Optional (Public Tier Active)[/green]         │
└───────────┴───────────────────┴────────────────────────────────────────┘

[dim]Audit passed: 3 API keys configured securely in shell environment.[/dim]`,

    providers: `                                Supported Providers
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Provider  ┃ Mode         ┃ Auth Required ┃ Env Variable     ┃ Status                   ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ pixabay   │ REST API     │ Yes           │ PIXABAY_API_KEY  │ [green]Ready[/green]                    │
│ pexels    │ REST API     │ Yes           │ PEXELS_API_KEY   │ [green]Ready[/green]                    │
│ unsplash  │ REST API     │ Yes           │ UNSPLASH_API_KEY │ [green]Ready[/green]                    │
│ flickr    │ HTML Scraper │ No            │ None             │ [green]Ready (No Key Required)[/green]  │
│ wikimedia │ MediaWiki    │ No            │ None             │ [green]Ready (No Key Required)[/green]  │
│ openverse │ REST API     │ Optional      │ OPENVERSE_API_KEY│ [green]Ready (Public Tier)[/green]      │
└───────────┴──────────────┴───────────────┴━━━━━━━━━━━━━━━━━━┴━━━━━━━━━━━━━━━━━━━━━━━━━━┘`,
  };

  const terminalChips = document.querySelectorAll(".terminal-chip");
  const terminalCmd = document.getElementById("terminal-cmd");
  const terminalOutput = document.getElementById("terminal-output");

  terminalChips.forEach((chip) => {
    chip.addEventListener("click", () => {
      terminalChips.forEach((c) => c.classList.remove("active"));
      chip.classList.add("active");

      const action = chip.getAttribute("data-action");
      if (terminalOutputs[action]) {
        if (action === "find") terminalCmd.textContent = "stock-fetcher find 'cyberpunk neon' --limit 3";
        else if (action === "flickr") terminalCmd.textContent = "stock-fetcher search flickr 'alpine lake' -l 4 -d";
        else if (action === "keys") terminalCmd.textContent = "stock-fetcher keys";
        else if (action === "providers") terminalCmd.textContent = "stock-fetcher providers";

        // Simple text format parsing for Rich simulation
        terminalOutput.innerHTML = terminalOutputs[action]
          .replace(/\[bold cyan\](.*?)\[\/bold cyan\]/g, '<span style="color:var(--color-accent); font-weight:700;">$1</span>')
          .replace(/\[bold green\](.*?)\[\/bold green\]/g, '<span style="color:var(--color-code-green); font-weight:700;">$1</span>')
          .replace(/\[green\](.*?)\[\/green\]/g, '<span style="color:var(--color-code-green);">$1</span>')
          .replace(/\[bold magenta\](.*?)\[\/bold magenta\]/g, '<span style="color:var(--color-code-magenta); font-weight:700;">$1</span>')
          .replace(/\[dim\](.*?)\[\/dim\]/g, '<span style="color:var(--color-text-muted);">$1</span>');
      }
    });
  });

  // 4. Code Architecture Showcase Tabs
  const codeTabBtns = document.querySelectorAll(".code-tab-btn");
  const codePanels = document.querySelectorAll(".code-panel");

  codeTabBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      codeTabBtns.forEach((b) => b.setAttribute("aria-selected", "false"));
      codePanels.forEach((p) => (p.hidden = true));

      btn.setAttribute("aria-selected", "true");
      const targetPanelId = btn.getAttribute("aria-controls");
      const targetPanel = document.getElementById(targetPanelId);
      if (targetPanel) {
        targetPanel.hidden = false;
      }
    });
  });
});
