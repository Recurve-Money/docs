# Recurve Docs

Static documentation for Recurve Protocol. Deployed at docs.recurvemoney.xyz.

## Stack

Plain HTML generated from a Python shell so the sidebar, header, pager, and
on-page nav stay in sync across pages. No framework, no bundler, no build
dependency beyond Python 3.

## Regenerating

Edit content in `build/pages.py`, then:

```bash
python3 build/pages.py
```

Every `.html` in the root is generated. Do not edit them by hand, they get
overwritten.

To add a page: append it to `NAV` in `build/gen.py` and add a `page(...)` call
in `build/pages.py`. The sidebar, prev/next pager, and table of contents all
derive from those two places.

## On-page nav

The table of contents is built from `h2`/`h3` tags that carry an `id`. A heading
without an id simply does not appear in it.

## Styling

`style.css` is copied from the main site so brand tokens stay identical.
`docs.css` layers the documentation layout on top. If a colour or font changes
on the site, copy `style.css` over again rather than editing it here.

## Deploy

Separate Vercel project from the main site, pointed at `docs.recurvemoney.xyz`.

```powershell
cd "D:\1проекты\recurve-docs"; vercel --prod
```

DNS is already set: CNAME `docs` to `cname.vercel-dns.com`.
